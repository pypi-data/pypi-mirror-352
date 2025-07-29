import csv # Added for CSV writing
from .utils import get_format_from_string
from .config import ALL_FORMATS, ASCII, BINARY, DECIMAL, HEXADECIMAL
# Note: execute_and_print_conversion will be in cli.py, so this will cause a circular import if not handled.
# For now, we'll assume it's passed as an argument or defined/imported differently later.

# --- File Processing Function ---
def process_file_input(file_path, cli_args, conversion_map_dict, conversion_executor_func):
    """
    Processes input from a file, where each line can specify a value, input base, and output base.
    Returns a list of dictionaries, where each dictionary is a row for the CSV.
    """
    all_results_for_csv = []
    try:
        with open(file_path, 'r') as f:
            for line_num, line_content in enumerate(f, 1):
                line_content = line_content.strip()
                if not line_content or line_content.startswith('#'):
                    continue

                parts = line_content.split()
                if len(parts) < 1:
                    print(f"Skipping empty or invalid line {line_num}: {line_content}")
                    continue
                
                value_to_convert = parts[0]
                file_input_base_str = parts[1] if len(parts) > 1 else None
                file_output_base_str = parts[2] if len(parts) > 2 else "all" # Default to all if not specified

                effective_input_format = None
                if file_input_base_str:
                    effective_input_format = get_format_from_string(file_input_base_str)
                    if not effective_input_format:
                        print(f"Error on line {line_num}: Unknown input format '{file_input_base_str}'. Skipping.")
                        all_results_for_csv.append({"Input Value": value_to_convert, "Input Base": file_input_base_str, "Requested Output Base": file_output_base_str, "Actual Output Value": "Error: Unknown input format on file line", "Steps": ""})
                        continue
                else: # Try to infer from cli_args or value itself (logic similar to direct CLI input)
                    if cli_args.input_format:
                         effective_input_format = get_format_from_string(cli_args.input_format)
                    else:
                        try:
                            int(value_to_convert)
                            effective_input_format = DECIMAL
                        except ValueError:
                            if all(c in '0123456789abcdefABCDEF' for c in value_to_convert) and any(c.lower() in 'abcdef' for c in value_to_convert):
                                effective_input_format = HEXADECIMAL
                            else:
                                effective_input_format = ASCII
                
                if not effective_input_format:
                    print(f"Error on line {line_num}: Could not determine input format for '{value_to_convert}'. Skipping.")
                    all_results_for_csv.append({"Input Value": value_to_convert, "Input Base": "Unknown", "Requested Output Base": file_output_base_str, "Actual Output Value": "Error: Could not determine input format on file line", "Steps": ""})
                    continue

                output_formats_for_this_line = []
                file_output_all = file_output_base_str.lower() == "all"

                if file_output_all:
                    output_formats_for_this_line = [fmt for fmt in ALL_FORMATS]
                else:
                    requested_fmt_from_file = get_format_from_string(file_output_base_str)
                    if requested_fmt_from_file:
                        output_formats_for_this_line = [requested_fmt_from_file]
                    else:
                        print(f"Error on line {line_num}: Unknown output format '{file_output_base_str}'. Skipping.")
                        all_results_for_csv.append({"Input Value": value_to_convert, "Input Base": str(effective_input_format), "Requested Output Base": file_output_base_str, "Actual Output Value": "Error: Unknown output format on file line", "Steps": ""})
                        continue
                
                print(f"\n--- Processing File Line {line_num}: {line_content} ---")
                # The conversion_executor_func is execute_conversion_and_get_data from cli.py
                # It already handles printing to console and returns a list of dicts for CSV.
                line_results = conversion_executor_func(
                    value_to_convert, 
                    effective_input_format, 
                    output_formats_for_this_line, 
                    cli_args.steps, 
                    cli_args.latex, 
                    conversion_map_dict,
                    file_output_all # Pass whether 'all' was specified for this line's output
                )
                all_results_for_csv.extend(line_results)
        
    except FileNotFoundError:
        print(f"Error: Input file '{file_path}' not found.")
        # Add an error entry for CSV if a CSV file was specified in CLI
        if cli_args.csv_output_file: 
             all_results_for_csv.append({"Input Value": "FILE_ERROR", "Input Base": file_path, "Requested Output Base": "N/A", "Actual Output Value": "Error: Input file not found", "Steps": ""})
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
        if cli_args.csv_output_file:
            all_results_for_csv.append({"Input Value": "FILE_ERROR", "Input Base": file_path, "Requested Output Base": "N/A", "Actual Output Value": f"Error: {e}", "Steps": ""})
    
    return all_results_for_csv

def write_results_to_csv(results_list, filename):
    """Writes a list of result dictionaries to a CSV file."""
    if not results_list:
        print("No data to write to CSV.")
        return

    # Define the headers based on the keys of the first dictionary (assuming all dicts have the same keys)
    # More robust: define headers explicitly to ensure order and inclusion of all desired fields.
    headers = ["Input Value", "Input Base", "Requested Output Base", "Actual Output Value", "Steps"]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for data_row in results_list:
                # Ensure all expected headers are present in data_row, fill with empty string if not
                # This handles cases where an error might have prevented some fields from being populated
                row_to_write = {header: data_row.get(header, "") for header in headers}
                writer.writerow(row_to_write)
        # print(f"Results successfully written to {filename}") # Already printed in cli.py
    except IOError:
        print(f"Error: Could not write to CSV file {filename}. Check permissions or path.")
    except Exception as e:
        print(f"An unexpected error occurred while writing to CSV: {e}") 