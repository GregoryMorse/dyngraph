SINGLE_MANTISSA, DOUBLE_MANTISSA, LONGDOUBLE_MANTISSA = 24, 53, 64 #one more bit than is stored
SINGLE_BITSIZE, DOUBLE_BITSIZE, LONGDOUBLE_BITSIZE = 32, 64, 80
BINARY16_MANTISSA, BINARY128_MANTISSA, BINARY256_MANTISSA = 11, 113, 237
BINARY16_BITSIZE, BINARY128_BITSIZE, BINARY256_BITSIZE = 16, 128, 256
def roundNegInf(n, d): #floor
    return n // d
def roundPosInf(n, d): #ceil
    return (n + d + -1*(d >= 0)) // d
def roundTowardsZero(n, d):
    return (n + ((d + -1*(d >=0)) if (n < 0) ^ (d < 0) else 0)) // d
def roundAwayFromZero(n, d):
    return (n + (0 if (n < 0) ^ (d < 0) else (d + -1*(d >= 0)))) // d
def roundNearestPosInf(n, d):
    #return (((n << 1) // d) + 1) >> 1
    #return (((n * 2) // d) + 1) // 2
    q, r = divmod(n, d)
    return q + (2 * r <= d if d < 0 else 2 * r >= d)
def roundNearestNegInf(n, d):
    q, r = divmod(n, d)
    return q + (2 * r < d if d < 0 else 2 * r > d)
def roundNearestEven(n, d): #round only when for positive numbers guard, round, sticky are 11X or 1X1
    q, r = divmod(n, d)
    return q + (q & 1) * (2 * r == d) + ((2 * r < d) if d < 0 else (2 * r > d))
def roundNearestToZero(n, d):
    q, r = divmod(n, d)
    return q + (q < 0) * (2 * r == d) + ((2 * r < d) if d < 0 else (2 * r > d))
def roundNearestAwayZero(n, d):
    q, r = divmod(n, d)
    return q + (q >= 0) * (2 * r == d) + ((2 * r < d) if d < 0 else (2 * r > d))
def testRounding():
    pairs = ((1, 2), (-1, 2), (1, -2), (-1, -2), (3, 2), (-3, 2), (3, -2), (-3, -2),
             (1, 3), (-1, 3), (1, -3), (-1, -3), (2, 3), (-2, 3), (2, -3), (-2, -3))
    funcs = (roundNegInf, roundPosInf, roundTowardsZero, roundAwayFromZero,
             roundNearestPosInf, roundNearestNegInf,
             roundNearestToZero, roundNearestAwayZero, roundNearestEven)
    res = [[f(*p) for p in pairs] for f in funcs]
    expected = [[0, -1, -1, 0, 1, -2, -2, 1, 0, -1, -1, 0, 0, -1, -1, 0],
                   [1, 0, 0, 1, 2, -1, -1, 2, 1, 0, 0, 1, 1, 0, 0, 1],
                   [0, 0, 0, 0, 1, -1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                   [1, -1, -1, 1, 2, -2, -2, 2, 1, -1, -1, 1, 1, -1, -1, 1],
                   [1, 0, 0, 1, 2, -1, -1, 2, 0, 0, 0, 0, 1, -1, -1, 1],
                   [0, -1, -1, 0, 1, -2, -2, 1, 0, 0, 0, 0, 1, -1, -1, 1],
                   [0, 0, 0, 0, 1, -1, -1, 1, 0, 0, 0, 0, 1, -1, -1, 1],
                   [1, -1, -1, 1, 2, -2, -2, 2, 0, 0, 0, 0, 1, -1, -1, 1],
                   [0, 0, 0, 0, 2, -2, -2, 2, 0, 0, 0, 0, 1, -1, -1, 1]
                   ]
    assert(all([x == y for x, y in zip(res, expected)]))
#testRounding()
def floatToInt(f):
    import struct
    return struct.unpack('<L', struct.pack('<f', f))[0]
def doubleToInt(f):
    import struct
    return struct.unpack('<Q', struct.pack('<d', f))[0]
def intToFloat(v):
    import struct
    return struct.unpack('<f', struct.pack('<L', v))[0]
def intToDouble(v):
    import struct
    return struct.unpack('<d', struct.pack('<Q', v))[0]

def extractMantissa(num, mantSize):
    return num & ((1<<(mantSize-1))-1)
def extractExponent(num, mantSize, bitSize):
    return (num >> (mantSize-1)) & ((1 << (bitSize - mantSize))-1)
def trailing1mask(num):
    return (~num + 1) | num
def trailing1detect(num):
    return (~num + 1) & num
def reverseBits(num, size):
    r = num & 1; size -= 1; num >>= 1
    while num != 0:
        r <<= 1; r |= num & 1
        num >>= 1; size -= 1
    r <<= size
    return r
def leading1detect(num, size):
    return reverseBits(trailing1detect(reverseBits(num, size)), size)
def oneHotDecode(val):
    r = 0; val >>= 1
    while val > 0:
        r += 1; val >>= 1
    return r
def floatAddSub(num1, num2, mantSize, bitSize, isSub=False):
    #initialization: splice apart mantissa, exponent and sign
    mant1, mant2 = (1<<(mantSize-1)) | extractMantissa(num1, mantSize), (1<<(mantSize-1)) | extractMantissa(num2, mantSize)
    exp1, exp2 = extractExponent(num1, mantSize, bitSize), extractExponent(num2, mantSize, bitSize)
    sign1, sign2 = num1 >> (bitSize-1), num2 >> (bitSize-1)

    #pipeline stage 1: comparison, sign parity and final sign
    swap = (num1 & ((1<<(bitSize-1))-1)) < (num2 & ((1<<(bitSize-1))-1))
    signParity = sign1 ^ sign2 ^ isSub #sign1 == sign2 if isSub else sign1 != sign2
    
    #pipeline stage 2: swapping and exponent difference, zero, inf/NaN detection
    sign = (not sign2 if isSub else sign2) if swap else sign1
    mant1, mant2 = mant2 if swap else mant1, mant1 if swap else mant2
    expDiff = (exp1 ^ (-1 if swap else 0)) - (exp2 ^ (-1 if swap else 0))
    expZero1, expZero2 = exp1 == 0, exp2 == 0
    expInf1, expInf2 = exp1 == (1<<(bitSize-mantSize))-1, exp2 == (1<<(bitSize-mantSize))-1
    exp = exp2 if swap else exp1

    #pipeline stage 3: add guard, round bits, shifting smaller argument right, compression for "sticky" bit
    stickymask = 0 if expDiff <= 1 else ((1<<expDiff)>>2)-1
    #stickymask &= (1<<(mantSize-1))-1
    mant1 <<= 3 #pad with guard, round and for larger argument the zero sticky bit
    shifted = (mant2<<2) >> expDiff
    zeroMant = expZero1 or expZero2 or expDiff > mantSize+1 or expInf1 or expInf2
    nearOverflow = exp==(1<<(bitSize-mantSize))-2

    #pipeline stage 4: handling zero mantissa, computing sticky bit
    sticky = (mant2 & stickymask) != 0
    mant2 = 0 if zeroMant else shifted
    mant2 = (mant2 << 1) | (1 if sticky else 0)

    #pipeline stage 5: conditional addition/subtraction
    resultMant = mant1 + (-mant2 if signParity else mant2)

    #pipeline stage 6: check zero result, count of leading zeros
    isZero = resultMant == 0
    expAdjust = oneHotDecode(trailing1detect(reverseBits(resultMant>>2, mantSize+1+1)))
    
    #pipeline stage 7: shift left, underflow detect
    resultMant = resultMant << expAdjust
    underflow = expAdjust > exp

    #pipeline stage 8: rounding
    resultMant = roundNearestEven(resultMant, 16)

    #pipeline stage 9: exponent adjust and mantissa NaN marking
    roundOverflow = resultMant >> mantSize #if expAdjust == 1 or expAdjust == 2 else 0
    resultMant &= (1<<(mantSize-1))-1
    isNaN = (isZero or signParity) and expInf1 and expInf2
    resultMant |= 1<<(mantSize-2) if isNaN else 0
    resultMant = 0 if underflow or nearOverflow and (roundOverflow!=0 or expAdjust==0) else resultMant
    exp = 0 if isZero and not expInf1 and not expInf2 or underflow else exp + ((roundOverflow<<1)+(not roundOverflow)) - expAdjust

    #finalization: recombine mantissa, exponent and sign
    result = resultMant | (exp << (mantSize-1))
    result |= (1 if sign else 0) << (bitSize-1)
    return result
def floatMul(num1, num2, mantSize, bitSize):
    #initialization: splice apart mantissa, exponent and sign
    mant1, mant2 = (1<<(mantSize-1)) | extractMantissa(num1, mantSize), (1<<(mantSize-1)) | extractMantissa(num2, mantSize)
    exp1, exp2 = extractExponent(num1, mantSize, bitSize), extractExponent(num2, mantSize, bitSize)
    sign1, sign2 = num1 >> (bitSize-1), num2 >> (bitSize-1)
    adjustExp = (1 << (bitSize-mantSize-1)) - 1

    #multi-cycle pipeline stage 1: zero, inf/NaN detection, final sign, multiply, detect explicit NaN, simple underflow, overflow
    resultMant = mant1 * mant2 #at minimum 3 cycles for DSPs
    #pipeline stage 1A:
    expInf1, expInf2 = exp1 == (1<<(bitSize-mantSize))-1, exp2 == (1<<(bitSize-mantSize))-1
    isZero = exp1 == 0 or exp2 == 0
    sign = sign1 ^ sign2
    expNormal = exp1 + exp2 - adjustExp
    mant1nz, mant2nz = mant1!=(1<<(mantSize-1)), mant2!=(1<<(mantSize-1))
    #pipeline stage 1B:
    isNaN = isZero and (expInf1 or expInf2) or mant1nz and expInf1 or mant2nz and expInf2
    underflow = isZero or expNormal < 0
    nearUnderflow = expNormal == 0
    overflow = expInf1 or expInf2 or expNormal>=((1<<(bitSize-mantSize))-1)
    nearOverflow = expNormal==((1<<(bitSize-mantSize))-2)
    #pipeline stage 1C:
    expUpdate = (1<<(bitSize-mantSize))-1 if overflow else (0 if underflow else expNormal)
    flowCond = underflow or overflow

    #pipeline stage 2: check result size, including boundary overflow and underflow, shift left by zero/one or set zero/NaN, calculate sticky
    incExp = (resultMant >> (mantSize*2 - 1)) != 0
    roundOverflow = resultMant>>(mantSize-2)==((((1<<mantSize)-1)<<1) | (not nearUnderflow))
    sticky = resultMant & ((1<<(mantSize-1))-1) != (not incExp)
    if flowCond or nearUnderflow and not incExp or nearOverflow and incExp: mult = 1<<(mantSize-1) if isNaN else 0 #or nearOverflow and incExp
    elif not incExp: mult = resultMant >> (mantSize-2) #resultMant << 1
    else: mult = resultMant >> (mantSize-1) #resultMant
    incExp = incExp and not flowCond

    #pipeline stage 3: rounding, final exponent computation
    mult = roundNearestEven((mult<<1) | sticky, 4) & ((1<<(mantSize-1))-1) #1<<mantSize
    #roundOverflow |= mult >> mantSize #incExp == False
    newExp = expUpdate + incExp + roundOverflow

    #finalization: recombine mantissa, exponent and sign
    result = mult | (newExp << (mantSize - 1))
    result |= (1 if sign else 0) << (bitSize-1)
    return result
    
def randFloat(mantSize, bitSize):
    import math, random
    return math.ldexp(random.random(), 1+random.randint(-(1<<((bitSize-mantSize)-1))+2, (1<<((bitSize-mantSize)-1))-1))
def cmpFloat(a, b, bias):
    import math
    if (a == 0.0 or isSubnormal(a, bias)) and (b == 0.0 or isSubnormal(b, bias)): return True
    if math.isnan(a) and math.isnan(b): return True
    return a == b
def removeSubnormal(a, bias):
    import math
    return math.copysign(0.0, a) if isSubnormal(a, bias) else a
def isSubnormal(a, bias):
    import math
    return math.isfinite(a) and math.frexp(a)[1] <= -bias+1
def testAddition(mantSize, bitSize):    
    import math
    #print(hex(floatAddSub(0x3c98000000000000, 0x3ff0000000000000, mantSize, bitSize, True))); assert False
    #print(hex(floatAddSub(0x3ff0000000000000, 0x3c90000000000000, mantSize, bitSize, True))); assert False
    bias = (1<<(bitSize-mantSize))//2-1
    boundarycases = (
        0.0, -0.0, 1.0, -1.0, 2.0, -2.0, #addition/Subtraction Idempotency, Addition/Subtraction Identity, additive inverse, associativity
        ((1<<(mantSize-1))+1)/(1<<(mantSize-1)), #rounding, the most complex is round-to-nearest-even - odd value then even value already covered (1.0), then 4 various round/sticky combinations
        *(i/(1<<(mantSize+2)) for i in range(1, 8)), #0<<(mantSize+1) already covered (0.0), even are for addition, odd for the guard bit in subtraction cases
        *((((1<<mantSize)-1) - ((1<<i)-1))/(1<<mantSize) for i in range(53)), #subtraction
        *(-(((1<<mantSize)-1) - ((1<<i)-1))/(1<<mantSize) for i in range(53)),
        *(((1<<mantSize)-1)/(1<<(mantSize+bias-2-i)) for i in range(1, 53+1)), #underflow
        *(-((1<<mantSize)-1)/(1<<(mantSize+bias-2-i)) for i in range(1, 53+1)),
        *((((1<<mantSize)-1) - ((1<<i)-1))/(1<<(mantSize+bias-2)) for i in range(53)),
        *(-(((1<<mantSize)-1) - ((1<<i)-1))/(1<<(mantSize+bias-2)) for i in range(53)),
        *(float((1<<mantSize)-1)*(1<<(bias-mantSize+1-i)) for i in range(1,53+1)), #overflow
        *(-float((1<<mantSize)-1)*(1<<(bias-mantSize+1-i)) for i in range(1,53+1)),
        *(float(((1<<mantSize)-1) - ((1<<i)-1))*(1<<(bias-mantSize+1)) for i in range(53)),
        *(-float(((1<<mantSize)-1) - ((1<<i)-1))*(1<<(bias-mantSize+1)) for i in range(53)),
        float('inf'), float('-inf'), float('nan'), float('-nan') #special values
    ) 
    for a in boundarycases:
        for b in boundarycases:
            add, sub, revsub, mul = a + b, a - b, b - a, a * b
            addres = floatAddSub(doubleToInt(a), doubleToInt(b), mantSize, bitSize)
            subres = floatAddSub(doubleToInt(a), doubleToInt(b), mantSize, bitSize, True)
            revsubres = floatAddSub(doubleToInt(b), doubleToInt(a), mantSize, bitSize, True)
            mulres = floatMul(doubleToInt(a), doubleToInt(b), mantSize, bitSize)
            #print(hex(doubleToInt(a)), hex(doubleToInt(b)), a, b)
            if not cmpFloat(intToDouble(addres), add, bias): print(hex(addres), hex(doubleToInt(add)), a, b, hex(doubleToInt(a)), hex(doubleToInt(b)), '+')
            if not cmpFloat(intToDouble(subres), sub, bias): print(hex(subres), hex(doubleToInt(sub)), a, b, hex(doubleToInt(a)), hex(doubleToInt(b)), '-')
            if not cmpFloat(intToDouble(revsubres), revsub, bias): print(hex(revsubres), hex(doubleToInt(revsub)), a, b, hex(doubleToInt(a)), hex(doubleToInt(b)), '--')
            if not cmpFloat(intToDouble(mulres), mul, bias): print(hex(mulres), hex(doubleToInt(mul)), a, b, hex(doubleToInt(a)), hex(doubleToInt(b)), '*')
    while True:
        a, b = randFloat(mantSize, bitSize), randFloat(mantSize, bitSize)
        a, b, = removeSubnormal(a, bias), removeSubnormal(b, bias)
        add, sub, revsub, mul = a + b, a - b, b - a, a * b
        addres = floatAddSub(doubleToInt(a), doubleToInt(b), mantSize, bitSize)
        subres = floatAddSub(doubleToInt(a), doubleToInt(b), mantSize, bitSize, True)
        revsubres = floatAddSub(doubleToInt(b), doubleToInt(a), mantSize, bitSize, True)
        mulres = floatMul(doubleToInt(a), doubleToInt(b), mantSize, bitSize)
        #print(hex(doubleToInt(a)), hex(doubleToInt(b)), a, b)
        if not cmpFloat(intToDouble(addres), add, bias): print(hex(addres), hex(doubleToInt(add)), a, b, hex(doubleToInt(a)), hex(doubleToInt(b)), '+')
        if not cmpFloat(intToDouble(subres), sub, bias): print(hex(subres), hex(doubleToInt(sub)), a, b, hex(doubleToInt(a)), hex(doubleToInt(b)), '-')
        if not cmpFloat(intToDouble(revsubres), revsub, bias): print(hex(revsubres), hex(doubleToInt(revsub)), hex(doubleToInt(a)), hex(doubleToInt(b)), a, b, '--')
        if not cmpFloat(intToDouble(mulres), mul, bias): print(hex(mulres), hex(doubleToInt(mul)), a, b, hex(doubleToInt(a)), hex(doubleToInt(b)), '*')
    f = math.ldexp(((1<<mantSize)-1)/(1<<mantSize), 0)
    print(f, hex(doubleToInt(f)))

    #Boundary Value Analysis for zero
    assert 0.0 + 0.0 == 0.0 #Addition Idempotency
    assert 0.0 - 0.0 == 0.0 #Subtraction Idempotency
    assert f + 0.0 == f #Addition Identity
    assert 0.0 + f == f #former with Associativity
    assert f - 0.0 == f #Subtraction Identity
    assert 0.0 - f == -f #former with Associativity
    assert f - f == 0.0 #additive inverse

    #Addition/subtraction cases with same exponent, or change of exponent by +/- 1

    #Subtraction exponent reduction cases
    for i in range(mantSize):
        assert f - math.ldexp(((1<<mantSize)-1 - (1<<i)-1)/(1<<mantSize), i) == math.ldexp((1<<(mantSize-i))-1, i)

    #All 8 round to nearest even cases

    #can extend to +/-Inf, NaN, sub-normals to cover the full standard

#testAddition(SINGLE_MANTISSA, SINGLE_BITSIZE)
testAddition(DOUBLE_MANTISSA, DOUBLE_BITSIZE)
testAddition(LONGDOUBLE_MANTISSA, LONGDOUBLE_BITSIZE)