def get_signed_magnitude_solution(decimal_num, bit_length):
    # Calculate valid range for n-bit signed magnitude
    max_val = 2 ** (bit_length - 1) - 1
    min_val = -(2 ** (bit_length - 1) - 1)
    
    # Check if the number can be represented in the given bit length
    if decimal_num > max_val or decimal_num < min_val:
        return f"Overflow: Cannot represent {decimal_num} in {bit_length}-bit Signed Magnitude. Valid range is [$-2^{{8-1}} - 1$, $2^{{8-1}} - 1$] or [{min_val}, {max_val}]."
    
    # Determine the sign of the decimal number
    if decimal_num < 0:
        sign_bit = 1
        abs_value = abs(decimal_num)
    else:
        sign_bit = 0
        abs_value = decimal_num
    
    # Convert the absolute value to binary
    abs_binary = bin(abs_value)[2:]
    
    # Determine how many bits are needed for the magnitude part
    magnitude_bits = bit_length - 1
    
    # Check if the magnitude can be represented in the allocated bits
    if len(abs_binary) > magnitude_bits:
        overflow_msg = f"Overflow: Cannot represent {decimal_num} in {bit_length}-bit Signed Magnitude."
        return overflow_msg
    
    # Pad the binary number with zeros to match the required length
    padded_abs_binary = abs_binary.zfill(magnitude_bits)
    
    # Create the signed magnitude representation
    signed_magnitude_binary = str(sign_bit) + padded_abs_binary
    
    # Build the solution steps with LaTeX formatting
    solution = "\\begin{enumerate}\n"
    
    # Step 1: Check if the number is within the valid range
    solution += f"\\item Check if the decimal number ${decimal_num}_{{10}}$ is within the valid range for {bit_length}-bit Signed Magnitude representation:\n\\begin{{itemize}}\n"
    solution += f"\\item Valid range: $[{min_val}, {max_val}]$\n"
    solution += f"\\item Since ${min_val} \\leq {decimal_num} \\leq {max_val}$, the number can be represented in {bit_length}-bit Signed Magnitude format.\n\\end{{itemize}}\n"
    
    # Step 2: Determine sign
    solution += f"\\item Determine the sign of the decimal number ${decimal_num}_{{10}}$: "
    if decimal_num < 0:
        solution += f"Since ${decimal_num} < 0$, the sign bit is 1 (negative).\n"
        # Step 3: Find absolute value
        solution += f"\\item Find the absolute value of the decimal number: "
        solution += f"$|{decimal_num}| = {abs_value}$\n"
    else:
        solution += f"Since ${decimal_num} \\geq 0$, the sign bit is 0 (positive).\n"
    
    # Step 4: Convert to binary
    solution += f"\\item Convert the absolute value ${abs_value}_{{10}}$ to binary:\n\\begin{{itemize}}\n"
    
    # Binary conversion steps
    conversion_steps = []
    quotient = abs_value
    
    if quotient == 0:
        conversion_steps.append(f"\\item Divide ${quotient}$ by $2$ = $0$ remainder $0$")
    
    while quotient > 0:
        remainder = quotient % 2
        quotient = quotient // 2
        conversion_steps.append(f"\\item Divide ${int(quotient*2+remainder)}$ by $2$ = ${quotient}$ remainder ${remainder}$")
    
    # We need to reverse the display of the steps to show them in correct order
    # for step in reversed(conversion_steps):
    #     solution += step + "\n"
    for step in (conversion_steps):
        solution += step + "\n"
    
    solution += "\\end{itemize}\n"
    
    # Step 5: Show the binary result
    solution += f"\\item Binary conversion result: ${abs_value}_{{10}} = {abs_binary}_2$\n"
    
    # Step 6: Pad with zeros if necessary
    if len(abs_binary) < magnitude_bits:
        solution += f"\\item Add leading zeros to reach a magnitude part length of {magnitude_bits} bits: "
        solution += f"${abs_binary}_2 \\rightarrow {padded_abs_binary}_2$\n"
    
    # Step 7: Add the sign bit
    solution += f"\\item Prepend the sign bit to form the {bit_length}-bit Signed Magnitude representation: "
    solution += f"${sign_bit}{padded_abs_binary}_2$\n"
    
    # Final answer
    solution += f"\\begin{{center}}\nFinal answer: The {bit_length}-bit Signed Magnitude representation of ${decimal_num}_{{10}}$ is ${signed_magnitude_binary}_2$\n\\end{{center}}\n"
    solution += "\\end{enumerate}"
    
    return solution

def get_ones_complement_solution(decimal_num, bit_length):
    # First check if the number can be represented in one's complement
    max_val = 2 ** (bit_length - 1) - 1
    min_val = -(2 ** (bit_length - 1) - 1)
    
    if decimal_num > max_val or decimal_num < min_val:
        return f"Overflow: Cannot represent {decimal_num} in {bit_length}-bit One's Complement. Valid range is [$-2^{{8-1}} - 1$, $2^{{8-1}} - 1$] or [{min_val}, {max_val}]."
    
    # Build the solution steps with LaTeX formatting
    solution = "\\begin{enumerate}\n"
    
    # Step 1: Check if the number is within the valid range
    solution += f"\\item Check if the decimal number ${decimal_num}_{{10}}$ is within the valid range for {bit_length}-bit One's Complement representation:\n\\begin{{itemize}}"
    solution += f"\\item Valid range: $[{min_val}, {max_val}]$\n"
    solution += f"\\item Since ${min_val} \\leq {decimal_num} \\leq {max_val}$, the number can be represented in {bit_length}-bit One's Complement format.\n\\end{{itemize}}"
    
    # Step 2: Determine sign
    solution += f"\\item Determine the sign of the decimal number ${decimal_num}_{{10}}$: "
    
    if decimal_num < 0:
        sign_bit = 1
        abs_value = abs(decimal_num)
        solution += f"Since ${decimal_num} < 0$, the sign bit is 1 (negative).\n"
            # Step 3: Find absolute value and convert to binary
        solution += f"\\item Find the absolute value and convert to binary: "
        solution += f"$|{decimal_num}| = {abs_value}$\n"
    else:
        sign_bit = 0
        abs_value = decimal_num
        solution += f"Since ${decimal_num} \\geq 0$, the sign bit is 0 (positive).\n"
    
    # Step 4: Binary conversion steps
    solution += f"\\item Convert ${abs_value}_{{10}}$ to binary:\n\\begin{{itemize}}\n"
    
    # Generate division steps
    conversion_steps = []
    quotient = abs_value
    
    if quotient == 0:
        conversion_steps.append(f"\\item Divide ${quotient}$ by $2$ = $0$ remainder $0$")
    
    while quotient > 0:
        remainder = quotient % 2
        quotient = quotient // 2
        conversion_steps.append(f"\\item Divide ${int(quotient*2+remainder)}$ by $2$ = ${quotient}$ remainder ${remainder}$")
    
    # Reverse to display in correct order
    # for step in reversed(conversion_steps):
    #     solution += step + "\n"
    for step in (conversion_steps):
        solution += step + "\n"
    
    solution += "\\end{itemize}\n"
    
    # Get the binary representation of the absolute value
    abs_binary = bin(abs_value)[2:]
    
    # Step 5: Pad with zeros
    magnitude_bits = bit_length - 1
    padded_abs_binary = abs_binary.zfill(magnitude_bits)
    
    solution += f"Binary value: ${abs_binary}_2$\n"
    
    if len(abs_binary) < magnitude_bits:
        solution += f"\\item Add leading zeros to reach a value part length of {magnitude_bits} bits: "
        solution += f"${abs_binary}_2 \\rightarrow {padded_abs_binary}_2$\n"
    
    # Step 6: Form the binary representation based on sign
    if decimal_num >= 0:
        # For positive numbers, add 0 as sign bit
        result_binary = '0' + padded_abs_binary
        solution += f"\\item Since this is a positive number, the sign bit is 0. One's Complement representation is: "
        solution += f"${result_binary}_2$\n"
    else:
        # For negative numbers, add 1 as sign bit and invert all bits after the sign bit
        # First create binary with sign bit
        temp_binary = '1' + padded_abs_binary
        
        # Then invert all bits after the sign bit (all magnitude bits)
        solution += f"\\item Since this is a negative number, we need to follow these steps to find the One's Complement representation:\n\\begin{{itemize}}\n"
        solution += f"\\item Prepend sign bit 1: $1{padded_abs_binary}_2$\n"
        solution += f"\\item Invert all bits after the sign bit: "
        
        # Invert the magnitude bits
        inverted_magnitude = ''
        for bit in padded_abs_binary:
            inverted_bit = '1' if bit == '0' else '0'
            inverted_magnitude += inverted_bit
        
        solution += f"${padded_abs_binary}_2 \\rightarrow {inverted_magnitude}_2$\n"
        
        result_binary = '1' + inverted_magnitude
        solution += f"\\item Result after inversion: ${result_binary}_2$\n"
        solution += "\\end{itemize}\n"
    
    # Final answer
    solution += f"\\begin{{center}}\nFinal answer: The {bit_length}-bit One's Complement representation of ${decimal_num}_{{10}}$ is ${result_binary}_2$\n\\end{{center}}\n"
    solution += "\\end{enumerate}"
    
    return solution

def get_twos_complement_solution(decimal_num, bit_length):
    # First check if the number can be represented in two's complement
    max_val = 2 ** (bit_length - 1) - 1
    min_val = -(2 ** (bit_length - 1))
    
    if decimal_num > max_val or decimal_num < min_val:
        return f"Overflow: Cannot represent {decimal_num} in {bit_length}-bit Two's Complement. Valid range is [$-2^{{8-1}}$, $2^{{8-1}} - 1$] or [{min_val}, {max_val}]."
    
    # Build the solution steps with LaTeX formatting
    solution = "\\begin{enumerate}\n"
    
    # Step 1: Check if the number is within the valid range
    solution += f"\\item Check if the decimal number ${decimal_num}_{{10}}$ is within the valid range for {bit_length}-bit Two's Complement representation:\n\\begin{{itemize}}\n"
    solution += f"\\item Valid range: $[{min_val}, {max_val}]$\n"
    solution += f"\\item Since ${min_val} \\leq {decimal_num} \\leq {max_val}$, the number can be represented in {bit_length}-bit Two's Complement format.\n\\end{{itemize}}\n"
    
    # Step 2: Determine sign
    solution += f"\\item Determine the sign of the decimal number ${decimal_num}_{{10}}$: "
    
    if decimal_num < 0:
        sign_bit = 1
        abs_value = abs(decimal_num)
        solution += f"Since ${decimal_num} < 0$, the sign bit is 1 (negative).\n"
            # Step 3: Find absolute value and convert to binary
        solution += f"\\item Find the absolute value and convert to binary: "
        solution += f"$|{decimal_num}| = {abs_value}$\n"
    else:
        sign_bit = 0
        abs_value = decimal_num
        solution += f"Since ${decimal_num} \\geq 0$, the sign bit is 0 (positive).\n"
    

    
    # Step 4: Binary conversion steps
    solution += f"\\item Convert ${abs_value}_{{10}}$ to binary:\n\\begin{{itemize}}\n"
    
    # Generate division steps
    conversion_steps = []
    quotient = abs_value
    
    if quotient == 0:
        conversion_steps.append(f"\\item Divide ${quotient}$ by $2$ = $0$ remainder $0$")
    
    while quotient > 0:
        remainder = quotient % 2
        quotient = quotient // 2
        conversion_steps.append(f"\\item Divide ${int(quotient*2+remainder)}$ by $2$ = ${quotient}$ remainder ${remainder}$")
    
    # Reverse to display in correct order
    for step in (conversion_steps):
        solution += step + "\n"
    
    solution += "\\end{itemize}\n"
    
    # Get the binary representation of the absolute value
    abs_binary = bin(abs_value)[2:]
    
    # Step 5: Pad with zeros if needed
    magnitude_bits = bit_length - 1
    padded_abs_binary = abs_binary.zfill(magnitude_bits)
    
    solution += f"Binary value: ${abs_binary}_2$\n"
    
    if len(abs_binary) < magnitude_bits:
        solution += f"\\item Add leading zeros to reach a binary representation length of {magnitude_bits} bits: "
        solution += f"${abs_binary}_2 \\rightarrow {padded_abs_binary}_2$\n"
    
    # Step 6: Form the binary representation based on sign
    if decimal_num >= 0:
        # For positive numbers, simply add 0 as sign bit
        result_binary = '0' + padded_abs_binary
        solution += f"\\item Since this is a positive number, the sign bit is 0. Two's Complement representation is: "
        solution += f"${result_binary}_2$\n"
    else:
        # For negative numbers, we need to:
        # 1. Add 0 as sign bit to the magnitude
        # 2. Invert all bits
        # 3. Add 1 to the result
        solution += f"\\item Since this is a negative number, we need to follow these steps to find the Two's Complement representation:\n\\begin{{itemize}}\n"
        solution += f"\\item Prepend sign bit 0 (temporarily): $0{padded_abs_binary}_2$\n"
        
        # Invert all bits
        inverted_binary = ''
        for bit in '0' + padded_abs_binary:
            inverted_bit = '1' if bit == '0' else '0'
            inverted_binary += inverted_bit
        
        solution += f"\\item Invert all bits (get One's Complement): ${('0' + padded_abs_binary)}_2 \\rightarrow {inverted_binary}_2$\n"
        
        # Add 1 to the inverted binary
        inverted_dec = int(inverted_binary, 2)
        twos_complement_dec = inverted_dec + 1
        twos_complement_bin = bin(twos_complement_dec)[2:].zfill(bit_length)
        
        solution += f"\\item Add 1 to the result (get Two's Complement): ${inverted_binary}_2 + 1 = {twos_complement_bin}_2$\n"
        solution += "\\end{itemize}\n"
        
        result_binary = twos_complement_bin
    
    # Final answer
    solution += f"\\begin{{center}}\nFinal answer: The {bit_length}-bit Two's Complement representation of ${decimal_num}_{{10}}$ is ${result_binary}_2$\n\\end{{center}}\n"
    solution += "\\end{enumerate}"
    
    return solution

def get_excess_128_solution(decimal_num, bit_length):
    # Check if the number can be represented in the excess-128 format
    # For 8-bit excess-128, range is -128 to +127
    max_val = 2 ** (bit_length - 1) - 1
    min_val = -(2 ** (bit_length - 1))
    
    if decimal_num > max_val or decimal_num < min_val:
        return f"Overflow: Cannot represent {decimal_num} in {bit_length}-bit Excess-128 format. Valid range is [{min_val}, {max_val}]."
    
    # Add the bias (128) to the decimal number
    biased_value = decimal_num + 128
    
    # Convert the biased value to binary
    biased_binary = bin(biased_value)[2:].zfill(bit_length)
    
    # Build the solution with LaTeX formatting
    solution = "\\begin{enumerate}\n"
    
    # Step 1: Check if the number is within the valid range
    solution += f"\\item Check if the decimal number ${decimal_num}_{{10}}$ is within the valid range for {bit_length}-bit Excess-128 representation:\n\\begin{{itemize}}"
    solution += f"\\item Valid range: $[{min_val}, {max_val}]$\n"
    solution += f"\\item Since ${min_val} \\leq {decimal_num} \\leq {max_val}$, the number can be represented in {bit_length}-bit Excess-128 format.\n\\end{{itemize}}"
    
    # Step 2: Explain the format
    solution += f"\\item Understanding the Excess-128 format (for {bit_length}-bit representation): "
    solution += f"In Excess-128 format, we add 128 to the decimal value before converting to binary.\n"
    
    # Step 3: Add the bias
    solution += f"\\item Add 128 to the decimal value ${decimal_num}_{{10}}$: "
    solution += f"${decimal_num} + 128 = {biased_value}$\n"
    
    # Step 4: Convert to binary
    solution += f"\\item Convert ${biased_value}_{{10}}$ to binary:\n\\begin{{itemize}}\n"
    
    # Generate division steps
    conversion_steps = []
    quotient = biased_value
    
    if quotient == 0:
        conversion_steps.append(f"\\item Divide ${quotient}$ by $2$ = $0$ remainder $0$")
    
    while quotient > 0:
        remainder = quotient % 2
        quotient = quotient // 2
        conversion_steps.append(f"\\item Divide ${int(quotient*2+remainder)}$ by $2$ = ${quotient}$ remainder ${remainder}$")
    
    # Reverse to display in correct order
    for step in (conversion_steps):
        solution += step + "\n"
    
    solution += "\\end{itemize}\n"
    
    # Get the raw binary representation
    raw_binary = bin(biased_value)[2:]
    
    # Step 5: Pad with zeros if needed
    if len(raw_binary) < bit_length:
        solution += f"\\item Add leading zeros to reach a binary representation length of {bit_length} bits: "
        solution += f"${raw_binary}_2 \\rightarrow {biased_binary}_2$\n"
    else:
        solution += f"Binary value: ${biased_binary}_2$\n"
    
    # Final answer
    solution += f"\\begin{{center}}\nFinal answer: The {bit_length}-bit Excess-128 representation of ${decimal_num}_{{10}}$ is ${biased_binary}_2$\n\\end{{center}}\n"
    solution += "\\end{enumerate}"
    
    return solution 