import re

def translate_to_regex(pattern: str) -> str:
    special_chars = '.^$*+?{}[]\\|()'
    regex_parts = []
    pos = 0
    for match in re.finditer(r'\{(.*?)\}', pattern):
        start, end = match.span()
        raw_regex = match.group(1)
        chunk = pattern[pos:start]
        chunk = re.sub(f'([{re.escape(special_chars)}])', r'\\\1', chunk)
        regex_parts.append(chunk)
        regex_parts.append(f'(?:{raw_regex})')
        pos = end
    chunk = pattern[pos:]
    chunk = re.sub(f'([{re.escape(special_chars)}])', r'\\\1', chunk)
    regex_parts.append(chunk)
    return ''.join(regex_parts)

# List of exclusion patterns
exclude_patterns = [
    "SkCanvas::experimental_{.*}",
    "SkFoo::{bar|baz}_impl",
    "std::vector<{.*}>",
]

# Convert and combine into a single regex
combined_regex = "|".join(f"(?:{translate_to_regex(p)})" for p in exclude_patterns)
compiled_exclude_regex = re.compile(f"^{combined_regex}$")

# ✅ Test
test_symbols = [
    "SkCanvas::experimental_thing",
    "SkCanvas::DrawSomething",
    "SkFoo::bar_impl",
    "SkFoo::baz_impl",
    "std::vector<int>",
    "std::vector<std::string>",
]

for symbol in test_symbols:
    if compiled_exclude_regex.match(symbol):
        print(f"Excluded: {symbol}")
    else:
        print(f"Allowed:  {symbol}")
