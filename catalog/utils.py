import re
import os

def extract_chapter_number(filename):
    """
    Extracts the chapter number from a filename.
    Supports formats like:
    - "One Piece 1000.zip" -> 1000.0
    - "Chapter 12.cbz" -> 12.0
    - "v1ch2.5.zip" -> 2.5
    - "012.zip" -> 12.0
    
    Returns the number as a float, or None if no number is found.
    """
    # Remove extension
    name, _ = os.path.splitext(filename)
    
    # 1. Look for explicit patterns like "ch", "chap", "chapter" followed by number
    # This handles "Chapter 12", "ch.12", "ch12", "c12"
    explicit_pattern = re.search(r'(?:ch|chap|chapter|c)[.\-_ ]*(\d+(?:\.\d+)?)', name, re.IGNORECASE)
    if explicit_pattern:
        try:
            return float(explicit_pattern.group(1))
        except ValueError:
            pass

    # 2. Look for numbers at the end of the string
    # This handles "One Piece 1000", "Naruto 50.5"
    end_number_pattern = re.search(r'(\d+(?:\.\d+)?)\s*$', name)
    if end_number_pattern:
        try:
            return float(end_number_pattern.group(1))
        except ValueError:
            pass
            
    # 3. Look for any standalone number, prioritizing the last one found
    # This might match "2023" in "Summer 2023.zip", so it's a fallback
    all_numbers = re.findall(r'(\d+(?:\.\d+)?)', name)
    if all_numbers:
        try:
            # Check if likely a year (simple heuristic: > 1900 and < current year + 2)
            # But chapters like 2000 are valid (e.g. Hajime no Ippo getting there?)
            # For now, just take the last number found as it's usually the chapter number in standardized naming
            return float(all_numbers[-1])
        except ValueError:
            pass
            
    return None
