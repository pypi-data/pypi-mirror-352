def get_signedmagnitude_re_solution(binary_num):
    # Get the decimal value
    decimal_value = signedmagnitude_binary_to_decimal(binary_num)
    
    # Build the solution with LaTeX formatting
    solution = "\\begin{enumerate}\n"
    
    # Step 1: Identify the sign bit
    sign_bit = binary_num[0]
    magnitude_part = binary_num[1:]
    
    solution += f"\\item Identify the sign bit and magnitude part:\n\\begin{{itemize}}\n"
    solution += f"\\item Sign bit: ${sign_bit}$\n"
    solution += f"\\item Magnitude part: ${magnitude_part}_2$\n\\end{{itemize}}\n"
    
    # Step 2: Interpret the sign bit
    solution += f"\\item Interpret the sign bit: "
    if sign_bit == '0':
        solution += f"Sign bit is 0, so this is a positive number.\n"
    else:
        solution += f"Sign bit is 1, so this is a negative number.\n"
    
    # Step 3: Convert the magnitude part to decimal
    magnitude_decimal = 0
    solution += f"\\item Convert the magnitude part ${magnitude_part}_2$ to decimal:\n\\begin{{itemize}}\n"
    
    for i, bit in enumerate(magnitude_part):
        position = len(magnitude_part) - i - 1
        if bit == '1':
            value = 2 ** position
            magnitude_decimal += value
            solution += f"\\item Bit ${bit}$ at position ${position}$ contributes $2^{{{position}}} = {value}$\n"
        else:
            solution += f"\\item Bit ${bit}$ at position ${position}$ contributes $0$\n"
    
    solution += "\\end{itemize}\n"
    solution += f"Magnitude value in decimal: ${magnitude_decimal}_{{10}}$\n"
    
    # Step 4: Apply the sign
    solution += f"\\item Apply the sign to the decimal value: "
    if sign_bit == '0':
        solution += f"Positive sign, so the decimal value is ${magnitude_decimal}_{{10}}$\n"
    else:
        solution += f"Negative sign, so the decimal value is $-{magnitude_decimal}_{{10}}$\n"
    
    # Final answer
    solution += f"\\begin{{center}}\nFinal answer: The binary number ${binary_num}_2$ in Signed Magnitude representation is ${decimal_value}_{{10}}$\n\\end{{center}}\n"
    solution += "\\end{enumerate}"
    
    return solution

def get_onescomplement_re_solution(binary_num):
    # Get the decimal value
    decimal_value = onescomplement_binary_to_decimal(binary_num)
    
    # Build the solution with LaTeX formatting
    solution = "\\begin{enumerate}\n"
    
    # Step 1: Identify the sign bit
    sign_bit = binary_num[0]
    value_part = binary_num[1:]
    
    solution += f"\\item Identify the sign bit and value part:\n\\begin{{itemize}}"
    solution += f"\\item Sign bit: ${sign_bit}$\n"
    solution += f"\\item Value part: ${value_part}_2$\n \\end{{itemize}}"
    
    # Step 2: Interpret the sign bit
    solution += f"\\item Interpret the sign bit: "
    if sign_bit == '0':
        solution += f"Sign bit is 0, so this is a positive number.\n"
        
        # Step 3: For positive numbers, convert directly
        solution += f"\\item For positive numbers in One's Complement, convert directly to decimal:\n\\begin{{itemize}}\n"
        
        decimal_val = 0
        for i, bit in enumerate(binary_num):
            position = len(binary_num) - i - 1
            if bit == '1':
                value = 2 ** position
                decimal_val += value
                solution += f"\\item Bit ${bit}$ at position ${position}$ contributes $2^{{{position}}} = {value}$\n"
            else:
                solution += f"\\item Bit ${bit}$ at position ${position}$ contributes $0$\n"
        
        solution += "\\end{itemize}\n"
        solution += f"Decimal value: ${decimal_val}_{{10}}$\n"
    
    else:
        # Step 3: For negative numbers, find the ones' complement
        solution += f"\\item For negative numbers in One's Complement, invert all bits (get One's Complement) then convert to decimal: "
        inverted_binary = ''
        for bit in binary_num:
            inverted_bit = '1' if bit == '0' else '0'
            inverted_binary += inverted_bit
        
        solution += f"Invert all bits: ${binary_num}_2 \\rightarrow {inverted_binary}_2$\n"
        
        # Step 4: Convert the inverted binary to decimal
        solution += f"\\item Convert the inverted number ${inverted_binary}_2$ to decimal:\n\\begin{{itemize}}\n"
        
        inverted_decimal = 0
        for i, bit in enumerate(inverted_binary):
            position = len(inverted_binary) - i - 1
            if bit == '1':
                value = 2 ** position
                inverted_decimal += value
                solution += f"\\item Bit ${bit}$ at position ${position}$ contributes $2^{{{position}}} = {value}$\n"
            else:
                solution += f"\\item Bit ${bit}$ at position ${position}$ contributes $0$\n"
        
        solution += "\\end{itemize}\n"
        solution += f"Decimal value after inversion: ${inverted_decimal}_{{10}}$\n"
        
        # Step 5: Apply the negative sign
        solution += f"\\item Apply the negative sign to the result: "
        solution += f"$-{inverted_decimal}_{{10}}$\n"
    
    # Final answer
    solution += f"\\begin{{center}}\nFinal answer: The binary number ${binary_num}_2$ in One's Complement representation is ${decimal_value}_{{10}}$\n\\end{{center}}\n"
    solution += "\\end{enumerate}"
    
    return solution

def get_twoscomplement_re_solution(binary_num):
    # Get the decimal value
    decimal_value = twoscomplement_binary_to_decimal(binary_num)
    
    # Build the solution with LaTeX formatting
    solution = "\\begin{enumerate}\n"

    # Step 1: Identify the sign bit
    sign_bit = binary_num[0]
    
    solution += f"\\item Identify the sign bit: "
    
    # Step 2: Interpret based on the sign bit
    if sign_bit == '0':
        # Positive number
        solution += f"Sign bit is 0, so this is a positive number in Two's Complement.\n"
        
        # Step 3: Convert to decimal directly
        solution += f"\\item For positive numbers in Two's Complement, convert directly to decimal:\n\\begin{{itemize}}\n"
        
        decimal_val = 0
        for i, bit in enumerate(binary_num):
            position = len(binary_num) - i - 1
            if bit == '1':
                value = 2 ** position
                decimal_val += value
                solution += f"\\item Bit ${bit}$ at position ${position}$ contributes $2^{{{position}}} = {value}$\n"
            else:
                solution += f"\\item Bit ${bit}$ at position ${position}$ contributes $0$\n"
        
        solution += "\\end{itemize}\n"
        solution += f"Decimal value: ${decimal_val}_{{10}}$\n"
    
    else:
        # Negative number
        solution += f"Sign bit is 1, so this is a negative number in Two's Complement.\n"
        
        # Step 3: Find two's complement
        solution += f"\\item To find the decimal value of a negative number in Two's Complement, follow these steps:\n\\begin{{itemize}}\n"
        
        # Step 3a: Invert all bits
        solution += f"\\item Invert all bits (get One's Complement): "
        inverted_binary = ''
        for bit in binary_num:
            inverted_bit = '1' if bit == '0' else '0'
            inverted_binary += inverted_bit
        
        solution += f"${binary_num}_2 \\rightarrow {inverted_binary}_2$\n"
        
        # Step 3b: Add 1 to get the two's complement
        solution += f"\\item Add 1 to get the Two's Complement: "
        inverted_decimal = int(inverted_binary, 2)
        twos_complement_decimal = inverted_decimal + 1
        twos_complement_binary = bin(twos_complement_decimal)[2:].zfill(len(binary_num))
        
        solution += f"${inverted_binary}_2 + 1 = {twos_complement_binary}_2$\n"
        
        # Step 3c: Convert to decimal
        solution += f"\\item Convert the result to decimal:\n\\begin{{itemize}}\n"
        
        abs_decimal = 0
        for i, bit in enumerate(twos_complement_binary):
            position = len(twos_complement_binary) - i - 1
            if bit == '1':
                value = 2 ** position
                abs_decimal += value
                solution += f"\\item Bit ${bit}$ at position ${position}$ contributes $2^{{{position}}} = {value}$\n"
            else:
                solution += f"\\item Bit ${bit}$ at position ${position}$ contributes $0$\n"
        
        solution += "\\end{itemize}\n"
        solution += f"Decimal value : ${abs_decimal}_{{10}}$\n"
        
        # Step 4: Apply negative sign
        solution += f"\\item Apply the negative sign to the result: "
        solution += f"$-{abs_decimal}_{{10}}$\n\\end{{itemize}}\n"
    
    # Final answer
    solution += f"\\begin{{center}}\nFinal answer: The binary number ${binary_num}_2$ in Two's Complement representation is ${decimal_value}_{{10}}$\n\\end{{center}}\n"
    solution += "\\end{enumerate}"
    
    return solution

def get_excess128_re_solution(binary_num):
    # Get the decimal value
    decimal_value = excess128_binary_to_decimal(binary_num)
    
    # Build the solution with LaTeX formatting
    solution = "\\begin{enumerate}\n"
    
    # Step 1: Explain the Excess-128 format
    solution += f"\\item Explain the Excess-128 format: "
    solution += f"In Excess-128 format, the decimal value is calculated by converting the binary number to decimal, then subtracting 128 (the bias).\n"
    
    # Step 2: Convert binary to decimal
    solution += f"\\item Convert the binary number ${binary_num}_2$ to decimal:\n\\begin{{itemize}}\n"
    
    # Calculate the decimal value without subtracting the bias
    biased_decimal = 0
    for i, bit in enumerate(binary_num):
        position = len(binary_num) - i - 1
        if bit == '1':
            value = 2 ** position
            biased_decimal += value
            solution += f"\\item Bit ${bit}$ at position ${position}$ contributes $2^{{{position}}} = {value}$\n"
        else:
            solution += f"\\item Bit ${bit}$ at position ${position}$ contributes $0$\n"
    
    solution += "\\end{itemize}\n"
    solution += f"Decimal value before subtracting bias: ${biased_decimal}_{{10}}$\n"
    
    # Step 3: Subtract the bias
    solution += f"\\item Subtract the bias (128) to get the actual value: "
    solution += f"${biased_decimal}_{{10}} - 128 = {biased_decimal - 128}_{{10}}$\n"
    
    # Final answer
    solution += f"\\begin{{center}}\nFinal answer: The binary number ${binary_num}_2$ in Excess-128 representation is ${decimal_value}_{{10}}$\n\\end{{center}}\n"
    solution += "\\end{enumerate}"
    
    return solution

# Đảm bảo thêm các hàm cần thiết để tính toán giá trị thập phân
def signedmagnitude_binary_to_decimal(binary_num):
    if binary_num[0] == '0':
        # Positive number
        return int(binary_num[1:], 2)
    else:
        # Negative number
        return -int(binary_num[1:], 2)

def onescomplement_binary_to_decimal(binary_num):
    if binary_num[0] == '0':
        # Positive number
        return int(binary_num, 2)
    else:
        # Negative number
        # Invert all bits
        inverted = ''.join('1' if bit == '0' else '0' for bit in binary_num)
        return -int(inverted, 2)

def twoscomplement_binary_to_decimal(binary_num):
    if binary_num[0] == '0':
        # Positive number
        return int(binary_num, 2)
    else:
        # Negative number
        # Find two's complement
        inverted = ''.join('1' if bit == '0' else '0' for bit in binary_num)
        return -(int(inverted, 2) + 1)

def excess128_binary_to_decimal(binary_num):
    # Convert binary to decimal and subtract the bias
    return int(binary_num, 2) - 128 