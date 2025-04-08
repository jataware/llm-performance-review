from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table


from .utils import Span

import pdb


def explain_code(source_code: str, spans: list[Span]):
    """
    Displays source code with highlighted spans and explanations.
    """
    # handle merging any overlapping spans
    spans = handle_overlaps(spans)

    console = Console()

    # Sort spans so we don’t mess up indexes when inserting highlights
    spans = sorted(spans, key=lambda x: x.start)

    # Create a plain Text object with syntax highlighting
    syntax = Syntax(source_code, "python", theme="monokai", line_numbers=True, word_wrap=True)
    code_text = Text.from_markup(syntax.highlight(source_code).plain)

    # Apply color highlights to spans
    colors = ["on red", "on green", "on yellow", "on cyan", "on magenta", "on blue"]
    labels: list[tuple[str, str, str]] = []

    for i, span in enumerate(spans):
        label = f"[{i + 1}]"
        color = colors[i % len(colors)]

        # highlight the selection in the code
        code_text.stylize(color, span.start, span.stop)
        labels.append((label, color, span.reason))

    # Left panel: highlighted code
    code_panel = Panel(code_text, title="Source Code", border_style="blue")

    # Right panel: explanations using a table for indentation
    explanation_table = Table(show_header=False, box=None, padding=(1, 1, 0, 0))
    explanation_table.add_column("Label", width=len(str(len(spans)))+2, style="bold", justify="right")
    explanation_table.add_column("Explanation", style="white", overflow="fold")

    for label, color, expl in labels:
        explanation_table.add_row(Text(f'{label}', style=color), Text(f'{expl}'))

    explanation_panel = Panel(explanation_table, title="Explanations", border_style="green")

    # Display side by side
    console.print(Columns([code_panel, explanation_panel]))


def merge_spans(left: Span, right: Span) -> Span:
    """Merges two spans into one."""
    return Span(
        min(left.start, right.start),
        max(left.stop, right.stop),
        f'{left.reason}\n{"-" * 80}\n{right.reason}',
    )

def handle_overlaps(spans: list[Span]) -> list[Span]:
    # repeat span merging until there are no more overlaps
    n_spans = len(spans)
    while True:
        spans=_handle_overlaps(spans)
        if len(spans) == n_spans:
            break
        n_spans = len(spans)
    return spans

def _handle_overlaps(spans: list[Span]) -> list[Span]:
    """
    Merges spans that overlap the exact same or almost exact range.
    """
    spans = sorted(spans, key=lambda x: (x.start, x.stop))

    i = 0
    while i < len(spans) - 1:
        left = spans[i]
        right = spans[i + 1]


        # # if the spans are identical
        # if left.start == right.start and left.stop == right.stop:
        #     spans[i] = merge_spans(left, right)
        #     del spans[i + 1]
        #     continue

        # # if the overlap is close enough
        # dstart = abs(left.start - right.start)
        # dstop = abs(left.stop - right.stop)
        # overlap = abs(min(left.stop, right.stop) - max(left.start, right.start))
        # if (dstart + dstop) / overlap < 0.1:
        #     spans[i] = merge_spans(left, right)
        #     del spans[i + 1]
        #     continue

        # if right is completely inside the left, it's ok
        if left.start < right.start and left.stop > right.stop:
            i += 1
            continue
        # if right.start < left.start and right.stop > left.stop:
        #     # i += 2
        #     j += 1
        #     continue
        
        # in the case of any overlap at all
        # TODO: for now just merge them, but probably want something better...
        if left.start <= right.start and left.stop >= right.start:
            spans[i] = merge_spans(left, right)
            del spans[i + 1]
            continue

        # otherwise the spans should have no overlap
        i += 1

    return spans






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
