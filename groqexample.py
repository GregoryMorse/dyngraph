import sys
MANT_DIG = sys.float_info.mant_dig
import numpy as np
import groq.api as g
import groq.api.instruction as inst
import groq.tensor as tensor

def extract_int8(var):
    return g.concat_vectors([x.reinterpret(g.int8).split_vectors([1]*4)[0] for x in var], (len(var), var[0].shape[1]))
WEST, EAST = 0, 1
def get_slice4(drctn, start, end, bank=0):
    return "-1, H1(" + ("W" if drctn==WEST else "E") + "), S4(" + str(start) + "-" + str(end) + "), B1(" + str(bank) + ")"
def get_slice1(drctn, start, bank=0):
    return "-1, H1(" + ("W" if drctn==WEST else "E") + "), S1(" + str(start) + "), B1(" + str(bank) + ")"
s16rangeW = list(range(25, 27+1))+list(range(29, 37+1))+list(range(39,42+1))
s16rangeE = list(range(26, 27+1))+list(range(29,42+1))
def flatten_zip(z): return [item for sublist in z for item in sublist]
def flatten_unzip(z, interleave=2): return list(zip(*zip(*([iter(z)] * interleave))))
class DiagonalExtractor(g.Component):
    def __init__(self, chunks, dim, **kwargs):
        super().__init__(**kwargs)
        self.chunks, self.dim = chunks, dim      
        self.identmat, self.allones = [], []
        for hemi in (WEST, EAST):
            self.identmat.append(g.from_data(np.kron(np.eye(2, dtype=np.int8),
                np.hstack((np.tile(np.eye(dim, dtype=np.int8), (2, 1)), np.zeros((dim*2, dim), dtype=np.int8)))),
                layout=get_slice4(hemi, 0, 3, 0)))
            self.allones.append(g.ones((1,320), dtype=g.int8, layout=get_slice1(hemi, 43, 0)))
    def build(self, tmat):
        tmatsplit = g.split_vectors(tmat, [self.chunks*self.dim*2*self.dim*2*2//320]*2)
        with g.ResourceScope(name="identmask", is_buffered=True, time=0) as pred:
            result = []
            for hemi in (WEST, EAST):
                staggered_s16 = tensor.create_storage_request(
                    storage=tensor.Storage(address_tensor=
                        np.roll(inst.malloc(hemis=["W" if hemi==WEST else "E"],
                                slices=s16rangeW if hemi==WEST else s16rangeE, banks=[0],
                                count=self.chunks*self.dim*2*self.dim*2*2//320//16,
                                reserve_key="REV_W" if hemi == WEST else "REV_E"),
                            8, axis=1).transpose(0,2,3,1).flatten()))
                result_mt = g.mask(
                    g.concat_vectors(flatten_zip(flatten_unzip(g.split_vectors(
                        g.concat_vectors([self.identmat[hemi]] * (self.chunks//2), (self.dim*self.chunks*2, 320)),
                        [1]*(self.chunks*self.dim*2)), 16)), (self.chunks*self.dim*2, 320)
                    ).read(streams=g.SG4[1 if hemi==WEST else 4]),
                    g.concat_vectors(flatten_zip(flatten_unzip(g.split_vectors(tmatsplit[hemi],
                        [1]*(self.chunks*self.dim*2)), 16)), (self.chunks*self.dim*2, 320)
                    ).read(streams=g.SG4[2 if hemi==WEST else 5], time=0),
                    alus=[0 if hemi==WEST else 7], output_streams=g.SG4[2 if hemi==WEST else 5])
                result_mt = g.concat_vectors(flatten_zip(flatten_unzip(g.split_vectors(result_mt,
                    [1]*(self.chunks*self.dim*2)), self.chunks*self.dim*2//16)), (self.chunks*self.dim*2, 320))
                result.append(result_mt.write(storage_req=staggered_s16))
        g.add_mem_constraints(tmatsplit, result, g.MemConstraintType.NOT_MUTUALLY_EXCLUSIVE)
        with g.ResourceScope(name="extract", is_buffered=True, time=None, predecessors=[pred]) as pred:
            for hemi in (WEST, EAST):
                result_mt = result[hemi].read(streams=g.SG16)
                mxm_rq = tensor.create_mxm_request(planes=[hemi*2+0], num_planes=1)
                result_mt = g.split_vectors(result_mt, [self.dim*2*2] * (self.chunks//2))
                for i in range(self.chunks//2):
                    with g.ResourceScope(name="matmulextract" + str(i), is_buffered=False, time=10+i*30):
                        iw = g.install_weights(result_mt[i], planes=mxm_rq, time=0)
                        result_mt[i] = extract_int8([self.allones[hemi].matmul(
                            iw, planes=mxm_rq, num_planes=1, accum_input=None, time=0)])
                result[hemi] = g.concat_vectors(result_mt, (self.chunks//2,self.dim*2*2)
                    ).write(name="origvec" + str(hemi), layout=get_slice1(hemi, 43, 1))
        g.add_mem_constraints(result, self.allones, g.MemConstraintType.NOT_MUTUALLY_EXCLUSIVE)
        result = g.concat_vectors(result, (self.chunks, self.dim*2*2))
        return result
