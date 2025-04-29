import re

def translate_to_regex(pattern: str) -> str:
    special_chars = '.^$*+?{}[]\\|()'

    # Escape everything except for {...} sections
    regex_parts = []
    pos = 0
    for match in re.finditer(r'\{(.*?)\}', pattern):
        start, end = match.span()
        raw_regex = match.group(1)

        # Escape up to the start of this match
        chunk = pattern[pos:start]
        chunk = re.sub(f'([{re.escape(special_chars)}])', r'\\\1', chunk)
        regex_parts.append(chunk)

        # Add the raw regex without escaping
        regex_parts.append(f'(?:{raw_regex})')
        pos = end

    # Escape the remainder
    chunk = pattern[pos:]
    chunk = re.sub(f'([{re.escape(special_chars)}])', r'\\\1', chunk)
    regex_parts.append(chunk)

    return ''.join(regex_parts)

# ✅ Tests
test_patterns = [
    "MyClass::MyMethod{.*}",
    "vector<int>{.*}& func(int{\\+} a, char{.*} b)",
    "template<typename T> class MyTemplate{.*}",
    "SkCanvas::experimental_{.*}",
]

for test_pattern in test_patterns:
    regex_pattern = translate_to_regex(test_pattern)
    print(f"Original:   {test_pattern}")
    print(f"Translated: {regex_pattern}")
    print()

# ✅ Usage example
pattern = "SkCanvas::experimental_{.*}"
regex = re.compile(translate_to_regex(pattern))

if regex.match("SkCanvas::experimental_blend"):
    print("Matched!")
else:
    print("Not matched!")
