import csv
import os
import random
import re
import argparse
from .decimal_to_binary import signedMagnitude, onesComplement, twosComplement
from .binary_to_decimal import signedMagnitude_re, onesComplement_re, twosComplement_re
from .solutions.d2b_solutions import (
    get_signed_magnitude_solution,
    get_ones_complement_solution,
    get_twos_complement_solution,
)
from .solutions.b2d_solutions import (
    get_signedmagnitude_re_solution,
    get_onescomplement_re_solution,
    get_twoscomplement_re_solution,
)


def save_to_excel(input_data, solution, output, filename="binary_conversion_results.csv"):
    """
    Save results to a CSV file instead of Excel to avoid dependency on pandas
    """
    # Data to save
    new_data = [input_data, solution, output]
    
    # Check if the file already exists
    file_exists = os.path.isfile(filename)
    
    # Open file for writing (append mode if file already exists)
    mode = 'a' if file_exists else 'w'
    with open(filename, mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header if new file
        if not file_exists:
            writer.writerow(['input', 'solution', 'output'])
        
        # Write new data
        writer.writerow(new_data)
    
    print(f"Results have been saved to {filename}")


def extract_binary_result(solution):
    """
    Extract the binary result from a solution string.
    Returns only the binary representation without the explanation steps.
    """
    # If there was an overflow error, return None
    if "Overflow" in solution:
        return None
    
    # Try to find the binary result using regex patterns
    # The pattern looks for the final binary result in the center section
    match = re.search(r"\\begin{center}\s*The \d+-bit .+ representation of .+ is \$([01]+)_2\\$", solution)
    if match:
        return match.group(1)
    
    return None


def auto_generate_dataset(count=100, bit_length=8, type_filter=None, filename="auto_generated_dataset.csv"):
    """
    Automatically generate a dataset of decimal to binary conversions
    
    Args:
        count (int): Number of samples to generate
        bit_length (int): Bit length to use for conversions
        type_filter (str, optional): If specified, only generate examples for this conversion type ('s', '1', '2')
        filename (str): Output CSV filename
    """
    # Define valid ranges for each representation
    sm_max = 2 ** (bit_length - 1) - 1
    sm_min = -(2 ** (bit_length - 1) - 1)
    
    oc_max = 2 ** (bit_length - 1) - 1
    oc_min = -(2 ** (bit_length - 1) - 1)
    
    tc_max = 2 ** (bit_length - 1) - 1
    tc_min = -(2 ** (bit_length - 1))
    
    # Set of conversion types
    conversion_types = ['s', '1', '2'] if type_filter is None else [type_filter]
    
    # To avoid duplicates, keep track of already generated samples
    generated_samples = set()
    
    print(f"Generating {count} unique samples with {bit_length}-bit length for D2B...")
    generated_count = 0
    attempts = 0
    max_attempts = count * 10  # Avoid infinite loop if almost all possible values are used
    
    # Ensure header is written if file is new or empty
    if not os.path.isfile(filename) or os.path.getsize(filename) == 0:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['input', 'solution', 'output'])

    while generated_count < count and attempts < max_attempts:
        # Randomly select conversion type
        conv_type = random.choice(conversion_types)
        
        # Generate a decimal number within valid range for the conversion type
        if conv_type == 's':  # Signed Magnitude
            decimal_num = random.randint(sm_min, sm_max)
        elif conv_type == '1':  # 1's Complement
            decimal_num = random.randint(oc_min, oc_max)
        elif conv_type == '2':  # 2's Complement
            decimal_num = random.randint(tc_min, tc_max)
        
        # Create a unique key for this sample to check duplicates
        sample_key = f"{conv_type}_{decimal_num}_{bit_length}" # Add bit_length to key for uniqueness
        
        # Skip if this sample was already generated
        if sample_key in generated_samples:
            attempts += 1
            continue
        
        # Add to set of generated samples
        generated_samples.add(sample_key)
        
        # Generate solution and result
        if conv_type == 's':
            solution = get_signed_magnitude_solution(decimal_num, bit_length)
            input_desc = f"Convert {decimal_num} to {bit_length}-bit signed magnitude or indicate overflow."
        elif conv_type == '1':
            solution = get_ones_complement_solution(decimal_num, bit_length)
            input_desc = f"Convert {decimal_num} to {bit_length}-bit ones' complement or indicate overflow."
        elif conv_type == '2':
            solution = get_twos_complement_solution(decimal_num, bit_length)
            input_desc = f"Convert {decimal_num} to {bit_length}-bit two's complement or indicate overflow."
        
        # Extract the binary result or handle overflow
        binary_result = extract_binary_result(solution)
        if binary_result:
            formatted_result = f"${binary_result}_2$"
        else:
            formatted_result = "Overflow"
        
        # Save the generated data (using append mode directly in save_to_excel)
        save_to_excel(input_desc, solution, formatted_result, filename)
        
        # Increment counter
        generated_count += 1
        
        # Show progress
        if generated_count % 10 == 0 or generated_count == count:
            print(f"Generated {generated_count}/{count} D2B samples...")
    
    if attempts >= max_attempts and generated_count < count:
        print(f"Warning: Could only generate {generated_count} unique D2B samples after maximum attempts.")
    
    print(f"D2B dataset generation complete. {generated_count} samples saved to {filename}")


def auto_generate_binary_to_decimal(count=50, bit_length=8, type_filter=None, filename="b2d_dataset.csv"):
    """
    Automatically generate binary to decimal conversion examples
    
    Args:
        count (int): Number of samples to generate
        bit_length (int): Bit length of binary numbers to generate
        type_filter (str, optional): If specified, only generate examples for this conversion type ('s', '1', '2')
        filename (str): Output CSV filename
    """
    # Set of conversion types
    conversion_types = ['s', '1', '2'] if type_filter is None else [type_filter]
    
    # To avoid duplicates, keep track of already generated samples
    generated_samples = set()
    
    print(f"Generating {count} unique binary to decimal samples with {bit_length}-bit length...")
    generated_count = 0
    attempts = 0
    max_attempts = count * 10  # Avoid infinite loop

    # Ensure header is written if file is new or empty
    if not os.path.isfile(filename) or os.path.getsize(filename) == 0:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['input', 'solution', 'output'])
            
    while generated_count < count and attempts < max_attempts:
        # Randomly select conversion type
        conv_type = random.choice(conversion_types)
        
        # Generate a valid binary number of specified bit_length
        binary_num = ''.join(random.choice(['0', '1']) for _ in range(bit_length))
        
        # Create a unique key for this sample
        sample_key = f"{conv_type}_{binary_num}" # bit_length is implicit in binary_num
        
        # Skip if this sample was already generated
        if sample_key in generated_samples:
            attempts += 1
            continue
        
        # Add to set of generated samples
        generated_samples.add(sample_key)
        
        # Generate solution and result
        if conv_type == 's':
            solution = get_signedmagnitude_re_solution(binary_num)
            result = signedMagnitude_re(binary_num)
            input_desc = f"Convert {binary_num} ({bit_length}-bit) from signed magnitude to decimal"
        elif conv_type == '1':
            solution = get_onescomplement_re_solution(binary_num)
            result = onesComplement_re(binary_num)
            input_desc = f"Convert {binary_num} ({bit_length}-bit) from ones' complement to decimal"
        elif conv_type == '2':
            solution = get_twoscomplement_re_solution(binary_num)
            result = twosComplement_re(binary_num)
            input_desc = f"Convert {binary_num} ({bit_length}-bit) from two's complement to decimal"
        
        # Format the result
        formatted_result = f"${result}_{{10}}$"
        
        # Save the generated data
        save_to_excel(input_desc, solution, formatted_result, filename)
        
        # Increment counter
        generated_count += 1
        
        # Show progress
        if generated_count % 10 == 0 or generated_count == count:
            print(f"Generated {generated_count}/{count} B2D samples...")
    
    if attempts >= max_attempts and generated_count < count:
        print(f"Warning: Could only generate {generated_count} unique B2D samples after maximum attempts.")
    
    print(f"Binary to decimal dataset generation complete. {generated_count} samples saved to {filename}")


def auto_generate_overflow_dataset(count=10, bit_length=8, filename="overflow_cases_dataset.csv"):
    """
    Generate a dataset focusing only on overflow cases for each representation
    
    Args:
        count (int): Number of unique overflow cases to generate for each representation type
        bit_length (int): Bit length to use for conversions
        filename (str): Output CSV filename
    """
    # Define valid ranges for each representation
    sm_max = 2 ** (bit_length - 1) - 1
    sm_min = -(2 ** (bit_length - 1) - 1)
    
    oc_max = 2 ** (bit_length - 1) - 1 # Same as SM
    oc_min = -(2 ** (bit_length - 1) - 1) # Same as SM
    
    tc_max = 2 ** (bit_length - 1) - 1
    tc_min = -(2 ** (bit_length - 1))
    
    # Track generated samples to avoid duplicates
    generated_samples = set()
    
    # Conversion types
    conversion_types = ['s', '1', '2']
    
    print(f"Generating {count} unique overflow test cases per representation type with {bit_length}-bit length...")
    generated_count_total = 0
    # total_target = count * len(conversion_types)

    # Ensure header is written if file is new or empty
    if not os.path.isfile(filename) or os.path.getsize(filename) == 0:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['input', 'solution', 'output'])

    for conv_type in conversion_types:
        type_generated_count = 0
        attempts = 0
        max_attempts_per_type = count * 20 # Allow more attempts for specific overflow cases

        # Determine overflow boundaries for the current type
        if conv_type == 's':
            max_val, min_val = sm_max, sm_min
        elif conv_type == '1':
            max_val, min_val = oc_max, oc_min
        elif conv_type == '2':
            max_val, min_val = tc_max, tc_min
        
        # Specific boundary overflow values to try first
        # (These are more likely to be distinct and relevant)
        specific_overflows = [max_val + 1, min_val - 1]
        if bit_length == 8 and conv_type == '2': # Special case for 8-bit 2's complement
             # -128 is NOT an overflow for 8-bit 2's complement.
             # min_val -1 would be -129, which is an overflow.
             pass
        else:
            # For other cases, or if min_val is not the absolute minimum (like -128 for 2's comp)
            # adding tc_min -1 can be useful.
            pass


        for decimal_num in specific_overflows:
            if type_generated_count >= count: break

            sample_key = f"{conv_type}_{decimal_num}_{bit_length}"
            if sample_key in generated_samples: continue
            
            # Generate solution
            if conv_type == 's':
                solution = get_signed_magnitude_solution(decimal_num, bit_length)
            elif conv_type == '1':
                solution = get_ones_complement_solution(decimal_num, bit_length)
            elif conv_type == '2':
                solution = get_twos_complement_solution(decimal_num, bit_length)
            
            if "Overflow" in solution:
                generated_samples.add(sample_key)
                input_desc = f"Convert {decimal_num} to {bit_length}-bit {conv_type}-representation or indicate overflow."
                save_to_excel(input_desc, solution, "Overflow", filename)
                type_generated_count += 1
                generated_count_total +=1

        # Random generation for remaining count
        while type_generated_count < count and attempts < max_attempts_per_type:
            attempts += 1
            # Generate a random overflow value (positive or negative side)
            if random.choice([True, False]): # Positive overflow
                decimal_num = max_val + random.randint(1, 2**(bit_length-1)) # Go beyond max
            else: # Negative overflow
                decimal_num = min_val - random.randint(1, 2**(bit_length-1)) # Go beyond min

            sample_key = f"{conv_type}_{decimal_num}_{bit_length}"
            if sample_key in generated_samples: continue

            # Skip -128 for 8-bit two's complement if it's accidentally generated here as "overflow" target
            if bit_length == 8 and conv_type == '2' and decimal_num == -128:
                continue

            if conv_type == 's':
                solution = get_signed_magnitude_solution(decimal_num, bit_length)
            elif conv_type == '1':
                solution = get_ones_complement_solution(decimal_num, bit_length)
            elif conv_type == '2':
                solution = get_twos_complement_solution(decimal_num, bit_length)

            if "Overflow" in solution:
                generated_samples.add(sample_key)
                input_desc = f"Convert {decimal_num} to {bit_length}-bit {conv_type}-representation or indicate overflow."
                save_to_excel(input_desc, solution, "Overflow", filename)
                type_generated_count += 1
                generated_count_total +=1
        
        if type_generated_count < count:
            print(f"Warning: Could only generate {type_generated_count}/{count} unique overflow cases for type '{conv_type}'.")

    print(f"Overflow test dataset generation complete. Generated {generated_count_total} total overflow test cases. Results saved to {filename}")
    
    # Return stats about generated dataset
    return {
        "generated_count": generated_count_total,
        "unique_samples": len(generated_samples),
        "representation_stats": {
            "s": sum(1 for key in generated_samples if key.startswith("s_")),
            "1": sum(1 for key in generated_samples if key.startswith("1_")),
            "2": sum(1 for key in generated_samples if key.startswith("2_")),
        }
    }

# --- Helper functions for argparse commands ---
def handle_manual_conversion(args):
    bit_length = args.bit_length
    output_file = args.output

    # Ensure header is written if file is new or empty (for the first manual conversion to this file)
    if not os.path.isfile(output_file) or os.path.getsize(output_file) == 0:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['input', 'solution', 'output'])

    if args.direction == "d":
        try:
            num = int(args.value)
            # num_str = args.value # Original string value, used by some older functions if needed

            if args.type == "s":
                solution = get_signed_magnitude_solution(num, bit_length)
                input_desc = f"Convert {num} to {bit_length}-bit signed magnitude or indicate overflow."
            elif args.type == "1":
                solution = get_ones_complement_solution(num, bit_length)
                input_desc = f"Convert {num} to {bit_length}-bit ones' complement or indicate overflow."
            elif args.type == "2":
                solution = get_twos_complement_solution(num, bit_length)
                input_desc = f"Convert {num} to {bit_length}-bit two's complement or indicate overflow."
            else: # Should not happen due to choices in argparse
                print(f"Error: Invalid conversion type '{args.type}'.")
                return

            binary_representation = extract_binary_result(solution)
            formatted_result = f"${binary_representation}_2$" if binary_representation else "Overflow"
            save_to_excel(input_desc, solution, formatted_result, filename=output_file)
            print(f"Processed decimal to binary conversion. Results saved to {output_file}")

        except ValueError:
            print(f"Error: Value '{args.value}' is not a valid integer for decimal to binary conversion.")
            return
            
    elif args.direction == "b":
        binary_num_str = args.value
        
        if len(binary_num_str) != bit_length:
            print(f"Warning: Binary string length ({len(binary_num_str)}) does not match bit length ({bit_length}). Result may be unexpected.")
            # Decide if execution should continue or stop. For now, it continues.

        # Basic validation for binary string
        if not all(c in '01' for c in binary_num_str):
            print(f"Error: Value '{binary_num_str}' is not a valid binary string.")
            return

        result_decimal_str = "Error" # Default in case of issues

        if args.type == "s":
            solution = get_signedmagnitude_re_solution(binary_num_str) 
            result_decimal = signedMagnitude_re(binary_num_str)
            result_decimal_str = str(result_decimal)
            input_desc = f"Convert {binary_num_str} ({bit_length}-bit) from signed magnitude to decimal"
        elif args.type == "1":
            solution = get_onescomplement_re_solution(binary_num_str)
            result_decimal = onesComplement_re(binary_num_str)
            result_decimal_str = str(result_decimal)
            input_desc = f"Convert {binary_num_str} ({bit_length}-bit) from ones' complement to decimal"
        elif args.type == "2":
            solution = get_twoscomplement_re_solution(binary_num_str)
            result_decimal = twosComplement_re(binary_num_str)
            result_decimal_str = str(result_decimal)
            input_desc = f"Convert {binary_num_str} ({bit_length}-bit) from two's complement to decimal"
        else: # Should not happen
            print(f"Error: Invalid conversion type '{args.type}'.")
            return
            
        save_to_excel(input_desc, solution, f"${result_decimal_str}_{{10}}$", filename=output_file)
        print(f"Processed binary to decimal conversion. Results saved to {output_file}")
    else: # Should not happen
        print(f"Error: Invalid conversion direction '{args.direction}'.")

def handle_gen_d2b(args):
    auto_generate_dataset(count=args.count, bit_length=args.bit_length, type_filter=args.type_filter, filename=args.output)

def handle_gen_b2d(args):
    auto_generate_binary_to_decimal(count=args.count, bit_length=args.bit_length, type_filter=args.type_filter, filename=args.output)

def handle_gen_overflow(args):
    stats = auto_generate_overflow_dataset(count=args.count, bit_length=args.bit_length, filename=args.output)
    print(f"Overflow test cases dataset statistics:")
    print(f"Total samples generated: {stats['generated_count']}")
    print(f"Overflow cases for signed magnitude: {stats['representation_stats']['s']}")
    print(f"Overflow cases for ones' complement: {stats['representation_stats']['1']}")
    print(f"Overflow cases for two's complement: {stats['representation_stats']['2']}")

def main():
    parser = argparse.ArgumentParser(description="Tool for converting binary numbers.", formatter_class=argparse.RawTextHelpFormatter)
    parser.set_defaults(func=lambda args_lambda: parser.print_help()) # Default action if no subcommand
    subparsers = parser.add_subparsers(dest="command", help="Available commands:", required=False) # Making it not required to show help

    # --- Manual conversion parser ---
    manual_parser = subparsers.add_parser("manual", help="Perform manual conversion.")
    manual_parser.add_argument("--direction", choices=["d", "b"], required=True, help="Direction of conversion (d: Decimal to Binary, b: Binary to Decimal)")
    manual_parser.add_argument("--type", choices=["s", "1", "2"], required=True, help="Conversion type (s: Signed Magnitude, 1: Ones' Complement, 2: Twos' Complement)")
    manual_parser.add_argument("--value", required=True, help="Value to convert (decimal for 'd', binary for 'b')")
    manual_parser.add_argument("--bit-length", type=int, default=8, help="Bit length for conversion (default: 8)")
    manual_parser.add_argument("--output", default="binary_conversion_results.csv", help="Output CSV file name (default: binary_conversion_results.csv)")
    manual_parser.set_defaults(func=handle_manual_conversion)

    # --- Auto-generate decimal to binary dataset parser ---
    d2b_parser = subparsers.add_parser("gen-d2b", help="Auto-generate decimal to binary dataset.")
    d2b_parser.add_argument("--count", type=int, default=100, help="Number of samples to generate (default: 100)")
    d2b_parser.add_argument("--bit-length", type=int, default=8, help="Bit length for conversion (default: 8)")
    d2b_parser.add_argument("--type-filter", choices=["s", "1", "2"], default=None, help="Filter by specific type (s/1/2) or all if empty.")
    d2b_parser.add_argument("--output", default="auto_d2b_dataset.csv", help="Output CSV file name (default: auto_d2b_dataset.csv)")
    d2b_parser.set_defaults(func=handle_gen_d2b)

    # --- Auto-generate binary to decimal dataset parser ---
    b2d_parser = subparsers.add_parser("gen-b2d", help="Auto-generate binary to decimal dataset.")
    b2d_parser.add_argument("--count", type=int, default=50, help="Number of samples to generate (default: 50)")
    b2d_parser.add_argument("--bit-length", type=int, default=8, help="Bit length for conversion (default: 8)")
    b2d_parser.add_argument("--type-filter", choices=["s", "1", "2"], default=None, help="Filter by specific type (s/1/2) or all if empty.")
    b2d_parser.add_argument("--output", default="auto_b2d_dataset.csv", help="Output CSV file name (default: auto_b2d_dataset.csv)")
    b2d_parser.set_defaults(func=handle_gen_b2d)

    # --- Generate overflow test cases dataset parser ---
    overflow_parser = subparsers.add_parser("gen-overflow", help="Generate overflow test cases dataset.")
    overflow_parser.add_argument("--count", type=int, default=10, help="Number of overflow test cases per type (default: 10)")
    overflow_parser.add_argument("--bit-length", type=int, default=8, help="Bit length for conversion (default: 8)")
    overflow_parser.add_argument("--output", default="overflow_cases.csv", help="Output CSV file name (default: overflow_cases.csv)")
    overflow_parser.set_defaults(func=handle_gen_overflow)
    
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        # This case should be hit if no subcommand is given, and 'required=False' for subparsers.
        # It will print help due to parser.set_defaults.
        # If 'required=True' for subparsers, argparse handles it.
        parser.print_help()


if __name__ == "__main__":
    main() 