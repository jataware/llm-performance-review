from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns

# from dataclasses import dataclass

# @dataclass
# class Span:
#     start: int
#     end: int
#     explanation: str

from .utils import Span



def explain_code(source_code: str, spans: list[Span]):
    """
    Displays source code with highlighted spans and explanations.
    """
    console = Console()

    # Sort spans so we don’t mess up indexes when inserting highlights
    spans = sorted(spans, key=lambda x: x.start)

    # Create a plain Text object with syntax highlighting
    syntax = Syntax(source_code, "python", theme="monokai", line_numbers=True, word_wrap=True)
    code_text = Text.from_markup(syntax.highlight(source_code).plain)

    # Apply color highlights to spans
    colors = ["on red", "on green", "on yellow", "on cyan", "on magenta", "on blue"]
    labels = []

    for i, span in enumerate(spans):
        label = f"[{i + 1}]"
        color = colors[i % len(colors)]

        # highlight the selection in the code
        code_text.stylize(color, span.start, span.stop)
        labels.append((label, color, span.reason))

    # Left panel: highlighted code
    code_panel = Panel(code_text, title="Source Code", border_style="blue")

    # Right panel: explanations
    explanation_text = Text()
    for label, color, expl in labels:
        explanation_text.append(f"{label}", style=color)
        explanation_text.append(f" {expl}\n", style="white")

    explanation_panel = Panel(explanation_text, title="Explanations", border_style="green")

    # Display side by side
    console.print(Columns([code_panel, explanation_panel]))

if __name__ == "__main__":
    # Example 1
    code = '''
    def greet(name):
        print(f"Hello, {name}!")
    greet("Alice")
    '''

    spans = [
        Span(5, 21, "Defines a function called greet"),
        Span(30, 54, "Prints a greeting using an f-string"),
        Span(59, 74, "Calls the greet function with 'Alice'"),
    ]

    explain_code(code, spans)


    # Example 2
    code = """\
def add(a, b):
    return a + b
    """

    spans = [
        Span(4, 7, "This is the name of the function"),
        Span(8, 9, "This is the first parameter 'a'"),
        Span(11, 12, "This is the second parameter 'b'"),
        Span(19, 31, "This is the result"),
    ]
    explain_code(code, spans)
