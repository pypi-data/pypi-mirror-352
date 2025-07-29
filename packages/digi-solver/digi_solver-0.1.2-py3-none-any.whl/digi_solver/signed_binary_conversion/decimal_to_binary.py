def signedMagnitude(numd):
    outnum = ""
    str_numd = str(numd)
    absnumd = abs(int(numd))
    numb = bin(absnumd)
    bnumb = numb[2:]
    fixed = '{:0>7}'.format(bnumb)
    if str_numd.startswith("-"):
        outnum = "1" + fixed
    else:
        outnum = "0" + fixed
    print(outnum)
    return outnum

def onesComplement(numd):
    outnum = ""
    str_numd = str(numd)
    if str_numd.startswith("-"):
        numd = 256 - 1 - abs(int(numd))
    print(numd)
    absnumd = abs(int(numd))
    numb = bin(absnumd)
    bnumb = numb[2:]
    outnum = '{:0>8}'.format(bnumb)
    print(outnum)
    return outnum

def twosComplement(numd):
    outnum = ""
    str_numd = str(numd)
    if str_numd.startswith("-"):
        numd = 256 - abs(int(numd))
    print(numd)
    absnumd = abs(int(numd))
    numb = bin(absnumd)
    bnumb = numb[2:]
    outnum = '{:0>8}'.format(bnumb)
    print(outnum)
    return outnum

def excessEightbits(numd):
    outnum = ""
    biasednum = int(numd) + 128
    numb = bin(biasednum)
    bnumb = numb[2:]
    outnum = '{:0>8}'.format(bnumb)
    print(outnum)
    return outnum 