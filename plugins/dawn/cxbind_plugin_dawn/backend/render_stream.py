import textwrap


class RenderStream:
    def __init__(self) -> None:
        self.indentation = 0
        self.text = ""

    def write(self, text: str) -> None:
        self.text += text

    def write_indented(self, text: str) -> None:
        self.write(" " * self.indentation * 4)
        self.write(text)

    def __call__(self, text: str = ""):
        if len(text):
            text = textwrap.dedent(text)
            text = text.split("\n")
            for line in text:
                self.write_indented(line)
                self.write("\n")
        return self

    def __lshift__(self, text: str):
        if len(text):
            self.write_indented(text)
        return self

    def __enter__(self):
        self.indent()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dedent()

    def indent(self):
        self.indentation += 1

    def dedent(self):
        self.indentation -= 1
