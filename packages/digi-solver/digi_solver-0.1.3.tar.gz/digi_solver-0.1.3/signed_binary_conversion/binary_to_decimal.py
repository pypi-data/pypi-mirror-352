def signedMagnitude_re(numb):
    result = ""
    if numb[0] == "0":
        result = str(int(numb, 2))
    elif numb[0] == "1":
        result = "-" + str(int(numb[1:], 2))
    return result

def onesComplement_re(numb):
    result = ""
    if numb[0] == "0":
        result = str(int(numb, 2))
    elif numb[0] == "1":
        numd = 256 - 1 - int(numb, 2)
        result = "-" + str(numd)
    return result

def twosComplement_re(numb):
    result = ""
    if numb[0] == "0":
        result = str(int(numb, 2))
    elif numb[0] == "1":
        numd = 256 - int(numb, 2)
        result = "-" + str(numd)
    return result

def excessEightbits_re(numb):
    numd = int(numb, 2)
    result = str(numd - 128)
    return result 