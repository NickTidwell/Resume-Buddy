import difflib

def compare_strings(original, new):
    # Convert strings into lists of characters
    original_chars = list(original)
    new_chars = list(new)

    # Perform the comparison
    differ = difflib.Differ()
    diff = list(differ.compare(original_chars, new_chars))
    
    return diff

def generate_html_diff(diff):
    original_html = []
    new_html = []

    for char in diff:
        if char.startswith(' '):
            original_html.append(f'<span>{char[2:]}</span>')
            new_html.append(f'<span>{char[2:]}</span>')
        elif char.startswith('-'):
            original_html.append(f'<span style="background-color: #fdd; color: #d00;">{char[2:]}</span>')
        elif char.startswith('+'):
            new_html.append(f'<span style="background-color: #dfd; color: #080;">{char[2:]}</span>')

    # Add empty spaces for alignment
    max_len = max(len(original_html), len(new_html))
    original_html.extend(['<span>&nbsp;</span>'] * (max_len - len(original_html)))
    new_html.extend(['<span>&nbsp;</span>'] * (max_len - len(new_html)))

    return (''.join(original_html), ''.join(new_html))
