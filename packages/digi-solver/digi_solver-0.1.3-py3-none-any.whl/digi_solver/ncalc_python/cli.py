import argparse
from .config import ALL_FORMATS, ASCII, BINARY, DECIMAL, HEXADECIMAL, OCTAL # Added OCTAL
from .utils import get_format_from_string
from .conversions import (
    decimal_to_binary, binary_to_decimal, 
    decimal_to_hexadecimal, hexadecimal_to_decimal,
    decimal_to_octal, octal_to_decimal,
    hexadecimal_to_binary, binary_to_hexadecimal,
    octal_to_binary, binary_to_octal,
    hexadecimal_to_octal, octal_to_hexadecimal
)
from .step_generator import (
    decimal_to_binary_steps, binary_to_decimal_steps,
    decimal_to_hexadecimal_steps, hexadecimal_to_decimal_steps,
    decimal_to_binary_steps_latex, binary_to_decimal_steps_latex,
    decimal_to_hexadecimal_steps_latex, hexadecimal_to_decimal_steps_latex,
    decimal_to_octal_steps, octal_to_decimal_steps,
    decimal_to_octal_steps_latex, octal_to_decimal_steps_latex,
    hexadecimal_to_binary_steps, binary_to_hexadecimal_steps,
    hexadecimal_to_binary_steps_latex, binary_to_hexadecimal_steps_latex,
    octal_to_binary_steps, binary_to_octal_steps,
    octal_to_binary_steps_latex, binary_to_octal_steps_latex,
    hexadecimal_to_octal_steps, hexadecimal_to_octal_steps_latex,
    octal_to_hexadecimal_steps, octal_to_hexadecimal_steps_latex
)
from .file_processor import process_file_input, write_results_to_csv # Added write_results_to_csv

# --- Conversion Execution and Data Collection Logic ---
def execute_conversion_and_get_data(value_to_convert, effective_input_format, formats_to_output, show_steps, use_latex, conversion_map_dict, cli_output_format_is_all):
    """
    Handles the actual conversion, collects data for CSV, and optionally prints to console.
    Returns a list of dictionaries, where each dictionary is a row for the CSV.
    """
    if not effective_input_format:
        print(f"Error: Input format for '{value_to_convert}' is unknown or not specified correctly.")
        return []

    print(f"Input: {value_to_convert} (as {effective_input_format})")
    print("---")
    
    conversion_results_data = []

    for out_fmt in formats_to_output:
        current_result_data = {
            "Input Value": value_to_convert,
            "Input Base": effective_input_format,
            "Requested Output Base": out_fmt,
            "Actual Output Value": "",
            "Steps": ""
        }

        if effective_input_format == out_fmt:
            current_result_data["Actual Output Value"] = value_to_convert
            if cli_output_format_is_all or len(formats_to_output) == 1:
                 print(f"{out_fmt.capitalize()}: {value_to_convert}")
            conversion_results_data.append(current_result_data)
            continue

        conversion_key = (effective_input_format, out_fmt)
        if conversion_key in conversion_map_dict:
            convert_func, steps_funcs_tuple = conversion_map_dict[conversion_key]
            plain_steps_func, latex_steps_func = steps_funcs_tuple # Unpack the tuple

            if show_steps:
                steps_text_or_latex = ""
                result_value = ""
                if use_latex and latex_steps_func:
                    steps_text_or_latex, result_value = latex_steps_func(value_to_convert)
                    # For LaTeX, we typically want to print the raw LaTeX if displaying steps.
                    # The CSV will store this raw LaTeX.
                    print(f"Conversion to {out_fmt.capitalize()} (LaTeX Steps):")
                    print(steps_text_or_latex) # Print raw LaTeX
                    if result_value is None and not ("Error:" in steps_text_or_latex if isinstance(steps_text_or_latex, str) else False):
                        print(f"Error during LaTeX step-by-step conversion of '{value_to_convert}' to {out_fmt}")
                    print("---")
                elif plain_steps_func: # Default to plain text steps if not latex or latex_func not available
                    steps_list, result_value = plain_steps_func(value_to_convert)
                    steps_text_or_latex = "\n".join(steps_list)
                    print(f"Conversion to {out_fmt.capitalize()} (Steps):")
                    for step_line in steps_list:
                        print(step_line)
                    if result_value is None and not any("Error:" in s for s in steps_list):
                        print(f"Error during step-by-step conversion of '{value_to_convert}' to {out_fmt}")
                    print("---")
                
                current_result_data["Actual Output Value"] = result_value if result_value is not None else "Error in steps"
                current_result_data["Steps"] = steps_text_or_latex

            else: # No steps requested
                result_value = convert_func(value_to_convert)
                current_result_data["Actual Output Value"] = result_value
                current_result_data["Steps"] = "" # No steps
                if isinstance(result_value, str) and "Error:" in result_value:
                    print(f"{out_fmt.capitalize()}: {result_value}")
                else:
                    print(f"{out_fmt.capitalize()}: {result_value}")
            
            conversion_results_data.append(current_result_data)
        else:
            print(f"{out_fmt.capitalize()}: Conversion from {effective_input_format} to {out_fmt} not implemented yet.")
            current_result_data["Actual Output Value"] = "Not Implemented"
            conversion_results_data.append(current_result_data)
            
    return conversion_results_data

# --- Main CLI Application Logic ---
def main_cli():
    parser = argparse.ArgumentParser(description="Number base converter.")
    parser.add_argument("value", nargs='?', help="The number or character to convert.")
    parser.add_argument("-i", "--input", dest="input_format", default=None,
                        help="Input format (ascii, binary, octal, decimal, hexadecimal). Defaults to decimal or ascii based on input if 'value' is provided directly.")
    parser.add_argument("-o", "--output", dest="output_format", default="all",
                        help="Output format (ascii, binary, octal, decimal, hexadecimal, all). Default: all. May be overridden by file lines specifying output format.")
    parser.add_argument("-s", "--steps", action="store_true", help="Show step-by-step solution (plain text or LaTeX if -l is also given).")
    parser.add_argument("-f", "--file", dest="input_file", help="Read input from text file. Each line: 'value input_base output_base'.")
    parser.add_argument("-l", "--latex", action="store_true", help="Generate step-by-step solution in LaTeX format (requires -s).")
    parser.add_argument("-csv", "--csvfile", dest="csv_output_file", help="Export results to a CSV file.")
    # parser.add_argument("-q", "--quiet", action="store_true", help="Suppress printing of output format type(s).") # TODO
    # parser.add_argument("-e", "--excel", dest="excel_file", help="Export step-by-step solution to excel file (implies LaTeX for steps).") # TODO
    parser.add_argument("-v", "--version", action="version", version="%(prog)s Python v0.1.1 (Modular with CSV)")

    args = parser.parse_args()

    if args.latex and not args.steps:
        parser.error("-l/--latex requires -s/--steps.")

    all_csv_data = []

    # --- Conversion Map (defined once) ---
    # Now stores a tuple for steps: (plain_steps_func, latex_steps_func)
    conversion_map = {
        (DECIMAL, BINARY): (decimal_to_binary, (decimal_to_binary_steps, decimal_to_binary_steps_latex)),
        (BINARY, DECIMAL): (binary_to_decimal, (binary_to_decimal_steps, binary_to_decimal_steps_latex)),
        (DECIMAL, HEXADECIMAL): (decimal_to_hexadecimal, (decimal_to_hexadecimal_steps, decimal_to_hexadecimal_steps_latex)),
        (HEXADECIMAL, DECIMAL): (hexadecimal_to_decimal, (hexadecimal_to_decimal_steps, hexadecimal_to_decimal_steps_latex)),
        
        # New conversions involving Octal
        (DECIMAL, OCTAL): (decimal_to_octal, (decimal_to_octal_steps, decimal_to_octal_steps_latex)),
        (OCTAL, DECIMAL): (octal_to_decimal, (octal_to_decimal_steps, octal_to_decimal_steps_latex)),
        
        # Hexadecimal <-> Binary
        (HEXADECIMAL, BINARY): (hexadecimal_to_binary, (hexadecimal_to_binary_steps, hexadecimal_to_binary_steps_latex)),
        (BINARY, HEXADECIMAL): (binary_to_hexadecimal, (binary_to_hexadecimal_steps, binary_to_hexadecimal_steps_latex)),

        # Octal <-> Binary
        (OCTAL, BINARY): (octal_to_binary, (octal_to_binary_steps, octal_to_binary_steps_latex)),
        (BINARY, OCTAL): (binary_to_octal, (binary_to_octal_steps, binary_to_octal_steps_latex)),

        # Hexadecimal <-> Octal (via Binary)
        (HEXADECIMAL, OCTAL): (hexadecimal_to_octal, (hexadecimal_to_octal_steps, hexadecimal_to_octal_steps_latex)),
        (OCTAL, HEXADECIMAL): (octal_to_hexadecimal, (octal_to_hexadecimal_steps, octal_to_hexadecimal_steps_latex)),
    }

    if args.input_file:
        # process_file_input will call execute_conversion_and_get_data for each line
        # and should accumulate the results.
        # We modify process_file_input to return the accumulated list of dicts.
        all_csv_data = process_file_input(
            args.input_file, 
            args, 
            conversion_map,
            lambda val, in_fmt, out_fmts, steps, use_ltx, conv_map, cli_all: execute_conversion_and_get_data(val, in_fmt, out_fmts, steps, use_ltx, conv_map, cli_all)
        )
    elif args.value:
        input_value = args.value
        actual_input_format = None
        
        if args.input_format:
            actual_input_format = get_format_from_string(args.input_format)
            if not actual_input_format:
                print(f"Error: Unknown input format '{args.input_format}' provided via -i.")
                if args.csv_output_file: # Also write error to CSV if applicable
                     all_csv_data.append({
                        "Input Value": input_value, "Input Base": args.input_format, 
                        "Requested Output Base": args.output_format, "Actual Output Value": "Error: Unknown input format", "Steps": ""
                    })
                # No return here yet, let it try to write CSV if filename given.
        else: 
            try:
                int(input_value)
                actual_input_format = DECIMAL
            except ValueError:
                if all(c in '0123456789abcdefABCDEF' for c in input_value) and any(c.lower() in 'abcdef' for c in input_value):
                    actual_input_format = HEXADECIMAL
                else:
                    actual_input_format = ASCII
        
        if not actual_input_format : # Should have been caught above if -i was bad. This is for auto-detection failure leading to no format.
             print(f"Error: Could not reliably determine input format for '{input_value}'. Please specify with -i.")
             all_csv_data.append({
                "Input Value": input_value, "Input Base": "Unknown", 
                "Requested Output Base": args.output_format, "Actual Output Value": "Error: Could not determine input format", "Steps": ""
            })
        else:
            output_formats_requested = []
            cli_output_all = args.output_format.lower() == "all"

            if cli_output_all:
                output_formats_requested = [fmt for fmt in ALL_FORMATS]
            else:
                requested_out_fmt = get_format_from_string(args.output_format)
                if requested_out_fmt:
                    output_formats_requested = [requested_out_fmt]
                else:
                    print(f"Error: Unknown output format '{args.output_format}' provided via -o.")
                    all_csv_data.append({
                        "Input Value": input_value, "Input Base": actual_input_format, 
                        "Requested Output Base": args.output_format, "Actual Output Value": "Error: Unknown output format", "Steps": ""
                    })
            
            if output_formats_requested: # Only proceed if we have valid output formats
                data_from_conversion = execute_conversion_and_get_data(
                    input_value, 
                    actual_input_format, 
                    output_formats_requested, 
                    args.steps, 
                    args.latex, 
                    conversion_map, 
                    cli_output_all
                )
                all_csv_data.extend(data_from_conversion)

    else: # No input_file and no value
        parser.print_help()
        # No data to write to CSV in this case.
    
    if args.csv_output_file and all_csv_data:
        # Ensure file_processor.py has write_results_to_csv
        # This function should be imported or defined in file_processor.py
        # For now, assuming it's imported and available.
        print(f"\nWriting results to {args.csv_output_file}...")
        write_results_to_csv(all_csv_data, args.csv_output_file)
        print("Done.")
    elif args.csv_output_file and not all_csv_data:
        print(f"\nNo data to write to {args.csv_output_file}.") 