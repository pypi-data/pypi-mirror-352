from config import ALL_FORMATS, ASCII, BINARY, OCTAL, DECIMAL, HEXADECIMAL

# --- Helper function to resolve format names ---
def get_format_from_string(format_str_in):
    """Converts short or long format names (e.g., 'b', 'binary') to canonical format names."""
    if not format_str_in:
        return None
    s = format_str_in.lower()
    if s in ALL_FORMATS: return s
    if s == 'a': return ASCII
    if s == 'b': return BINARY
    if s == 'o': return OCTAL
    if s == 'd': return DECIMAL
    if s == 'h': return HEXADECIMAL
    return None # Unknown 

def get_ordinal_suffix(n_int):
    """Converts an integer to its ordinal string with suffix (e.g., 1 -> 1st, 2 -> 2nd)."""
    if 11 <= (n_int % 100) <= 13:
        return str(n_int) + 'th'
    suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
    return str(n_int) + suffixes.get(n_int % 10, 'th')

def get_ordinal_text(n_int):
    """Converts an integer to its ordinal text (e.g., 1 -> First, 2 -> Second)."""
    # Based on Go version, but Python handles large N differently. 
    # This is a simplified version matching common cases from Go.
    if n_int <= 0:
        return f"{n_int}th" # Or raise error
    if n_int == 1: return "First"
    if n_int == 2: return "Second"
    if n_int == 3: return "Third"
    if n_int == 4: return "Fourth"
    if n_int == 5: return "Fifth"
    if n_int == 6: return "Sixth"
    if n_int == 7: return "Seventh"
    if n_int == 8: return "Eighth"
    if n_int == 9: return "Ninth"
    if n_int == 10: return "Tenth"
    return f"{n_int}th" # Fallback for numbers > 10, Go version was more complex 