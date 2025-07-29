# --- Conversion Functions ---

def decimal_to_binary(decimal_str):
    """Converts a decimal string to a binary string."""
    try:
        n = int(decimal_str)
        if n < 0:
            return "Error: Input must be non-negative for binary conversion."
        if n == 0:
            return "0"
        return bin(n)[2:]
    except ValueError:
        return f"Error: Invalid decimal input '{decimal_str}'"

def binary_to_decimal(binary_str):
    """Converts a binary string to a decimal string."""
    try:
        if not all(c in '01' for c in binary_str):
            return f"Error: Invalid binary digit in '{binary_str}'"
        return str(int(binary_str, 2))
    except ValueError:
        return f"Error: Invalid binary input '{binary_str}'"

def decimal_to_hexadecimal(decimal_str):
    """Converts a decimal string to a hexadecimal string."""
    try:
        n = int(decimal_str)
        if n < 0:
            return "Error: Input must be non-negative for hexadecimal conversion."
        return hex(n)[2:].upper()
    except ValueError:
        return f"Error: Invalid decimal input '{decimal_str}'"

def hexadecimal_to_decimal(hex_str):
    """Converts a hexadecimal string to a decimal string."""
    try:
        if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
            return f"Error: Invalid hexadecimal digit in '{hex_str}'"
        return str(int(hex_str, 16))
    except ValueError:
        return f"Error: Invalid hexadecimal input '{hex_str}'"

# --- New Conversion Functions ---

def decimal_to_octal(decimal_str):
    """Converts a decimal string to an octal string."""
    try:
        n = int(decimal_str)
        if n < 0:
            return "Error: Input must be non-negative for octal conversion."
        if n == 0:
            return "0"
        return oct(n)[2:]
    except ValueError:
        return f"Error: Invalid decimal input '{decimal_str}'"

def octal_to_decimal(octal_str):
    """Converts an octal string to a decimal string."""
    try:
        if not all(c in '01234567' for c in octal_str):
            return f"Error: Invalid octal digit in '{octal_str}'"
        return str(int(octal_str, 8))
    except ValueError:
        return f"Error: Invalid octal input '{octal_str}'"

def hexadecimal_to_binary(hex_str):
    """Converts a hexadecimal string to a binary string."""
    try:
        if not hex_str: return "Error: Empty hexadecimal input"
        if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
            return f"Error: Invalid hexadecimal digit in '{hex_str}'"
        # Convert hex to decimal, then decimal to binary string (without '0b' prefix)
        decimal_val = int(hex_str, 16)
        if decimal_val == 0: return "0"
        return bin(decimal_val)[2:]
    except ValueError:
        return f"Error: Invalid hexadecimal input '{hex_str}'"

def binary_to_hexadecimal(binary_str):
    """Converts a binary string to a hexadecimal string."""
    try:
        if not binary_str: return "Error: Empty binary input"
        if not all(c in '01' for c in binary_str):
            return f"Error: Invalid binary digit in '{binary_str}'"
        # Convert binary to decimal, then decimal to hex string (without '0x' prefix, uppercase)
        decimal_val = int(binary_str, 2)
        return hex(decimal_val)[2:].upper()
    except ValueError: # Should be caught by the digit check, but as a safeguard
        return f"Error: Invalid binary input '{binary_str}'"

def octal_to_binary(octal_str):
    """Converts an octal string to a binary string."""
    try:
        if not octal_str: return "Error: Empty octal input"
        if not all(c in '01234567' for c in octal_str):
            return f"Error: Invalid octal digit in '{octal_str}'"
        decimal_val = int(octal_str, 8)
        if decimal_val == 0: return "0"
        return bin(decimal_val)[2:]
    except ValueError:
        return f"Error: Invalid octal input '{octal_str}'"

def binary_to_octal(binary_str):
    """Converts a binary string to an octal string."""
    try:
        if not binary_str: return "Error: Empty binary input"
        if not all(c in '01' for c in binary_str):
            return f"Error: Invalid binary digit in '{binary_str}'"
        decimal_val = int(binary_str, 2)
        if decimal_val == 0: return "0"
        return oct(decimal_val)[2:]
    except ValueError:
        return f"Error: Invalid binary input '{binary_str}'"

# --- Combined Conversions (using binary as intermediary) ---

def hexadecimal_to_octal(hex_str):
    """Converts a hexadecimal string to an octal string (via binary)."""
    binary_representation = hexadecimal_to_binary(hex_str)
    if "Error:" in binary_representation:
        return binary_representation # Propagate error
    return binary_to_octal(binary_representation)

def octal_to_hexadecimal(octal_str):
    """Converts an octal string to a hexadecimal string (via binary)."""
    binary_representation = octal_to_binary(octal_str)
    if "Error:" in binary_representation:
        return binary_representation # Propagate error
    return binary_to_hexadecimal(binary_representation) 