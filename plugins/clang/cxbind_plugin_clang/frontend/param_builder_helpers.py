def _find_matching_angle(s: str, lt: int) -> int:
    depth = 0
    for i in range(lt, len(s)):
        if s[i] == "<":
            depth += 1
        elif s[i] == ">":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _split_template_args(arg_str: str) -> list[str]:
    args: list[str] = []
    depth = 0
    start = 0
    for i, c in enumerate(arg_str):
        if c == "<":
            depth += 1
        elif c == ">":
            depth -= 1
        elif c == "," and depth == 0:
            args.append(arg_str[start:i].strip())
            start = i + 1
    tail = arg_str[start:].strip()
    if tail:
        args.append(tail)
    return args


def _outer_template_args(spelling: str) -> list[str] | None:
    lt = spelling.find("<")
    if lt == -1:
        return None
    gt = _find_matching_angle(spelling, lt)
    if gt == -1:
        return None
    return _split_template_args(spelling[lt + 1 : gt])


def _replace_outer_template_args(fq: str, resolved_args: list[str]) -> str:
    lt = fq.find("<")
    if lt == -1:
        return fq
    gt = _find_matching_angle(fq, lt)
    if gt == -1:
        return fq

    fq_args = _split_template_args(fq[lt + 1 : gt])
    out_args = fq_args[:]
    for i in range(min(len(out_args), len(resolved_args))):
        out_args[i] = resolved_args[i]

    return f"{fq[:lt]}<{', '.join(out_args)}>{fq[gt + 1:]}"
