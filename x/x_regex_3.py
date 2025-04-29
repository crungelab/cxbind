import re

def translate_to_regex(pattern: str) -> str:
    # Step 1: extract raw regex sections in {}
    raw_sections = []
    def extract_raw(match):
        raw = match.group(1)
        placeholder = f"__RAW_{len(raw_sections)}__"
        raw_sections.append(raw)
        return placeholder

    pattern = re.sub(r'\{(.*?)\}', extract_raw, pattern)

    # Step 2: Escape and translate glob syntax
    def escape_and_globify(c):
        if c == '*':
            return '.*'
        elif c == '?':
            return '.'
        elif c in '.^$+{}[]\\|()':
            return '\\' + c
        return c

    pattern = ''.join(escape_and_globify(c) for c in pattern)

    # Step 3: Replace raw sections
    for i, raw in enumerate(raw_sections):
        pattern = pattern.replace(f"__RAW_{i}__", f"(?:{raw})")

    return pattern


from itertools import product

def expand_braces(pattern):
    # Handle simple {a,b} brace expansion
    match = re.search(r'\{([^{}]+)\}', pattern)
    if not match:
        return [pattern]

    prefix = pattern[:match.start()]
    suffix = pattern[match.end():]
    options = match.group(1).split(',')

    results = []
    for opt in options:
        for expanded in expand_braces(prefix + opt + suffix):
            results.append(expanded)
    return results

exclude_patterns = [
    "SkCanvas::experimental_*",
    "SkFoo::{bar,baz}_impl",
    "std::vector<{.*}>",
]

# Expand + translate all patterns
expanded_patterns = []
for pattern in exclude_patterns:
    for expanded in expand_braces(pattern):
        expanded_patterns.append(f"(?:{translate_to_regex(expanded)})")

combined_regex = "|".join(expanded_patterns)
compiled_exclude_regex = re.compile(f"^{combined_regex}$")

# Test again
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
