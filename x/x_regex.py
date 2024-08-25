import re

def translate_to_regex(pattern):
    # List of special regex characters to escape
    special_chars = '.^$*+?{}[]\\|()'
    
    # Function to escape special regex characters
    def escape_special(match):
        return '\\' + match.group(0)
    
    # Replace contents of curly braces with placeholders
    placeholders = {}
    def replace_curly_braces(match):
        content = match.group(1)
        placeholder = f"__PLACEHOLDER_{len(placeholders)}__"
        placeholders[placeholder] = content
        return placeholder
    
    pattern = re.sub(r'\{(.*?)\}', replace_curly_braces, pattern)
    
    # Escape special regex characters outside curly braces
    pattern = re.sub(f'([{re.escape(special_chars)}])', escape_special, pattern)
    
    # Replace placeholders with their original content
    for placeholder, content in placeholders.items():
        pattern = pattern.replace(placeholder, content)
    
    return pattern

# Test the translator
test_patterns = [
    "MyClass::MyMethod{.*}",
    "vector<int>{*}& func(int{+} a, char{*} b)",
    "template<typename T> class MyTemplate{.*}",
]

for test_pattern in test_patterns:
    regex_pattern = translate_to_regex(test_pattern)
    print(f"Original: {test_pattern}")
    print(f"Translated: {regex_pattern}")
    print()