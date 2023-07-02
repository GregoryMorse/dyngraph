import random

EXIT, LOOP, FORWARD = 0, 1, 2
def test_irreducible():
    ilt = (irreducible_loops_no_goto,
        irreducible_loops)
    def doinc(z): z[0] += 1
    for i in range(2):
        u, v, w, x = [0], [0], [0], [0]
        random.seed(5)
        ilt[i](random.randint(0, 1) == 1, lambda: random.randint(0, 2),
            lambda: random.randint(0, 2), lambda: doinc(u),
            lambda: doinc(v), lambda: doinc(w), lambda: doinc(x))
        print(u, v, w, x)

def irreducible_loops_no_goto(u_start,
    w_cond, x_cond, u, v, w, x):
    is_end, v_first = [False], not u_start
    def doExit(): is_end[0], loop[0] = True, True
    def doLoop(): loop[0] = True
    def doForward(): pass
    while True:
        if not v_first: u()
        while True:
            if not v_first:
                w()
                loop = [False]
                [doExit, doLoop, doForward][w_cond()]()
                if loop[0]: break
            while True:
                if not v_first:
                    x()
                    loop = [False]
                    [doExit, doLoop, doForward][x_cond()]()
                    if loop[0]: break
                v()
                v_first = False
            if is_end[0]: break
        if is_end[0]: break

JUMP, CONDJUMP, JUMPTABLE, CALLLAMBDA = 0, 1, 2, 3 #opcodes
def irreducible_loops(u_start,
    w_cond, x_cond, u, v, w, x):
    do_u, do_w, do_x, do_v, end = 1, 2, 4, 6, 8
    code = [(CONDJUMP, not u_start, do_v), #0
            (CALLLAMBDA, u), #1=do_u
            (CALLLAMBDA, w), #2=do_w
            (JUMPTABLE, w_cond, [end, do_u, do_x]), #3
            (CALLLAMBDA, x), #4=do_x
            (JUMPTABLE, x_cond, [end, do_w, do_v]), #5
            (CALLLAMBDA, v), #6 = do_v
            (JUMP, do_x)] #7, end is 8
    instptr = 0
    while True:
      if code[instptr][0] == JUMP:
        instptr = code[instptr][1]
      elif code[instptr][0] == CONDJUMP:
        if code[instptr][1]:
          instptr = code[instptr][2]
        else: instptr += 1
      elif code[instptr][0] == JUMPTABLE:
        instptr = code[instptr][2][code[instptr][1]()]
      elif code[instptr][0] == CALLLAMBDA:
        code[instptr][1]()
        instptr += 1
      else: assert False
      if instptr >= len(code): break

test_irreducible()