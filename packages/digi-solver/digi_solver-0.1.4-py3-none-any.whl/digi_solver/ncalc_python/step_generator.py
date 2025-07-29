from .utils import get_ordinal_text, get_ordinal_suffix
import math

# --- Step-by-step Conversion Functions (Plain Text) ---

def decimal_to_binary_steps(decimal_str):
    """Generates plain text steps for decimal to binary conversion."""
    steps = []
    try:
        n = int(decimal_str)
        if n < 0:
            steps.append("Error: Input must be a non-negative integer for step-by-step conversion.")
            return steps, None

        if n == 0:
            steps.append(f"{n} ÷ 2 = 0 remainder 0")
            steps.append("Result: 0")
            return steps, "0"

        original_n = n
        binary_representation = []
        steps.append(f"Converting decimal number {original_n} to binary:")
        steps.append("Method: Divide continuously by 2, note the remainders, read the result from bottom to top.")

        while n > 0:
            remainder = n % 2
            quotient = n // 2
            steps.append(f"{n} ÷ 2 = {quotient} remainder {remainder}")
            binary_representation.insert(0, str(remainder))
            n = quotient

        result_binary = "".join(binary_representation)
        steps.append(f"Reading remainders from bottom to top: {result_binary}")
        steps.append(f"Result: {result_binary}")
        return steps, result_binary
    except ValueError:
        steps.append(f"Error: Invalid decimal input for steps: {decimal_str}")
        return steps, None

def binary_to_decimal_steps(binary_str):
    """Generates plain text steps for binary to decimal conversion."""
    steps = []
    try:
        if not all(c in '01' for c in binary_str):
            steps.append(f"Error: Invalid binary digit in input: {binary_str}")
            return steps, None

        decimal_val = 0
        n_len = len(binary_str)
        steps.append(f"Converting binary number {binary_str} to decimal:")
        steps.append("Formula: Decimal = d_1 * 2^(n-1) + d_2 * 2^(n-2) + ... + d_n * 2^0")
        steps.append(f"For {binary_str}:")

        for i, digit_char in enumerate(binary_str):
            digit = int(digit_char)
            power = n_len - 1 - i
            term_value = digit * (2**power)
            steps.append(f"  {digit} * 2^{power} = {digit} * {2**power} = {term_value}")
            decimal_val += term_value

        steps.append(f"Sum: {decimal_val}")
        steps.append(f"Result: {decimal_val}")
        return steps, str(decimal_val)
    except ValueError: # Should be caught by the initial check, but as a safeguard
        steps.append(f"Error: Invalid binary input for steps: {binary_str}")
        return steps, None

def decimal_to_hexadecimal_steps(decimal_str):
    """Generates plain text steps for decimal to hexadecimal conversion."""
    steps = []
    try:
        n = int(decimal_str)
        if n < 0:
            steps.append("Error: Input must be a non-negative integer for step-by-step conversion.")
            return steps, None
        
        if n == 0:
            steps.append(f"{n} ÷ 16 = 0 remainder 0")
            steps.append("Result: 0")
            return steps, "0"

        original_n = n
        hex_representation = []
        hex_digits_map = "0123456789ABCDEF"
        steps.append(f"Converting decimal number {original_n} to hexadecimal:")
        steps.append("Method: Divide continuously by 16, note the remainders, read the result from bottom to top.")
        steps.append("Note: Remainders 10-15 are represented by A-F respectively.")

        while n > 0:
            remainder = n % 16
            quotient = n // 16
            hex_char = hex_digits_map[remainder]
            steps.append(f"{n} ÷ 16 = {quotient} remainder {remainder} (which is '{hex_char}' in hex)")
            hex_representation.insert(0, hex_char)
            n = quotient
        
        result_hex = "".join(hex_representation)
        steps.append(f"Reading remainders from bottom to top: {result_hex}")
        steps.append(f"Result: {result_hex}")
        return steps, result_hex
    except ValueError:
        steps.append(f"Error: Invalid decimal input for steps: {decimal_str}")
        return steps, None

def hexadecimal_to_decimal_steps(hex_str):
    """Generates plain text steps for hexadecimal to decimal conversion."""
    steps = []
    try:
        if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
            steps.append(f"Error: Invalid hexadecimal digit in input: {hex_str}")
            return steps, None

        upper_hex_str = hex_str.upper()
        decimal_val = 0
        n_len = len(upper_hex_str)
        steps.append(f"Converting hexadecimal number {upper_hex_str} to decimal:")
        steps.append("Formula: Decimal = d_1 * 16^(n-1) + d_2 * 16^(n-2) + ... + d_n * 16^0")
        steps.append("Note: A=10, B=11, C=12, D=13, E=14, F=15")
        steps.append(f"For {upper_hex_str}:")

        for i, hex_char in enumerate(upper_hex_str):
            power = n_len - 1 - i
            digit_val = 0
            digit_display = hex_char
            if 'A' <= hex_char <= 'F':
                digit_val = ord(hex_char) - ord('A') + 10
                digit_display = f"{hex_char} (={digit_val})"
            else:
                digit_val = int(hex_char)
            
            term_value = digit_val * (16**power)
            steps.append(f"  {digit_display} * 16^{power} = {digit_val} * {16**power} = {term_value}")
            decimal_val += term_value

        steps.append(f"Sum: {decimal_val}")
        steps.append(f"Result: {decimal_val}")
        return steps, str(decimal_val)
    except ValueError: # Should be caught by initial check
        steps.append(f"Error: Invalid hexadecimal input for steps: {hex_str}")
        return steps, None


# --- Step-by-step Conversion Functions (LaTeX Output) ---

def decimal_to_binary_steps_latex(decimal_str):
    """Generates LaTeX formatted steps for decimal to binary conversion."""
    try:
        original_n_int = int(decimal_str)
        if original_n_int < 0:
            return "Error: Input must be a non-negative integer for LaTeX step-by-step conversion.", None

        result_builder = []
        result_builder.append("\\begin{enumerate}")
        result_builder.append("\\item Method: Divide continuously by 2, note the remainders, read the result from bottom to top.")

        if original_n_int == 0:
            result_builder.append("\\begin{itemize}")
            result_builder.append(f"    \\item \\({original_n_int} \\div 2 = 0\\) remainder \\(0\\)")
            result_builder.append("\\end{itemize}")
            result_builder.append("\\item Read the result from bottom to top. Result: \\(0_2\\)")
            result_builder.append("\\end{enumerate}")
            return "".join(result_builder), "0"

        n_int = original_n_int
        binary_representation_list = []
        division_steps_latex = []

        while n_int > 0:
            remainder = n_int % 2
            quotient = n_int // 2
            division_steps_latex.append(f"    \\item \\({n_int} \\div 2 = {quotient}\\) remainder \\({remainder}\\)")
            binary_representation_list.insert(0, str(remainder))
            n_int = quotient
        
        result_builder.append("\\begin{itemize}")
        result_builder.extend(division_steps_latex)
        result_builder.append("\\end{itemize}")
        
        final_binary_str = "".join(binary_representation_list)
        result_builder.append(f"\\item Read the result from bottom to top. Result: \\({final_binary_str}_2\\)")
        result_builder.append("\\end{enumerate}")
        return "".join(result_builder), final_binary_str

    except ValueError:
        return f"Error: Invalid decimal input for LaTeX steps: {decimal_str}", None

def binary_to_decimal_steps_latex(binary_str):
    """Generates LaTeX formatted steps for binary to decimal conversion."""
    try:
        if not all(c in '01' for c in binary_str):
            return f"Error: Invalid binary digit in input: {binary_str}", None

        result_builder = []
        decimal_val_total = 0
        n_len = len(binary_str)

        result_builder.append("\\begin{enumerate}")
        result_builder.append("\\item Method: To convert a binary number to its decimal equivalent, assign each binary digit a positional weight based on its position, where the rightmost digit has a weight of \\(2^0\\), the next digit to the left has a weight of \\(2^1\\), and so on, up to the leftmost digit with a weight of \\(2^{n-1}\\) for a number with \\(n\\) digits. Multiply each digit by its corresponding power of 2, then sum all the products to obtain the decimal value, as expressed by the formula:")
        result_builder.append("\\begin{center}")
        result_builder.append("    \\(\\text{Decimal} = d_1 \\times 2^{n-1} + d_2 \\times 2^{n-2} + \\dots + d_n \\times 2^{0}\\)")
        result_builder.append("\\end{center}")
        result_builder.append(f"For \\({binary_str}_2\\) (\\(n = {n_len}\\) digits):")
        result_builder.append("\\item Calculate each part:")
        result_builder.append("\\begin{itemize}")

        sum_terms_latex = []
        for i, digit_char in enumerate(binary_str):
            digit = int(digit_char)
            power = n_len - 1 - i
            power_val_calc = int(math.pow(2, power))
            term_value = digit * power_val_calc
            decimal_val_total += term_value
            ordinal_text = get_ordinal_text(i + 1)
            result_builder.append(f"    \\item {ordinal_text} digit (\\(d_{i+1} = {digit}\\)): \\({digit} \\times 2^{{{n_len}-{i+1}}} = {digit} \\times 2^{power} = {digit} \\times {power_val_calc} = {term_value}\\)")
            if term_value > 0 or len(binary_str) == 1: # include 0 if it's the only digit
                 sum_terms_latex.append(str(term_value))

        result_builder.append("\\end{itemize}")
        sum_expression_latex = " + ".join(sum_terms_latex) if sum_terms_latex else "0"
        result_builder.append(f"\\item Sum: \\({sum_expression_latex} = {decimal_val_total}\\)")
        result_builder.append(f"\\item Final Answer: \\({decimal_val_total}_{{10}}\\)")
        result_builder.append("\\end{enumerate}")
        
        return "".join(result_builder), str(decimal_val_total)

    except ValueError:
        return f"Error: Invalid binary input for LaTeX steps: {binary_str}", None


def decimal_to_hexadecimal_steps_latex(decimal_str):
    """Generates LaTeX formatted steps for decimal to hexadecimal conversion."""
    try:
        original_n_int = int(decimal_str)
        if original_n_int < 0:
            return "Error: Input must be a non-negative integer for LaTeX step-by-step conversion.", None

        result_builder = []
        result_builder.append("\\begin{enumerate}")
        result_builder.append("\\item Method: Divide the decimal number by 16 repeatedly, record the remainders, and read the remainders from bottom to top to form the hexadecimal number.")
        result_builder.append("\\textbf{Note}: Hexadecimal digits range from 0 to 15, where:")
        result_builder.append("\\begin{itemize}")
        result_builder.append("    \\item \\(10 = A\\), \\(11 = B\\), \\(12 = C\\), \\(13 = D\\), \\(14 = E\\), \\(15 = F\\)")
        result_builder.append("\\end{itemize}")
        result_builder.append("\\item Perform the Division:")

        if original_n_int == 0:
            result_builder.append("\\begin{itemize}")
            result_builder.append(f"    \\item \\({original_n_int} \\div 16 = 0\\) remainder \\(0\\)")
            result_builder.append("\\end{itemize}")
            result_builder.append("\\item Read the Result: Reading the remainders from bottom to top: \\(0\\).")
            result_builder.append("\\item Thus, the hexadecimal number is \\(0_{16}\\).")
            result_builder.append("\\begin{center}")
            result_builder.append(f"\\textbf{{Final Answer:}} \\({original_n_int}_{{10}} = 0_{{16}}\\)")
            result_builder.append("\\end{center}")
            result_builder.append("\\end{enumerate}")
            return "".join(result_builder), "0"

        n_int = original_n_int
        hex_digits_map = "0123456789ABCDEF"
        hex_representation_list = []
        division_steps_latex = []

        result_builder.append(f"For \\({original_n_int}_{{10}}\\):")
        result_builder.append("\\begin{itemize}")

        while n_int > 0:
            remainder = n_int % 16
            quotient = n_int // 16
            hex_char = hex_digits_map[remainder]
            remainder_display = f"{remainder}" if remainder < 10 else f"{remainder} = {hex_char}"
            division_steps_latex.append(f"    \\item \\({n_int} \\div 16 = {quotient}\\) remainder \\({remainder_display}\\)")
            hex_representation_list.insert(0, hex_char)
            n_int = quotient
        
        result_builder.extend(division_steps_latex)
        result_builder.append("\\end{itemize}")
        
        final_hex_str = "".join(hex_representation_list)
        hex_digits_for_display = [f"\\({digit}\\)" for digit in final_hex_str]
        result_builder.append(f"\\item Read the Result: Reading the remainders from bottom to top: {', '.join(hex_digits_for_display)}.")
        result_builder.append(f"\\item Thus, the hexadecimal number is \\({final_hex_str}_{{16}}\\).")
        result_builder.append("\\begin{center}")
        result_builder.append(f"\\textbf{{Final Answer:}} \\({original_n_int}_{{10}} = {final_hex_str}_{{16}}\\)")
        result_builder.append("\\end{center}")
        result_builder.append("\\end{enumerate}")
        
        return "".join(result_builder), final_hex_str

    except ValueError:
        return f"Error: Invalid decimal input for LaTeX steps: {decimal_str}", None


def hexadecimal_to_decimal_steps_latex(hex_str):
    """Generates LaTeX formatted steps for hexadecimal to decimal conversion."""
    try:
        upper_hex_str = hex_str.upper()
        if not all(c in '0123456789ABCDEF' for c in upper_hex_str):
            return f"Error: Invalid hexadecimal digit in input: {upper_hex_str}", None

        result_builder = []
        decimal_val_total = 0
        n_len = len(upper_hex_str)

        result_builder.append("\\begin{enumerate}")
        result_builder.append("\\item Apply the formula: \\(\\text{Decimal} = d_1 \\times 16^{n-1} + d_2 \\times 16^{n-2} + \\dots + d_n \\times 16^{0}\\), where \\(d_i\\) represents each digit of the hexadecimal number, and \\(n\\) is the number of digits.")
        result_builder.append("\\item In hexadecimal, digits range from 0 to 15. Digits 0--9 are represented as is, while letters A--F represent values 10--15, respectively:")
        result_builder.append("\\begin{center}")
        result_builder.append("$A = 10$, $B = 11$, $C = 12$, $D = 13$, $E = 14$, $F = 15$")
        result_builder.append("\\end{center}")
        result_builder.append(f"\\item Calculate each term for the hexadecimal number \\({upper_hex_str}_{{16}}\\) (\\(n = {n_len}\\) digits):")
        
        formula_terms = []
        for i in range(n_len):
            formula_terms.append(f"d_{i+1} \\times 16^{{{n_len-1-i}}}")
        result_builder.append(f"The formula becomes: \\(\\text{{Decimal}} = {' + '.join(formula_terms)}\\).")
        
        result_builder.append("\\begin{itemize}")

        sum_terms_latex = []
        for i, hex_char_loop in enumerate(upper_hex_str):
            power = n_len - 1 - i
            digit_numeric_val = 0
            digit_display_text = hex_char_loop
            if 'A' <= hex_char_loop <= 'F':
                digit_numeric_val = ord(hex_char_loop) - ord('A') + 10
                digit_display_text = f"{hex_char_loop} = {digit_numeric_val}"
            else:
                digit_numeric_val = int(hex_char_loop)
            
            power_val_calc = int(math.pow(16, power))
            term_value_calc = digit_numeric_val * power_val_calc
            decimal_val_total += term_value_calc
            
            ordinal_text = get_ordinal_text(i + 1)
            result_builder.append(f"    \\item {ordinal_text} digit (\\(d_{i+1} = {digit_display_text}\\)): \\({digit_numeric_val} \\times 16^{{{power}}} = {digit_numeric_val} \\times {power_val_calc} = {term_value_calc}\\)")
            if term_value_calc > 0 or len(upper_hex_str) == 1:
                sum_terms_latex.append(str(term_value_calc))

        result_builder.append("\\end{itemize}")
        sum_expression_latex = " + ".join(sum_terms_latex) if sum_terms_latex else "0"
        result_builder.append(f"\\item Sum the results: \\({sum_expression_latex} = {decimal_val_total}\\).")
        result_builder.append(f"\\item Final Answer: \\({decimal_val_total}_{{{10}}}\\)")
        result_builder.append("\\end{enumerate}")
        
        return "".join(result_builder), str(decimal_val_total)

    except ValueError:
        return f"Error: Invalid hexadecimal input for LaTeX steps: {hex_str}", None 

# --- New Step-by-Step Functions (Plain Text and LaTeX) ---

# --- Decimal to Octal ---
def decimal_to_octal_steps(decimal_str):
    """Generates plain text steps for decimal to octal conversion."""
    steps = []
    try:
        n = int(decimal_str)
        if n < 0:
            steps.append("Error: Input must be a non-negative integer for step-by-step octal conversion.")
            return steps, None

        if n == 0:
            steps.append(f"{n} ÷ 8 = 0 remainder 0")
            steps.append("Result: 0")
            return steps, "0"

        original_n = n
        octal_representation = []
        steps.append(f"Converting decimal number {original_n} to octal:")
        steps.append("Method: Divide continuously by 8, note the remainders, read the result from bottom to top.")

        while n > 0:
            remainder = n % 8
            quotient = n // 8
            steps.append(f"{n} ÷ 8 = {quotient} remainder {remainder}")
            octal_representation.insert(0, str(remainder))
            n = quotient

        result_octal = "".join(octal_representation)
        steps.append(f"Reading remainders from bottom to top: {result_octal}")
        steps.append(f"Result: {result_octal}")
        return steps, result_octal
    except ValueError:
        steps.append(f"Error: Invalid decimal input for octal steps: {decimal_str}")
        return steps, None

def decimal_to_octal_steps_latex(decimal_str):
    """Generates LaTeX formatted steps for decimal to octal conversion."""
    try:
        original_n_int = int(decimal_str)
        if original_n_int < 0:
            return "Error: Input must be a non-negative integer for LaTeX step-by-step octal conversion.", None

        result_builder = ["\\begin{enumerate}"]
        result_builder.append("\\item Method: Divide continuously by 8, note the remainders, read the result from bottom to top.")

        if original_n_int == 0:
            result_builder.append("\\begin{itemize}")
            result_builder.append(f"    \\item \\({original_n_int} \\div 8 = 0\\) remainder \\(0\\)")
            result_builder.append("\\end{itemize}")
            result_builder.append(f"\\item Read the result from bottom to top. Result: \\(0_8\\)")
            result_builder.append("\\end{enumerate}")
            return "".join(result_builder), "0"

        n_int = original_n_int
        octal_representation_list = []
        division_steps_latex = []

        while n_int > 0:
            remainder = n_int % 8
            quotient = n_int // 8
            division_steps_latex.append(f"    \\item \\({n_int} \\div 8 = {quotient}\\) remainder \\({remainder}\\)")
            octal_representation_list.insert(0, str(remainder))
            n_int = quotient
        
        result_builder.append("\\begin{itemize}")
        result_builder.extend(division_steps_latex)
        result_builder.append("\\end{itemize}")
        
        final_octal_str = "".join(octal_representation_list)
        result_builder.append(f"\\item Read the result from bottom to top. Result: \\({final_octal_str}_8\\)")
        result_builder.append("\\end{enumerate}")
        return "".join(result_builder), final_octal_str
    except ValueError:
        return f"Error: Invalid decimal input for LaTeX octal steps: {decimal_str}", None

# --- Octal to Decimal ---
def octal_to_decimal_steps(octal_str):
    """Generates plain text steps for octal to decimal conversion."""
    steps = []
    try:
        if not all(c in '01234567' for c in octal_str):
            steps.append(f"Error: Invalid octal digit in input: {octal_str}")
            return steps, None

        decimal_val = 0
        n_len = len(octal_str)
        steps.append(f"Converting octal number {octal_str} to decimal:")
        steps.append("Formula: Decimal = d_1 * 8^(n-1) + d_2 * 8^(n-2) + ... + d_n * 8^0")
        steps.append(f"For {octal_str}:")

        for i, digit_char in enumerate(octal_str):
            digit = int(digit_char)
            power = n_len - 1 - i
            term_value = digit * (8**power)
            steps.append(f"  {digit} * 8^{power} = {digit} * {8**power} = {term_value}")
            decimal_val += term_value

        steps.append(f"Sum: {decimal_val}")
        steps.append(f"Result: {decimal_val}")
        return steps, str(decimal_val)
    except ValueError:
        steps.append(f"Error: Invalid octal input for steps: {octal_str}")
        return steps, None

def octal_to_decimal_steps_latex(octal_str):
    """Generates LaTeX formatted steps for octal to decimal conversion."""
    try:
        if not all(c in '01234567' for c in octal_str):
            return f"Error: Invalid octal digit in input: {octal_str}", None

        result_builder = ["\\begin{enumerate}"]
        decimal_val_total = 0
        n_len = len(octal_str)

        result_builder.append("\\item Method: To convert an octal number to its decimal equivalent, assign each octal digit a positional weight based on its position, where the rightmost digit has a weight of \\(8^0\\), the next digit to the left has a weight of \\(8^1\\), and so on, up to the leftmost digit with a weight of \\(8^{n-1}\\) for a number with \\(n\\) digits. Multiply each digit by its corresponding power of 8, then sum all the products to obtain the decimal value.")
        result_builder.append("\\begin{center}")
        result_builder.append("    \\(\\text{Decimal} = d_1 \\times 8^{n-1} + d_2 \\times 8^{n-2} + \\dots + d_n \\times 8^{0}\\)")
        result_builder.append("\\end{center}")
        result_builder.append(f"For \\({octal_str}_8\\) (\\(n = {n_len}\\) digits):")
        result_builder.append("\\item Calculate each part:")
        result_builder.append("\\begin{itemize}")

        sum_terms_latex = []
        for i, digit_char in enumerate(octal_str):
            digit = int(digit_char)
            power = n_len - 1 - i
            power_val_calc = int(math.pow(8, power))
            term_value = digit * power_val_calc
            decimal_val_total += term_value
            ordinal_text = get_ordinal_text(i + 1)
            result_builder.append(f"    \\item {ordinal_text} digit (\\(d_{i+1} = {digit}\\)): \\({digit} \\times 8^{{{n_len}-{i+1}}} = {digit} \\times 8^{power} = {digit} \\times {power_val_calc} = {term_value}\\)")
            if term_value > 0 or len(octal_str) == 1:
                 sum_terms_latex.append(str(term_value))

        result_builder.append("\\end{itemize}")
        sum_expression_latex = " + ".join(sum_terms_latex) if sum_terms_latex else "0"
        result_builder.append(f"\\item Sum: \\({sum_expression_latex} = {decimal_val_total}\\)")
        result_builder.append(f"\\item Final Answer: \\({decimal_val_total}_{{10}}\\)")
        result_builder.append("\\end{enumerate}")
        
        return "".join(result_builder), str(decimal_val_total)
    except ValueError:
        return f"Error: Invalid octal input for LaTeX steps: {octal_str}", None

# --- Hexadecimal to Binary ---
_HEX_TO_BIN_MAP = {
    '0': "0000", '1': "0001", '2': "0010", '3': "0011",
    '4': "0100", '5': "0101", '6': "0110", '7': "0111",
    '8': "1000", '9': "1001", 'A': "1010", 'B': "1011",
    'C': "1100", 'D': "1101", 'E': "1110", 'F': "1111"
}

def hexadecimal_to_binary_steps(hex_str):
    """Generates plain text steps for hexadecimal to binary conversion."""
    steps = []
    upper_hex_str = hex_str.upper()
    if not all(c in _HEX_TO_BIN_MAP for c in upper_hex_str):
        steps.append(f"Error: Invalid hexadecimal digit in input: {hex_str}")
        return steps, None
    
    if not upper_hex_str:
        steps.append("Error: Empty hexadecimal input.")
        return steps, None

    binary_result_parts = []
    steps.append(f"Converting hexadecimal number {upper_hex_str} to binary:")
    steps.append("Method: Convert each hexadecimal digit to its 4-bit binary equivalent.")
    steps.append("Hexadecimal to Binary Mapping:")
    for i, hex_digit in enumerate(upper_hex_str):
        binary_equivalent = _HEX_TO_BIN_MAP[hex_digit]
        steps.append(f"  Digit '{hex_digit}' (at position {i+1}) -> {binary_equivalent}")
        binary_result_parts.append(binary_equivalent)
    
    full_binary_representation = "".join(binary_result_parts)
    # Remove leading zeros unless it's the only digit "0"
    final_binary = full_binary_representation.lstrip('0') if full_binary_representation != "0000" else "0"
    if not final_binary and full_binary_representation: # if lstrip resulted in empty but original was not just "0000"
        final_binary = "0"


    steps.append(f"Combine the binary groups: {full_binary_representation}")
    if full_binary_representation != final_binary and final_binary != "0": # Show stripping only if it happened and result is not "0"
         steps.append(f"Remove leading zeros (if any, unless the number is 0): {final_binary}")
    
    steps.append(f"Result: {final_binary}")
    return steps, final_binary

def hexadecimal_to_binary_steps_latex(hex_str):
    """Generates LaTeX formatted steps for hexadecimal to binary conversion."""
    upper_hex_str = hex_str.upper()
    if not all(c in _HEX_TO_BIN_MAP for c in upper_hex_str):
        return f"Error: Invalid hexadecimal digit in input: {hex_str}", None
    if not upper_hex_str:
        return "Error: Empty hexadecimal input for LaTeX steps.", None

    result_builder = ["\\begin{enumerate}"]
    result_builder.append("\\item Method: Convert each hexadecimal digit to its 4-bit binary equivalent.")
    result_builder.append(f" For hexadecimal number \\({upper_hex_str}_{{16}}\\):")
    result_builder.append("\\begin{itemize}")

    binary_result_parts_latex = []
    raw_binary_parts = []

    for i, hex_digit_char in enumerate(upper_hex_str):
        binary_equivalent = _HEX_TO_BIN_MAP[hex_digit_char]
        ordinal_text = get_ordinal_text(i + 1)
        result_builder.append(f"    \\item The {ordinal_text} hexadecimal digit \\({{{hex_digit_char}}}\\) is equivalent to \\({{{binary_equivalent}}}_2\\).")
        binary_result_parts_latex.append(f"{{{binary_equivalent}}}")
        raw_binary_parts.append(binary_equivalent)

    result_builder.append("\\end{itemize}")
    
    full_binary_latex = "".join(binary_result_parts_latex)
    full_binary_raw = "".join(raw_binary_parts)
    
    # Normalize: remove leading zeros unless it's just "0"
    final_binary_raw = full_binary_raw.lstrip('0') if full_binary_raw != "0000" else "0"
    if not final_binary_raw and full_binary_raw: # handle cases like "0" -> "0000" -> "" by lstrip
        final_binary_raw = "0"


    result_builder.append(f"\\item Combine the 4-bit binary groups: ${full_binary_latex}$")
    
    # Display step for stripping leading zeros only if necessary and result isn't just "0"
    if full_binary_raw != final_binary_raw and final_binary_raw != "0":
        # To display the stripped version correctly in LaTeX, we might need to re-map it if it became empty.
        # However, final_binary_raw should now be correct ("0" or a string starting with "1").
        # We need to format final_binary_raw for LaTeX if it's different.
        # For simplicity, assume final_binary_raw can be directly used.
        # To show it visually, we could break it into groups again, but that's complex.
        # Let's just show the stripped raw string.
         result_builder.append(f"\\item Remove leading zeros (unless the entire number is zero): \\({{{final_binary_raw}}}_2\\).")


    result_builder.append(f"\\item Thus, \\({upper_hex_str}_{{16}} = {{{final_binary_raw}}}_2\\).")
    result_builder.append("\\end{enumerate}")
    
    return "".join(result_builder), final_binary_raw

# --- Binary to Hexadecimal ---
def _pad_binary_for_grouping(binary_str, group_size):
    remainder = len(binary_str) % group_size
    if remainder == 0:
        return binary_str
    return '0' * (group_size - remainder) + binary_str

_BIN_TO_HEX_MAP = {v: k for k, v in _HEX_TO_BIN_MAP.items()} # Reverse map

def binary_to_hexadecimal_steps(binary_str):
    """Generates plain text steps for binary to hexadecimal conversion."""
    steps = []
    if not all(c in '01' for c in binary_str):
        steps.append(f"Error: Invalid binary digit in input: {binary_str}")
        return steps, None
    if not binary_str:
        steps.append("Error: Empty binary input.")
        return steps, None
    
    # Handle "0" case separately to avoid padding issues leading to "0000" -> "0"
    if binary_str == "0":
        steps.append(f"Converting binary number {binary_str} to hexadecimal:")
        steps.append("Method: The binary number 0 is 0 in hexadecimal.")
        steps.append("Result: 0")
        return steps, "0"

    padded_binary = _pad_binary_for_grouping(binary_str, 4)
    steps.append(f"Converting binary number {binary_str} to hexadecimal:")
    steps.append("Method: Group the binary digits into sets of 4 from the right. Pad with leading zeros if necessary. Convert each 4-bit group to its hexadecimal equivalent.")
    if binary_str != padded_binary:
        steps.append(f"Pad with leading zeros to make groups of 4: {padded_binary}")
    
    hex_result_parts = []
    steps.append("Binary groups to Hexadecimal Mapping:")
    for i in range(0, len(padded_binary), 4):
        group = padded_binary[i:i+4]
        hex_digit = _BIN_TO_HEX_MAP[group]
        steps.append(f"  Group '{group}' -> {hex_digit}")
        hex_result_parts.append(hex_digit)
        
    final_hex = "".join(hex_result_parts)
    steps.append(f"Combine the hexadecimal digits: {final_hex}")
    steps.append(f"Result: {final_hex}")
    return steps, final_hex

def binary_to_hexadecimal_steps_latex(binary_str):
    """Generates LaTeX formatted steps for binary to hexadecimal conversion."""
    if not all(c in '01' for c in binary_str):
        return f"Error: Invalid binary digit in input: {binary_str}", None
    if not binary_str:
        return "Error: Empty binary input for LaTeX steps.", None

    if binary_str == "0":
        return "\\begin{enumerate}\\item The binary number \\({0}_2\\) is \\({0}_{16}\\).\\end{enumerate}", "0"

    result_builder = ["\\begin{enumerate}"]
    result_builder.append("\\item Method: Group the binary digits into sets of 4 from the right. Pad with leading zeros if necessary. Convert each 4-bit group to its hexadecimal equivalent.")
    result_builder.append(f"For binary number \\({{{binary_str}}}_2\\):")

    padded_binary = _pad_binary_for_grouping(binary_str, 4)
    if binary_str != padded_binary:
        result_builder.append(f"\\item Pad with leading zeros to ensure the length is a multiple of 4: \\({{{padded_binary}}}_2\\).")
    
    result_builder.append("\\item Convert each 4-bit group to its hexadecimal equivalent:")
    result_builder.append("\\begin{itemize}")

    hex_result_parts_latex = []
    raw_hex_parts = []
    
    # Create spaced version of padded_binary for display
    spaced_padded_binary = ' '.join([padded_binary[i:i+4] for i in range(0, len(padded_binary), 4)])
    result_builder.append(f"    \\item Grouped binary: \\({{{spaced_padded_binary}}}\\)")


    for i in range(0, len(padded_binary), 4):
        group = padded_binary[i:i+4]
        hex_digit = _BIN_TO_HEX_MAP[group]
        result_builder.append(f"    \\item The group \\({{{group}}}_2\\) is equivalent to \\({{{hex_digit}}}_{{16}}\\).")
        hex_result_parts_latex.append(f"{{{hex_digit}}}")
        raw_hex_parts.append(hex_digit)
        
    result_builder.append("\\end{itemize}")
    
    final_hex_latex = "".join(hex_result_parts_latex)
    final_hex_raw = "".join(raw_hex_parts)
    
    result_builder.append(f"\\item Combine the hexadecimal digits: ${final_hex_latex}$")
    result_builder.append(f"\\item Thus, \\({{{binary_str}}}_2 = {final_hex_latex}_{{16}}\\). (Result: \\({{{final_hex_raw}}}_{{16}}\\))")
    result_builder.append("\\end{enumerate}")
    
    return "".join(result_builder), final_hex_raw

# --- Octal to Binary ---
_OCT_TO_BIN_MAP = {
    '0': "000", '1': "001", '2': "010", '3': "011",
    '4': "100", '5': "101", '6': "110", '7': "111"
}

def octal_to_binary_steps(octal_str):
    """Generates plain text steps for octal to binary conversion."""
    steps = []
    if not all(c in _OCT_TO_BIN_MAP for c in octal_str):
        steps.append(f"Error: Invalid octal digit in input: {octal_str}")
        return steps, None
    if not octal_str:
        steps.append("Error: Empty octal input.")
        return steps, None

    binary_result_parts = []
    steps.append(f"Converting octal number {octal_str} to binary:")
    steps.append("Method: Convert each octal digit to its 3-bit binary equivalent.")
    steps.append("Octal to Binary Mapping:")
    for i, oct_digit in enumerate(octal_str):
        binary_equivalent = _OCT_TO_BIN_MAP[oct_digit]
        steps.append(f"  Digit '{oct_digit}' (at position {i+1}) -> {binary_equivalent}")
        binary_result_parts.append(binary_equivalent)
    
    full_binary_representation = "".join(binary_result_parts)
    final_binary = full_binary_representation.lstrip('0') if full_binary_representation != "000" else "0"
    if not final_binary and full_binary_representation: # if lstrip resulted in empty
        final_binary = "0"

    steps.append(f"Combine the binary groups: {full_binary_representation}")
    if full_binary_representation != final_binary and final_binary != "0":
         steps.append(f"Remove leading zeros (if any, unless the number is 0): {final_binary}")
    
    steps.append(f"Result: {final_binary}")
    return steps, final_binary

def octal_to_binary_steps_latex(octal_str):
    """Generates LaTeX formatted steps for octal to binary conversion."""
    if not all(c in _OCT_TO_BIN_MAP for c in octal_str):
        return f"Error: Invalid octal digit in input: {octal_str}", None
    if not octal_str:
        return "Error: Empty octal input for LaTeX steps.", None

    result_builder = ["\\begin{enumerate}"]
    result_builder.append("\\item Method: Convert each octal digit to its 3-bit binary equivalent.")
    result_builder.append(f"For octal number \\({octal_str}_8\\):")
    result_builder.append("\\begin{itemize}")

    binary_result_parts_latex = []
    raw_binary_parts = []
    for i, oct_digit_char in enumerate(octal_str):
        binary_equivalent = _OCT_TO_BIN_MAP[oct_digit_char]
        ordinal_text = get_ordinal_text(i + 1)
        result_builder.append(f"    \\item The {ordinal_text} octal digit \\({{{oct_digit_char}}}\\) is equivalent to \\({{{binary_equivalent}}}_2\\).")
        binary_result_parts_latex.append(f"{{{binary_equivalent}}}")
        raw_binary_parts.append(binary_equivalent)

    result_builder.append("\\end{itemize}")
    
    full_binary_latex = "".join(binary_result_parts_latex)
    full_binary_raw = "".join(raw_binary_parts)
    final_binary_raw = full_binary_raw.lstrip('0') if full_binary_raw != "000" else "0"
    if not final_binary_raw and full_binary_raw :
        final_binary_raw = "0"

    result_builder.append(f"\\item Combine the 3-bit binary groups: ${full_binary_latex}$")
    if full_binary_raw != final_binary_raw and final_binary_raw != "0":
         result_builder.append(f"\\item Remove leading zeros (unless the entire number is zero): \\({{{final_binary_raw}}}_2\\).")
    
    result_builder.append(f"\\item Thus, \\({octal_str}_8 = {{{final_binary_raw}}}_2\\).")
    result_builder.append("\\end{enumerate}")
    
    return "".join(result_builder), final_binary_raw

# --- Binary to Octal ---
_BIN_TO_OCT_MAP = {v: k for k, v in _OCT_TO_BIN_MAP.items()} # Reverse map

def binary_to_octal_steps(binary_str):
    """Generates plain text steps for binary to octal conversion."""
    steps = []
    if not all(c in '01' for c in binary_str):
        steps.append(f"Error: Invalid binary digit in input: {binary_str}")
        return steps, None
    if not binary_str:
        steps.append("Error: Empty binary input.")
        return steps, None

    if binary_str == "0":
        steps.append(f"Converting binary number {binary_str} to octal:")
        steps.append("Method: The binary number 0 is 0 in octal.")
        steps.append("Result: 0")
        return steps, "0"

    padded_binary = _pad_binary_for_grouping(binary_str, 3)
    steps.append(f"Converting binary number {binary_str} to octal:")
    steps.append("Method: Group the binary digits into sets of 3 from the right. Pad with leading zeros if necessary. Convert each 3-bit group to its octal equivalent.")
    if binary_str != padded_binary:
        steps.append(f"Pad with leading zeros to make groups of 3: {padded_binary}")
    
    octal_result_parts = []
    steps.append("Binary groups to Octal Mapping:")
    for i in range(0, len(padded_binary), 3):
        group = padded_binary[i:i+3]
        octal_digit = _BIN_TO_OCT_MAP[group]
        steps.append(f"  Group '{group}' -> {octal_digit}")
        octal_result_parts.append(octal_digit)
        
    final_octal = "".join(octal_result_parts)
    steps.append(f"Combine the octal digits: {final_octal}")
    steps.append(f"Result: {final_octal}")
    return steps, final_octal

def binary_to_octal_steps_latex(binary_str):
    """Generates LaTeX formatted steps for binary to octal conversion."""
    if not all(c in '01' for c in binary_str):
        return f"Error: Invalid binary digit in input: {binary_str}", None
    if not binary_str:
        return "Error: Empty binary input for LaTeX steps.", None

    if binary_str == "0":
        return "\\begin{enumerate}\\item The binary number \\({0}_2\\) is \\({0}_8\\).\\end{enumerate}", "0"

    result_builder = ["\\begin{enumerate}"]
    result_builder.append("\\item Method: Group the binary digits into sets of 3 from the right. Pad with leading zeros if necessary. Convert each 3-bit group to its octal equivalent.")
    result_builder.append(f"For binary number \\({{{binary_str}}}_2\\):")

    padded_binary = _pad_binary_for_grouping(binary_str, 3)
    if binary_str != padded_binary:
        result_builder.append(f"\\item Pad with leading zeros to ensure the length is a multiple of 3: \\({{{padded_binary}}}_2\\).")
    
    result_builder.append("\\item Convert each 3-bit group to its octal equivalent:")
    result_builder.append("\\begin{itemize}")

    octal_result_parts_latex = []
    raw_octal_parts = []
    
    spaced_padded_binary = ' '.join([padded_binary[i:i+3] for i in range(0, len(padded_binary), 3)])
    result_builder.append(f"    \\item Grouped binary: \\({{{spaced_padded_binary}}}\\)")

    for i in range(0, len(padded_binary), 3):
        group = padded_binary[i:i+3]
        octal_digit = _BIN_TO_OCT_MAP[group]
        result_builder.append(f"    \\item The group \\({{{group}}}_2\\) is equivalent to \\({{{octal_digit}}}_8\\).")
        octal_result_parts_latex.append(f"{{{octal_digit}}}")
        raw_octal_parts.append(octal_digit)
        
    result_builder.append("\\end{itemize}")
    
    final_octal_latex = "".join(octal_result_parts_latex)
    final_octal_raw = "".join(raw_octal_parts)
    
    result_builder.append(f"\\item Combine the octal digits: ${final_octal_latex}$")
    result_builder.append(f"\\item Thus, \\({{{binary_str}}}_2 = {final_octal_latex}_8\\). (Result: \\({{{final_octal_raw}}}_8\\))")
    result_builder.append("\\end{enumerate}")
    
    return "".join(result_builder), final_octal_raw

# --- Hexadecimal to Octal (via Binary) ---
def hexadecimal_to_octal_steps(hex_str):
    """Generates plain text steps for hexadecimal to octal conversion (via binary)."""
    steps = [f"Converting hexadecimal {hex_str} to octal. This is a two-step process:"]
    steps.append("Step 1: Convert Hexadecimal to Binary.")
    
    hex_to_bin_sub_steps, binary_representation = hexadecimal_to_binary_steps(hex_str)
    if binary_representation is None: # Error occurred
        return hex_to_bin_sub_steps, None # Return error steps from sub-function
    
    # Indent sub-steps for clarity
    for sub_step in hex_to_bin_sub_steps:
        steps.append(f"  {sub_step}")
    steps.append(f"Intermediate binary result: {binary_representation}")
    steps.append("\\nStep 2: Convert the intermediate Binary to Octal.")
    
    bin_to_oct_sub_steps, final_octal_result = binary_to_octal_steps(binary_representation)
    if final_octal_result is None: # Error occurred
        # Combine main steps with error sub-steps
        steps.extend([f"  {s}" for s in bin_to_oct_sub_steps])
        return steps, None

    for sub_step in bin_to_oct_sub_steps:
        steps.append(f"  {sub_step}")
        
    steps.append(f"Final Result: Hexadecimal {hex_str} = Octal {final_octal_result}")
    return steps, final_octal_result

def hexadecimal_to_octal_steps_latex(hex_str):
    """Generates LaTeX formatted steps for hexadecimal to octal conversion (via binary)."""
    result_builder = ["\\begin{enumerate}"]
    result_builder.append("\\item This is a two-step process: first convert Hexadecimal to Binary, then Binary to Octal.")
    
    # Step 1: Hex to Binary
    result_builder.append("\\item \\textbf{Step 1: Convert Hexadecimal to Binary}")
    hex_to_bin_latex, binary_representation = hexadecimal_to_binary_steps_latex(hex_str)
    if binary_representation is None: # Error occurred
        return hex_to_bin_latex, None # Return error LaTeX from sub-function

    result_builder.append(hex_to_bin_latex) # This already contains its own enumerate
    result_builder.append(f"Intermediate binary result: \\({{{binary_representation}}}_2\\)")
    
    # Step 2: Binary to Octal
    result_builder.append(f"\\item \\textbf{{Step 2: Convert Binary (\\({{{binary_representation}}}_2\\)) to Octal}}")
    bin_to_oct_latex, final_octal_result = binary_to_octal_steps_latex(binary_representation)
    if final_octal_result is None: # Error occurred
        # Append the error LaTeX from the sub-conversion
        result_builder.append(bin_to_oct_latex)
        result_builder.append("\\end{enumerate}")
        return "".join(result_builder), None
        
    result_builder.append(bin_to_oct_latex) # This also contains its own enumerate
    
    result_builder.append(f"\\item \\textbf{{Final Result:}} Combining the steps, \\({hex_str.upper()}_{{16}} = {{{binary_representation}}}_2 = {{{final_octal_result}}}_8\\).")
    result_builder.append("\\end{enumerate}")
    return "".join(result_builder), final_octal_result

# --- Octal to Hexadecimal (via Binary) ---
def octal_to_hexadecimal_steps(octal_str):
    """Generates plain text steps for octal to hexadecimal conversion (via binary)."""
    steps = [f"Converting octal {octal_str} to hexadecimal. This is a two-step process:"]
    steps.append("Step 1: Convert Octal to Binary.")

    oct_to_bin_sub_steps, binary_representation = octal_to_binary_steps(octal_str)
    if binary_representation is None:
        return oct_to_bin_sub_steps, None
        
    for sub_step in oct_to_bin_sub_steps:
        steps.append(f"  {sub_step}")
    steps.append(f"Intermediate binary result: {binary_representation}")
    steps.append("\\nStep 2: Convert the intermediate Binary to Hexadecimal.")

    bin_to_hex_sub_steps, final_hex_result = binary_to_hexadecimal_steps(binary_representation)
    if final_hex_result is None:
        steps.extend([f"  {s}" for s in bin_to_hex_sub_steps])
        return steps, None

    for sub_step in bin_to_hex_sub_steps:
        steps.append(f"  {sub_step}")
        
    steps.append(f"Final Result: Octal {octal_str} = Hexadecimal {final_hex_result.upper()}")
    return steps, final_hex_result.upper()


def octal_to_hexadecimal_steps_latex(octal_str):
    """Generates LaTeX formatted steps for octal to hexadecimal conversion (via binary)."""
    result_builder = ["\\begin{enumerate}"]
    result_builder.append("\\item This is a two-step process: first convert Octal to Binary, then Binary to Hexadecimal.")

    # Step 1: Octal to Binary
    result_builder.append("\\item \\textbf{Step 1: Convert Octal to Binary}")
    oct_to_bin_latex, binary_representation = octal_to_binary_steps_latex(octal_str)
    if binary_representation is None:
        return oct_to_bin_latex, None

    result_builder.append(oct_to_bin_latex)
    result_builder.append(f"Intermediate binary result: \\({{{binary_representation}}}_2\\)")

    # Step 2: Binary to Hexadecimal
    result_builder.append("\\item \\textbf{Step 2: Convert Binary (\\({{{binary_representation}}}_2\\)) to Hexadecimal}")
    bin_to_hex_latex, final_hex_result = binary_to_hexadecimal_steps_latex(binary_representation)
    if final_hex_result is None:
        result_builder.append(bin_to_hex_latex)
        result_builder.append("\\end{enumerate}")
        return "".join(result_builder), None
        
    result_builder.append(bin_to_hex_latex)
    
    final_hex_result_upper = final_hex_result.upper() # Ensure final hex is uppercase
    result_builder.append(f"\\item \\textbf{{Final Result:}} Combining the steps, \\({octal_str}_8 = {{{binary_representation}}}_2 = {{{final_hex_result_upper}}}_{{16}}\\).")
    result_builder.append("\\end{enumerate}")
    return "".join(result_builder), final_hex_result_upper 