import textwrap


class RenderStream:
    def __init__(self, indentation: int = 0) -> None:
        self.indentation = indentation
        self.text = ""

    @property
    def nl(self) -> str:
        return "\n"

    def inject(self, other: "RenderStream") -> "RenderStream":
        self.text += other.text
        return self

    def write(self, text: str) -> None:
        self.text += text

    def write_indent(self) -> None:
        self.write(" " * self.indentation * 4)

    def write_indented(self, text: str) -> None:
        #self.write(" " * self.indentation * 4)
        self.write_indent()
        self.write(text)

    def __call__(self, text: str = ""):
        if len(text):
            text = textwrap.dedent(text)
            text = text.split("\n")
            for line in text:
                self.write_indented(line)
                self.write("\n")
        else:
            self.write("\n")
        return self

    """
    def __lshift__(self, text: str):
        if len(text):
            self.write_indented(text)
        return self
    """

    def __lshift__(self, text: str):
        if len(text):
            self.write(text)
        return self

    def __floordiv__(self, text: str):
        if len(text):
            self.write_indented(text)
        return self

    def __enter__(self):
        self.indent()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dedent()

    def indent(self):
        self.indentation += 1

    def dedent(self):
        self.indentation -= 1
