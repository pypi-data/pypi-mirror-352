def signedMagnitude_re(numb, bit_length=None):
    if bit_length is not None and len(numb) != bit_length:
        return f"Error: Binary string length {len(numb)} does not match expected bit_length {bit_length}."
    if not all(c in '01' for c in numb):
        return "Error: Invalid binary input"
    if not numb:
        return "Error: Empty binary string"

    result = ""
    if numb[0] == "0":
        result = str(int(numb, 2)) # Positive number
    elif numb[0] == "1":
        if len(numb) == 1: # Just "1"
            return "Error: Invalid signed magnitude '1'"
        magnitude_part = numb[1:]
        if not magnitude_part: # Should not happen if len(numb) > 1
             return "Error: Missing magnitude part"
        result = "-" + str(int(magnitude_part, 2))
    return result

def onesComplement_re(numb, bit_length=None):
    if bit_length is not None and len(numb) != bit_length:
        return f"Error: Binary string length {len(numb)} does not match expected bit_length {bit_length}."
    if not all(c in '01' for c in numb):
        return "Error: Invalid binary input"
    if not numb:
        return "Error: Empty binary string"

    result = ""
    if numb[0] == "0":
        result = str(int(numb, 2)) # Positive number
    elif numb[0] == "1":
        # For negative, invert bits then convert to decimal
        # (2^(bit_length) - 1) - int(original_negative_representation, 2)
        # or more directly: if MSB is 1, it's -( (2^len(numb) -1) - int(numb,2) )
        # but this is the value of the *inverted* positive number, so it needs care.
        # Simpler: value = int(numb, 2) - ( (1 << len(numb)) -1 ) if it was positive and then got flipped
        # The decimal value of the negative 1's complement number is -( (2^N - 1) - X_bin )
        # where X_bin is the integer value of the 1's complement binary string.
        # N is the number of bits (len(numb)).
        val_of_bin = int(numb, 2)
        # (1 << len(numb)) - 1 creates a mask of all 1s for len(numb) bits.
        # The magnitude is (all_ones_mask - val_of_bin)
        magnitude = ((1 << len(numb)) - 1) - val_of_bin
        result = "-" + str(magnitude)
    return result

def twosComplement_re(numb, bit_length=None):
    if bit_length is not None and len(numb) != bit_length:
        return f"Error: Binary string length {len(numb)} does not match expected bit_length {bit_length}."
    if not all(c in '01' for c in numb):
        return "Error: Invalid binary input"
    if not numb:
        return "Error: Empty binary string"

    result = ""
    if numb[0] == "0":
        result = str(int(numb, 2)) # Positive number
    elif numb[0] == "1":
        # For negative, it's int(numb, 2) - 2^bit_length
        val_of_bin = int(numb, 2)
        # (1 << len(numb)) is 2^len(numb)
        decimal_equivalent = val_of_bin - (1 << len(numb))
        result = str(decimal_equivalent)
    return result

# excessEightbits_re seems specific to 8 bits and a bias of 128.
# Let's keep its signature as is, assuming it's intentionally 8-bit specific.
def excessEightbits_re(numb):
    if len(numb) != 8:
        return "Error: Input for excessEightbits_re must be an 8-bit string."
    if not all(c in '01' for c in numb):
        return "Error: Invalid binary input"

    numd = int(numb, 2)
    result = str(numd - 128)
    return result 