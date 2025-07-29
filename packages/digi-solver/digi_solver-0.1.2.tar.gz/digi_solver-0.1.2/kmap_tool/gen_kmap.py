import random
import itertools
import subprocess
import re
import os
import sys
import csv
from collections import defaultdict
import argparse

# Removed sys.path.append
from .QuineMcCluskey.core.qm.qm import QM

# Try to import pandas and openpyxl for Excel output
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    print("Warning: pandas not installed. Excel output will not be available, and final processing will fail.")
    HAS_PANDAS = False

# Variables for K-maps
var_sets = {
    3: ['a', 'b', 'c'],
    4: ['a', 'b', 'c', 'd'],
    5: ['a', 'b', 'c', 'd', 'e'],
    6: ['a', 'b', 'c', 'd', 'e', 'f']
}

# Parameters for generating K-map problems based on number of variables
gen_params_config = {
    3: {'min_terms_abs': 2, 'max_terms_val_ratio': 0.6, 'max_terms_abs': 5,  'dc_rem_ratio': 0.25, 'dc_abs': 2},
    4: {'min_terms_abs': 3, 'max_terms_val_ratio': 0.5, 'max_terms_abs': 10, 'dc_rem_ratio': 0.25, 'dc_abs': 4},
    5: {'min_terms_abs': 4, 'max_terms_val_ratio': 0.5, 'max_terms_abs': 19, 'dc_rem_ratio': 0.25, 'dc_abs': 8}, # Max 19 terms, dc up to 10
    6: {'min_terms_abs': 5, 'max_terms_val_ratio': 0.3, 'max_terms_abs': 19, 'dc_rem_ratio': 0.15, 'dc_abs': 8}, # Max 19 terms, dc up to 8
}

# Function to generate random terms (minterms)
def generate_random_terms(max_val, min_count, max_count):
    # Ensure max_count is not greater than max_val
    max_count = min(max_count, max_val)
    # Ensure min_count is not greater than max_count
    min_count = min(min_count, max_count)
    if min_count < 0: min_count = 0

    count = random.randint(min_count, max_count)
    return sorted(random.sample(range(max_val), count))

# Function to generate a K-map problem
def generate_kmap_problem(num_vars):
    if num_vars not in var_sets:
        raise ValueError(f"Unsupported number of variables for generation: {num_vars}")
    
    max_val = 2 ** num_vars
    params = gen_params_config[num_vars]

    # Generate minterms
    min_terms_count_actual = max(params['min_terms_abs'], int(num_vars * 0.8)) # At least params['min_terms_abs']
    max_terms_count_actual = min(int(max_val * params['max_terms_val_ratio']), params['max_terms_abs'])
    
    minterms = generate_random_terms(max_val, min_terms_count_actual, max_terms_count_actual)
    
    # Generate don't cares
    remaining_for_dc = [x for x in range(max_val) if x not in minterms]
    if not remaining_for_dc: # No space left for don't cares
        dontcares_selected = []
    else:
        max_dontcares_count = min(int(len(remaining_for_dc) * params['dc_rem_ratio']), params['dc_abs'])
        # generate_random_terms needs indices for remaining_for_dc, not values directly
        dontcare_indices = generate_random_terms(len(remaining_for_dc), 0, max_dontcares_count)
        dontcares_selected = sorted([remaining_for_dc[i] for i in dontcare_indices])
        
    return {
        'num_vars': num_vars,
        'minterms': minterms,
        'dontcares': dontcares_selected,
        'variables': var_sets[num_vars]
    }

# Function to convert literal expression to minterms (which original minterms/dontcares it covers)
def product_term_to_minterms(product_term, variables, all_minterms, all_dontcares):
    var_values = {}
    i = 0
    while i < len(product_term):
        if i < len(product_term) - 1 and product_term[i+1] == "'":
            var_values[product_term[i]] = 0
            i += 2
        elif product_term[i].isalpha():
            var_values[product_term[i]] = 1
            i += 1
        else:
            i += 1
    
    covered_minterms = []
    covered_dontcares = []
    
    for minterm_val in all_minterms + all_dontcares:
        binary = bin(minterm_val)[2:].zfill(len(variables))
        is_covered = True
        for var, value in var_values.items():
            if var in variables:
                var_index = variables.index(var)
                if var_index < len(binary) and int(binary[var_index]) != value:
                    is_covered = False
                    break
            else: # variable in product term not in overall K-map variables
                is_covered = False
                break 
        
        if is_covered:
            if minterm_val in all_minterms:
                covered_minterms.append(minterm_val)
            elif minterm_val in all_dontcares: # Ensure it was an original DC
                covered_dontcares.append(minterm_val)
    
    return covered_minterms, covered_dontcares

# Function to calculate all cells covered by a product term (implicant)
def calculate_full_implicant_cells(product_term_str, all_variables):
    if not all_variables: return []
    num_kmap_vars = len(all_variables)

    if product_term_str == "0": # Function is always 0 for this term means no cells for this term
        return []
    if product_term_str == "1":  # Function is always 1
        return list(range(2**num_kmap_vars))

    var_values_fixed = {}
    temp_idx = 0
    term_chars = list(product_term_str)

    while temp_idx < len(term_chars):
        char = term_chars[temp_idx]
        if char.isalpha() and char in all_variables:
            if temp_idx + 1 < len(term_chars) and term_chars[temp_idx + 1] == "'":
                var_values_fixed[char] = 0
                temp_idx += 2
            else:
                var_values_fixed[char] = 1
                temp_idx += 1
        elif char.isspace() or char in "+*": # Skip operators or spaces
            temp_idx +=1
        else: # Unexpected char
            # print(f"Warning: Unexpected character \'{char}\' in product term \'{product_term_str}\' while calculating full implicant cells.")
            temp_idx += 1
            
    free_variables = [v for v in all_variables if v not in var_values_fixed]
    
    implicant_minterms = []
    num_free_vars = len(free_variables)

    for i in range(2**num_free_vars):
        binary_combination = bin(i)[2:].zfill(num_free_vars)
        current_minterm_val_map = {}
        for var, val in var_values_fixed.items():
            current_minterm_val_map[var] = val
        for k, free_var_char in enumerate(free_variables):
            current_minterm_val_map[free_var_char] = int(binary_combination[k])
        
        minterm_binary_list = []
        valid_minterm = True
        for var_char_ordered in all_variables:
            if var_char_ordered in current_minterm_val_map:
                minterm_binary_list.append(str(current_minterm_val_map[var_char_ordered]))
            else: # Should not happen if free_variables logic is correct
                valid_minterm = False
                break 
        
        if valid_minterm:
            minterm_binary_str = "".join(minterm_binary_list)
            implicant_minterms.append(int(minterm_binary_str, 2))
        
    return sorted(list(set(implicant_minterms)))

# Function to solve a K-map problem using QuineMcCluskey
def solve_kmap_problem(problem):
    minterms = problem['minterms']
    dontcares = problem['dontcares']
    variables = problem['variables']
    
    qm = QM(minterms, dontcares, variables)
    solutions = qm.minimize() 

    minterm_groups_list = []
    dontcare_groups_list = [] # Original DCs covered by each term
    product_terms_for_grouping = []

    if not solutions or not solutions[0] or solutions[0] == "0":
        pass 
    else:
        solution_expression = solutions[0]
        individual_product_terms = [term.strip() for term in solution_expression.split('+') if term.strip()]
        
        for term_str in individual_product_terms:
            covered_minterms_orig, covered_dontcares_orig = product_term_to_minterms(term_str, variables, minterms, dontcares)
            
            minterm_groups_list.append(sorted(covered_minterms_orig))
            dontcare_groups_list.append(sorted(covered_dontcares_orig)) # Keep track of original DCs covered
            product_terms_for_grouping.append(term_str)

    all_covered_by_groups = set()
    for group_m_terms in minterm_groups_list:
        all_covered_by_groups.update(group_m_terms)
    
    solution_is_meaningful = solutions and solutions[0] and solutions[0] != "0"
    if solution_is_meaningful and all_covered_by_groups != set(minterms):
        uncovered = set(minterms) - all_covered_by_groups
        # This can happen if QM simplifies to "1" and minterms were not all possible minterms
        # Or if a term only covers don't cares that were essential for simplification
        # print(f"Note: {len(uncovered)} original minterms not directly in minterm_groups_list coverage: {uncovered}. Solution: {solutions[0]}. This is often fine if DCs were used.")
    
    return {
        'problem': problem,
        'solutions': solutions, 
        'minterm_groups': minterm_groups_list, # Original minterms covered by each product term of solution
        'dontcare_groups': dontcare_groups_list, # Original don't cares covered by each product term
        'product_terms': product_terms_for_grouping 
    }

# Function to format the output in the required format
def format_result(result, id):
    problem = result['problem']
    solutions = result['solutions'] 
    product_terms = result['product_terms'] 
    
    # print(f"[DEBUG format_result ID {id}] Product terms received: {product_terms}") # DEBUG

    all_groups_formatted = []
    if product_terms:
        for i, p_term_str in enumerate(product_terms):
            # print(f"[DEBUG format_result ID {id}] Processing p_term {i+1}: '{p_term_str}'") # DEBUG
            if not p_term_str or p_term_str == "0": 
                # print(f"[DEBUG format_result ID {id}] Skipping p_term '{p_term_str}' because it is empty or '0'") # DEBUG
                continue 
            
            full_implicant_cell_numbers = calculate_full_implicant_cells(p_term_str, problem['variables'])
            # print(f"[DEBUG format_result ID {id}] For p_term '{p_term_str}', full_implicant_cell_numbers: {full_implicant_cell_numbers}") # DEBUG

            if full_implicant_cell_numbers:
                group_str = f"GROUP{i+1} ({','.join(map(str, sorted(full_implicant_cell_numbers)))})"
                all_groups_formatted.append(group_str)
            # else:
                # print(f"[DEBUG format_result ID {id}] For p_term '{p_term_str}', no cells were found by calculate_full_implicant_cells and it's not '0'/'1'. Group not created.") # DEBUG
    else:
        # print(f"[DEBUG format_result ID {id}] Product_terms list is empty. No groups will be formatted.") # DEBUG
        pass

    all_groups = "\n".join(all_groups_formatted)
    # print(f"[DEBUG format_result ID {id}] Generated all_groups string: '{all_groups}'") # DEBUG
    
    case_id = f"Case {id}"
    variables_str = ','.join(problem['variables'])
    
    function_str = f"f({variables_str}) = {','.join(map(str, problem['minterms']))}"
    if problem['dontcares']:
        function_str += f" + dontcares: {','.join(map(str, problem['dontcares']))}"
    
    solution_display = "Error or no solution"
    if solutions:
        if solutions[0] == "":
             solution_display = "0"
        else:
             solution_display = solutions[0]
    elif not problem['minterms']:
        solution_display = "0"

    result_str = f"RESULT: f({variables_str}) = {solution_display}"
    
    minterms_str = ','.join(map(str, problem['minterms']))
    dontcares_str = ','.join(map(str, problem['dontcares'])) if problem['dontcares'] else ""
    
    input_prompt_str = f"Use the Karnaugh map method to simplify the following function: \\\\( f({variables_str}) = \\\\Sigma m({minterms_str})"
    if dontcares_str:
        input_prompt_str += f" + \\\\Sigma d({dontcares_str})"
    input_prompt_str += " \\\\)"
    
    type_str = "SOP"
    
    return {
        'Case': case_id,
        'Input': input_prompt_str,
        'Function': function_str,
        'Groups': all_groups,
        'Result': result_str,
        'Type': type_str
    }

# Main function to generate K-map questions
def generate_kmap_questions(num_problems, num_vars_for_generation):
    results = []
    for i in range(num_problems):
        problem = generate_kmap_problem(num_vars_for_generation)
        solved_data = solve_kmap_problem(problem)
        formatted = format_result(solved_data, i + 1)
        results.append(formatted)
        # print(f"Generated {num_vars_for_generation}-var problem {i+1}/{num_problems}")
    return results

# Function to write results to CSV file
def write_to_csv(results, filename='kmap_questions.csv'):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Case', 'Input', 'Function', 'Groups', 'Result', 'Type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    return filename

# Function to write results to Excel file
def write_to_excel(results, filename='kmap_questions.xlsx'):
    if not HAS_PANDAS:
        print("Pandas not installed. Skipping Excel output.")
        return None
    df_data = []
    columns = ['Case', 'Input', 'Function', 'Groups', 'Result', 'Type']
    for result in results:
        df_data.append(result)
    df = pd.DataFrame(df_data, columns=columns)
    df.to_excel(filename, index=False)
    return filename

# Function to parse input from a full function string
def parse_input_function_string(input_str):
    match = re.match(r"f\s*\(([^)]*)\)\s*=\s*([^+]*)(\s*\+\s*dontcares:\s*(.*))?", input_str, re.IGNORECASE)
    if not match:
        # Try another regex for sum of products style, e.g. "f(a,b,c) = a'b + bc'"
        # This part is complex if we want to parse generic SOP from the string.
        # For now, assume the "f(vars) = minterms + dontcares: dcs" format
        print(f"Error: Could not parse function string in 'f(vars)=minterms+dontcares:dcs' format: {input_str}")
        return None

    vars_str = match.group(1).strip()
    minterms_segment = match.group(2).strip()
    dontcares_segment = match.group(4) 

    parsed_variables = [v.strip() for v in vars_str.split(',') if v.strip()]
    if not parsed_variables:
        print(f"Error: No variables found in function string: {input_str}")
        return None
    num_parsed_vars = len(parsed_variables)

    if num_parsed_vars not in var_sets:
        print(f"Error: Unsupported number of variables ({num_parsed_vars}) in function string: {input_str}. Supported: {list(var_sets.keys())}")
        return None

    minterms = []
    if minterms_segment:
        try:
            minterms = [int(x.strip()) for x in minterms_segment.split(',') if x.strip()]
        except ValueError:
            print(f"Error: Invalid minterm number in function string: {input_str}")
            return None
    
    dontcares = []
    if dontcares_segment:
        try:
            dontcares = [int(x.strip()) for x in dontcares_segment.strip().split(',') if x.strip()]
        except ValueError:
            print(f"Error: Invalid don't care term number in function string: {input_str}")
            return None
            
    return {
        'num_vars': num_parsed_vars,
        'minterms': minterms,
        'dontcares': dontcares,
        'variables': parsed_variables
    }

# Function to read and process functions from a file
def process_functions_from_file(filename):
    problems_from_file = []
    try:
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'): # Skip empty lines and comments
                    problem_dict = parse_input_function_string(line)
                    if problem_dict:
                        problems_from_file.append(problem_dict)
                    else:
                        print(f"Skipping invalid line {line_num} in file {filename}: {line}")
    except FileNotFoundError:
        print(f"Error: Input file not found: {filename}")
        return []
    except Exception as e:
        print(f"Error reading input file {filename}: {str(e)}")
        return []

    results = []
    for i, problem_data in enumerate(problems_from_file):
        solved_data = solve_kmap_problem(problem_data)
        formatted = format_result(solved_data, i + 1)
        results.append(formatted)
    return results

# Functions from fillData.py
def parse_groups(groups_str):
    # print(f"[DEBUG parse_groups] Input groups_str: '{groups_str}' (type: {type(groups_str)})") # DEBUG
    groups = []
    if pd.notna(groups_str) and isinstance(groups_str, str): # Check both notna and type for robustness
        lines = groups_str.splitlines()
        # print(f"[DEBUG parse_groups] Split lines: {lines}") # DEBUG
        for i, line in enumerate(lines):
            # print(f"[DEBUG parse_groups] Processing line {i+1}: '{line}'") # DEBUG
            match = re.search(r'GROUP\d+\s*\((.*?)\)', line)
            if match:
                # print(f"[DEBUG parse_groups] Match found for line '{line}': '{match.group(1)}'") # DEBUG
                groups.append(match.group(1))
            else:
                # print(f"[DEBUG parse_groups] No match for line '{line}'") # DEBUG
                pass
    else:
        # print(f"[DEBUG parse_groups] groups_str is None, NaN, or not a string. Skipping parsing.") # DEBUG
        pass
    # print(f"[DEBUG parse_groups] Returning groups: {groups}") # DEBUG
    return groups

def generate_kmap(vars_str, minterms_str, dontcares_str):
    num_vars = len(vars_str.split(','))
    minterms = [int(x) for x in minterms_str.split(',') if x.strip()]
    dontcares = [int(x) for x in dontcares_str.split(',') if x.strip()] if dontcares_str else []

    if num_vars == 3:
        kmap = [[0 for _ in range(4)] for _ in range(2)]
        mapping = [
            (0, 0, 0), (0, 1, 1), (0, 2, 3), (0, 3, 2),
            (1, 0, 4), (1, 1, 5), (1, 2, 7), (1, 3, 6)
        ]
    elif num_vars == 4:
        kmap = [[0 for _ in range(4)] for _ in range(4)]
        mapping = [
            (0, 0, 0), (0, 1, 1), (0, 2, 3), (0, 3, 2),
            (1, 0, 4), (1, 1, 5), (1, 2, 7), (1, 3, 6),
            (2, 0, 12), (2, 1, 13), (2, 2, 15), (2, 3, 14), 
            (3, 0, 8), (3, 1, 9), (3, 2, 11), (3, 3, 10)   
        ]
    elif num_vars == 5: 
        kmap = [[0 for _ in range(8)] for _ in range(4)]
        mapping = [
            (0,0,0), (0,1,1), (0,2,3), (0,3,2), (0,4,6), (0,5,7), (0,6,5), (0,7,4),
            (1,0,8), (1,1,9), (1,2,11), (1,3,10), (1,4,14), (1,5,15), (1,6,13), (1,7,12),
            (2,0,24), (2,1,25), (2,2,27), (2,3,26), (2,4,30), (2,5,31), (2,6,29), (2,7,28),
            (3,0,16), (3,1,17), (3,2,19), (3,3,18), (3,4,22), (3,5,23), (3,6,21), (3,7,20)
        ]
    elif num_vars == 6: 
        kmap = [[0 for _ in range(8)] for _ in range(8)]
        mapping = [
            (0,0,0), (0,1,1), (0,2,3), (0,3,2), (0,4,4), (0,5,5), (0,6,7), (0,7,6),
            (1,0,8), (1,1,9), (1,2,11), (1,3,10), (1,4,12), (1,5,13), (1,6,15), (1,7,14),
            (2,0,24), (2,1,25), (2,2,27), (2,3,26), (2,4,28), (2,5,29), (2,6,31), (2,7,30),
            (3,0,16), (3,1,17), (3,2,19), (3,3,18), (3,4,20), (3,5,21), (3,6,23), (3,7,22),
            (4,0,32), (4,1,33), (4,2,35), (4,3,34), (4,4,36), (4,5,37), (4,6,39), (4,7,38),
            (5,0,40), (5,1,41), (5,2,43), (5,3,42), (5,4,44), (5,5,45), (5,6,47), (5,7,46),
            (6,0,56), (6,1,57), (6,2,59), (6,3,58), (6,4,60), (6,5,61), (6,6,63), (6,7,62),
            (7,0,48), (7,1,49), (7,2,51), (7,3,50), (7,4,52), (7,5,53), (7,6,55), (7,7,54)
        ]
    else:
        return [] 

    for row, col, val in mapping:
        if val in minterms:
            kmap[row][col] = 1
        elif val in dontcares:
            kmap[row][col] = 'x'
    return kmap

def kmap_to_latex(kmap, num_vars):
    if not kmap: return ""

    if num_vars == 3:
        rows, cols = 2, 4
        row_labels = ["0", "1"]
        col_labels_str = "00 & 01 & 11 & 10"
        header = f"\\[\\begin{{array}} {{|c|c|c|c|c|}} \\hline a \\backslash bc & {col_labels_str} \\\\ \\hline "
    elif num_vars == 4:
        rows, cols = 4, 4
        row_labels = ["00", "01", "11", "10"] 
        col_labels_str = "00 & 01 & 11 & 10"
        header = f"\\[\\begin{{array}} {{|c|c|c|c|c|}} \\hline ab \\backslash cd & {col_labels_str} \\\\ \\hline "
    elif num_vars == 5:
        rows, cols = 4, 8
        row_labels = ["00", "01", "11", "10"] 
        col_labels_str = "000 & 001 & 011 & 010 & 110 & 111 & 101 & 100" 
        header = f"\\[\\begin{{array}} {{|c|c|c|c|c|c|c|c|c|}} \\hline ab \\backslash cde & {col_labels_str} \\\\ \\hline "
    elif num_vars == 6:
        rows, cols = 8, 8
        row_labels = ["000", "001", "011", "010", "100", "101", "111", "110"] 
        col_labels_str = "000 & 001 & 011 & 010 & 100 & 101 & 111 & 110" 
        header = f"\\[\\begin{{array}} {{|c|c|c|c|c|c|c|c|c|c|}} \\hline abc \\backslash def & {col_labels_str} \\\\ \\hline "
    else:
        return ""

    latex = header
    for i in range(rows):
        latex += f"{row_labels[i]} & {' & '.join(str(kmap[i][j]) for j in range(cols))} \\\\ \\hline " # Use \\\\ for LaTeX newline
    latex += "\\end{array}\\]" # Use single curlies based on user's last version
    return latex

def generate_latex(row_data):
    func_match = re.search(r'f\((.*?)\) = (.*?)(?: \+ dontcares: (.*))?$', row_data['Function'])
    if not func_match:
        print(f"Warning: Could not parse 'Function' string for LaTeX generation: {row_data.get('Function')}")
        return None, None, None

    vars_str = func_match.group(1)
    minterms_str_from_func = func_match.group(2).strip()
    dontcares_str_from_func = func_match.group(3).strip() if func_match.group(3) is not None else ""
    
    result_match = re.search(r'RESULT:\s*f\((.*?)\) = (.*)', row_data['Result'])
    result_str = result_match.group(2).strip() if result_match else ""
    
    current_groups_string_for_latex = row_data['Groups'] 
    # print(f"[DEBUG generate_latex] Received groups_string from row_data['Groups']: '{current_groups_string_for_latex}'") # DEBUG

    groups = parse_groups(current_groups_string_for_latex)
    # print(f"[DEBUG generate_latex] Parsed groups for LaTeX (result from parse_groups): {groups}") # DEBUG
    
    num_vars = len(vars_str.split(','))
    flag_dontcare = bool(dontcares_str_from_func)

    data_input = f"Use the Karnaugh map method to simplify the following function: \\\\( f({vars_str}) = \\\\Sigma m({minterms_str_from_func})"
    if flag_dontcare:
        data_input += f" + \\\\Sigma d({dontcares_str_from_func})"
    data_input += " \\\\)"

    kmap = generate_kmap(vars_str, minterms_str_from_func, dontcares_str_from_func)
    kmap_latex = kmap_to_latex(kmap, num_vars)

    groups_latex = "\\[\\begin{array}{|c|c|} \\hline "
    result_terms = [term.strip() for term in result_str.split('+')]
    # print(f"[DEBUG generate_latex] Result terms for table: {result_terms}") # DEBUG

    if not groups:
        # print(f"[DEBUG generate_latex] 'groups' list is empty. No group rows will be added to LaTeX table.")
        pass
    else:
        for i, group_val_str in enumerate(groups):
            term_display = result_terms[i] if i < len(result_terms) else "Error: Term Missing"
            groups_latex += f"({group_val_str}) &  {term_display}  \\\\ \\hline "
            # print(f"[DEBUG generate_latex] Group {i+1}: ({group_val_str_item}) & {term_display}") # Your existing DEBUG
            
    groups_latex += "\\end{array}\\]"
    # print(f"[DEBUG generate_latex] Final groups_latex: '{groups_latex}'") # DEBUG
    
    kmap_structure_intro = ""
    row_var_names = ""
    col_var_names = ""
    row_gray_code_desc = ""
    col_gray_code_desc = ""
    example_kmap_numbering = ""

    if num_vars == 3:
        kmap_structure_intro = "3-variable K-map is arranged as follows (in Gray code order):"
        row_var_names = "$a$"
        col_var_names = "$bc$"
        row_gray_code_desc = "0, 1"
        col_gray_code_desc = "00, 01, 11, 10"
        example_kmap_numbering = '\\[\\begin{array} {|c|c|c|c|c|} \\hline a \\backslash bc & 00 & 01 & 11 & 10 \\\\ \\hline 0 & 0 & 1 & 3 & 2 \\\\ \\hline 1 & 4 & 5 & 7 & 6 \\\\ \\hline \\end{array}\\]'
    elif num_vars == 4:
        kmap_structure_intro = "4-variable K-map is arranged as follows (in Gray code order):"
        row_var_names = "$ab$"
        col_var_names = "$cd$"
        row_gray_code_desc = "00, 01, 11, 10"
        col_gray_code_desc = "00, 01, 11, 10"
        example_kmap_numbering = '\\[\\begin{array} {|c|c|c|c|c|} \\hline ab \\backslash cd & 00 & 01 & 11 & 10 \\\\ \\hline 00 & 0 & 1 & 3 & 2 \\\\ \\hline 01 & 4 & 5 & 7 & 6 \\\\ \\hline 11 & 12 & 13 & 15 & 14 \\\\ \\hline 10 & 8 & 9 & 11 & 10 \\\\ \\hline \\end{array}\\]'
    elif num_vars == 5:
        kmap_structure_intro = "5-variable K-map is arranged as follows (in Gray code order):"
        row_var_names = "$ab$"
        col_var_names = "$cde$"
        row_gray_code_desc = "00, 01, 11, 10"
        col_gray_code_desc = "000, 001, 011, 010, 110, 111, 101, 100"
        example_kmap_numbering = "\\[ \\begin{array}{|c|c|c|c|c|c|c|c|c|} \\hline \\text{ab} \\backslash \\text{cde} & 000 & 001 & 011 & 010 & 110 & 111 & 101 & 100 \\\\ \\hline 00 & 0 & 1 & 3 & 2 & 6 & 7 & 5 & 4 \\\\ \\hline 01 & 8 & 9 & 11 & 10 & 14 & 15 & 13 & 12 \\\\ \\hline 11 & 24 & 25 & 27 & 26 & 30 & 31 & 29 & 28 \\\\ \\hline 10 & 16 & 17 & 19 & 18 & 22 & 23 & 21 & 20 \\\\ \\hline \\end{array} \\]"
    elif num_vars == 6:
        kmap_structure_intro = "6-variable K-map is arranged as follows (in Gray code order):"
        row_var_names = "$abc$"
        col_var_names = "$def$"
        row_gray_code_desc = "000, 001, 011, 010, 100, 101, 111, 110"
        col_gray_code_desc = "000, 001, 011, 010, 100, 101, 111, 110"
        example_kmap_numbering = "\\[ \\begin{array}{|c|c|c|c|c|c|c|c|c|} \\hline \\text{abc} \\backslash \\text{def} & 000 & 001 & 011 & 010 & 100 & 101 & 111 & 110 \\\\ \\hline 000 & 0 & 1 & 3 & 2 & 4 & 5 & 7 & 6 \\\\ \\hline 001 & 8 & 9 & 11 & 10 & 12 & 13 & 15 & 14 \\\\ \\hline 011 & 24 & 25 & 27 & 26 & 28 & 29 & 31 & 30 \\\\ \\hline 010 & 16 & 17 & 19 & 18 & 20 & 21 & 23 & 22 \\\\ \\hline 100 & 32 & 33 & 35 & 34 & 36 & 37 & 39 & 38 \\\\ \\hline 101 & 40 & 41 & 43 & 42 & 44 & 45 & 47 & 46 \\\\ \\hline 111 & 56 & 57 & 59 & 58 & 60 & 61 & 63 & 62 \\\\ \\hline 110 & 48 & 49 & 51 & 50 & 52 & 53 & 55 & 54 \\\\ \\hline \\end{array} \\]"
        
    dontcare_item_text = ("\\item Don't-care (x) at minterms: $" + dontcares_str_from_func + "$. \n") if flag_dontcare else ""
    dontcare_fill_text = (", or x (don't-care)") if flag_dontcare else ""

    data_solution_parts = (
        "\\begin{enumerate} \n",
        "\\item Construct the K-map table. \\\\ We have " + str(num_vars) + " variables $(" + vars_str + ")$. ",
        "Typically, a " + kmap_structure_intro + " \\\\ \n",
        "Rows (based on " + row_var_names + "): \\begin{itemize} \\item " + row_gray_code_desc + " \\end{itemize}\n",
        "Columns (based on " + col_var_names + "): \\begin{itemize} \\item " + col_gray_code_desc + " \\end{itemize}\n",
        "The cells in the K-map are numbered as minterms, as shown below: \n",
        example_kmap_numbering + "\n",
        "For the function: \\begin{itemize}\n",
        "\\item 1 at minterms: $" + minterms_str_from_func + "$. \n",
        dontcare_item_text,
        "\\item 0 at all other minterms. \n",
        "\\end{itemize}\n",
        "Now, fill the K-map with values of 1, 0",
        dontcare_fill_text,
        ": " + kmap_latex + "\n",
        "\\item Grouping (grouping 1s and leveraging don't-care cells). \\\\ \n",
        "We group in powers of 2 (1, 2, 4, 8, ...) and use the x cells if they help expand the groups. ",
        "Here's one way to group (each \"group\" corresponds to a product term in the simplified form): ",
        groups_latex + "\n",
        "The result is: $f(" + vars_str + ") = " + result_str + "$ \n",
        "\\end{enumerate}"
    )
    data_solution = "".join(data_solution_parts)
    data_output = f"f({vars_str}) = {result_str}"
    return data_input, data_solution, data_output

# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='K-map Problem Generator/Solver for 3-6 Variables.',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--mode', choices=['generate', 'solve'], required=True, 
                        help='Mode of operation:\n'
                             'generate: Create random K-map problems.\n'
                             'solve: Solve K-map problems from specified input.')
    
    gen_group = parser.add_argument_group('Options for "generate" mode')
    gen_group.add_argument('--gen_num_vars', type=int, choices=[3, 4, 5, 6],
                           help='Number of variables for random problem generation (required in generate mode).')
    gen_group.add_argument('--num_problems', type=int, default=10,
                           help='Number of problems to generate (default: 10).')

    solve_source_group = parser.add_argument_group('Problem source for "solve" mode (choose one)')
    source_exclusive_group = solve_source_group.add_mutually_exclusive_group()
    source_exclusive_group.add_argument('--direct_cli', action='store_true',
                                        help='Solve a single problem specified by direct CLI -m/-p, -d, -v arguments.')
    source_exclusive_group.add_argument('--input_file', type=str,
                                        help='Path to a file with K-map problems (one per line, e.g., "f(a,b,c) = 0,1 + dontcares: 2").')
    source_exclusive_group.add_argument('--input_function_str', type=str,
                                        help='A single K-map problem as a string (e.g., "f(a,b,c) = 0,1 + dontcares: 2").')

    cli_details_group = parser.add_argument_group('Details for "--direct_cli" solving')
    cli_term_group = cli_details_group.add_mutually_exclusive_group()
    cli_term_group.add_argument('-m', '--minterms', type=str,
                                help='Comma-separated list of minterms (used with --direct_cli).')
    cli_term_group.add_argument('-p', '--sop', type=str,
                                help='Sum of products expression (used with --direct_cli, e.g., "a\'b + bc").')
    cli_details_group.add_argument('-d', '--dont_cares', type=str, default="",
                                   help="Comma-separated list of don't cares (used with --direct_cli).")
    cli_details_group.add_argument('-v', '--variables', type=str,
                                   help="Comma-separated list of variables (e.g., a,b,c). Required for --direct_cli.")

    parser.add_argument('--output_basename', type=str, default='kmap_solved_questions',
                        help='Base name for output CSV/Excel files (default: kmap_solved_questions).')

    args = parser.parse_args()
    intermediate_results = [] 

    if args.mode == 'generate':
        if not args.gen_num_vars:
            parser.error("--gen_num_vars is required for generate mode.")
        actual_num_vars = args.gen_num_vars
        print(f"Generating {args.num_problems} K-map questions with {actual_num_vars} variables...")
        intermediate_results = generate_kmap_questions(args.num_problems, actual_num_vars)
        if not intermediate_results:
             print("No intermediate results generated.")

    elif args.mode == 'solve':
        if args.input_file:
            print(f"Processing functions from file: {args.input_file}")
            intermediate_results = process_functions_from_file(args.input_file)
        elif args.input_function_str:
            print(f"Processing single function from input string: {args.input_function_str}")
            problem_dict = parse_input_function_string(args.input_function_str)
            if problem_dict:
                solved_data = solve_kmap_problem(problem_dict)
                intermediate_results = [format_result(solved_data, 1)]
            else:
                print(f"Could not parse or process the input function string.")
        elif args.direct_cli:
            if not args.variables:
                parser.error("-v (--variables) must be provided for --direct_cli solve mode.")
            
            cli_variables_list = [v.strip() for v in args.variables.split(',') if v.strip()]
            actual_num_vars = len(cli_variables_list)

            if actual_num_vars not in var_sets:
                parser.error(f"Number of variables ({actual_num_vars}) from -v is not supported. Supported: {list(var_sets.keys())}")
            
            if not args.minterms and not args.sop:
                parser.error("Either -m (--minterms) or -p (--sop) must be provided for --direct_cli solve mode.")

            problem_dict = {
                'num_vars': actual_num_vars,
                'variables': cli_variables_list,
                'dontcares': [int(x.strip()) for x in args.dont_cares.split(',') if args.dont_cares and x.strip()] if args.dont_cares else []
            }

            if args.minterms:
                try:
                    problem_dict['minterms'] = [int(x.strip()) for x in args.minterms.split(',') if x.strip()]
                except ValueError:
                    parser.error("Invalid number in minterms list.")
            elif args.sop:
                minterms_from_sop = []
                sop_product_terms_list = args.sop.split('+')
                for p_term_str in sop_product_terms_list:
                    p_term_str = p_term_str.strip()
                    if p_term_str:
                        cells = calculate_full_implicant_cells(p_term_str, cli_variables_list)
                        minterms_from_sop.extend(cells)
                problem_dict['minterms'] = sorted(list(set(minterms_from_sop)))
            
            solved_data = solve_kmap_problem(problem_dict)
            intermediate_results = [format_result(solved_data, 1)]
        else:
            print("For 'solve' mode, please specify a source: --direct_cli, --input_file, or --input_function_str")
            parser.print_help()
            sys.exit(1)
        
        if not intermediate_results:
            print("No intermediate results to process from solve mode.")

    else: 
        parser.print_help()
        sys.exit(1)

    if intermediate_results:
        if not HAS_PANDAS:
            print("Error: pandas library is required for final processing and output, but it's not installed.")
            print("Please install pandas (e.g., 'pip install pandas') and rerun.")
            sys.exit(1)
            
        print("Processing intermediate results for final LaTeX output...")
        final_output_data = []
        for item_from_gen_kmap in intermediate_results:
            current_function_str = str(item_from_gen_kmap.get('Function', ''))
            current_result_str = str(item_from_gen_kmap.get('Result', ''))
            current_groups_str = item_from_gen_kmap.get('Groups', "")
            current_groups_str = str(current_groups_str)

            row_for_latex = {
                'Function': current_function_str,
                'Result': current_result_str,
                'Groups': current_groups_str
            }
            
            data_input, data_solution, data_output = generate_latex(row_for_latex)
            
            if data_input is not None:
                final_output_data.append({
                    'input': data_input,
                    'solution': data_solution,
                    'output': data_output,
                    'heading': 2.5, 
                    'level': 3     
                })
            else:
                print(f"Skipping item due to LaTeX generation error for Function: {current_function_str}")

        if final_output_data:
            final_output_filename = "./output_v1.csv"
            print(f"Writing final processed results to CSV file: {final_output_filename}")
            final_df = pd.DataFrame(final_output_data, columns=['input', 'solution', 'output', 'heading', 'level'])
            try:
                final_df.to_csv(final_output_filename, index=False)
                print(f"Successfully saved final output to {final_output_filename}")
            except Exception as e:
                print(f"Error writing final CSV file: {str(e)}")
        else:
            print("No data to write to the final CSV file after LaTeX processing.")
            
    else: 
        print("No intermediate results were generated or solved to process further.")
    
    print("Done!") 