import re

def glob_to_regex(glob_pattern):
    # Escape all regex special characters except for * and ?
    pattern = re.escape(glob_pattern)
    pattern = pattern.replace(r'\*', '.*').replace(r'\?', '.')
    return f"^{pattern}$"

pattern = glob_to_regex("SkCanvas::experimental_*")
regex = re.compile(pattern)

if regex.match("SkCanvas::experimental_feature"):
    print("Matched!")