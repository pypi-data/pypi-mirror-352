def signedMagnitude(numd_str, bit_length=8):
    outnum = ""
    try:
        numd = int(numd_str)
    except ValueError:
        return "Error: Invalid decimal input"

    abs_numd = abs(numd)
    # Max value for magnitude part is 2^(bit_length-1) - 1
    max_magnitude = (1 << (bit_length - 1)) - 1 

    if abs_numd > max_magnitude:
        return f"Overflow: Cannot represent {numd} in {bit_length}-bit signed magnitude."

    bnumb = bin(abs_numd)[2:]
    # Pad magnitude to bit_length - 1 bits
    magnitude_part = bnumb.zfill(bit_length - 1)

    if len(magnitude_part) > bit_length -1: # Should be caught by overflow check, but as safeguard
        return f"Error: Magnitude {bnumb} too large for {bit_length-1} bits"

    if numd < 0:
        outnum = "1" + magnitude_part
    else:
        outnum = "0" + magnitude_part
    return outnum

def onesComplement(numd_str, bit_length=8):
    try:
        numd = int(numd_str)
    except ValueError:
        return "Error: Invalid decimal input"

    # Max positive value is 2^(bit_length-1) - 1
    # Min negative value is -(2^(bit_length-1) - 1)
    max_val = (1 << (bit_length - 1)) - 1
    min_val = -max_val

    if not (min_val <= numd <= max_val):
         return f"Overflow: {numd} cannot be represented in {bit_length}-bit one's complement."

    if numd >= 0:
        bnumb = bin(numd)[2:]
        return bnumb.zfill(bit_length)
    else: # numd < 0
        # For negative numbers, find 1's complement of the absolute value, then flip bits
        # Or, (2^bit_length - 1) - abs(numd)
        positive_equivalent_val = ( (1 << bit_length) - 1 ) - abs(numd)
        bnumb = bin(positive_equivalent_val)[2:]
        return bnumb.zfill(bit_length)

def twosComplement(numd_str, bit_length=8):
    try:
        numd = int(numd_str)
    except ValueError:
        return "Error: Invalid decimal input"

    # Max positive value is 2^(bit_length-1) - 1
    # Min negative value is -2^(bit_length-1)
    max_val = (1 << (bit_length - 1)) - 1
    min_val = -(1 << (bit_length - 1))

    if not (min_val <= numd <= max_val):
        return f"Overflow: {numd} cannot be represented in {bit_length}-bit two's complement."

    if numd >= 0:
        bnumb = bin(numd)[2:]
        return bnumb.zfill(bit_length)
    else: # numd < 0
        # For negative numbers, (2^bit_length) - abs(numd) or (2^bit_length) + numd
        positive_equivalent_val = (1 << bit_length) + numd # numd is negative
        bnumb = bin(positive_equivalent_val)[2:]
        return bnumb.zfill(bit_length)

# excessEightbits seems specific to 8 bits and a bias of 128.
# If you want to generalize it, it would need a bit_length and a bias parameter.
# For now, let's assume it's intentionally 8-bit specific as its name suggests.
def excessEightbits(numd_str):
    outnum = ""
    try:
        numd = int(numd_str)
    except ValueError:
        return "Error: Invalid decimal input"

    biased_num = numd + 128 # Standard Excess-128 for 8 bits
    # Range for biased_num should be 0 to 255 for 8 bits
    if not (0 <= biased_num <= 255):
        return f"Error: Value {numd} (biased to {biased_num}) out of 8-bit Excess-128 range."

    bnumb = bin(biased_num)[2:]
    outnum = bnumb.zfill(8)
    return outnum 