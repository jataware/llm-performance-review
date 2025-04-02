from dataclasses import dataclass
from typing import Annotated
from typing_extensions import NotRequired, TypedDict
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import pydantic
import pdb




class Example(TypedDict):
    query: Annotated[str, 'The user query that is solved by this example.']
    code: Annotated[str, 'The code that solves the example.']
    notes: NotRequired[Annotated[str, 'Optional notes about the example.']]

def load_examples(path:Path) -> list[Example]:
    with path.open('r') as f:
        examples: list[Example] = yaml.load(f, Loader=SafeLoader)
    if not isinstance(examples, list):
        raise ValueError(f"Loaded examples from {path} is not a list of examples. Found: {type(examples)}")
    pydantic.TypeAdapter(list[Example]).validate_python(examples)
    return examples



"""
how the llm will identify spans:
- start line that the content starts on
- a verbatim string of the content it wants to highlight
"""
@dataclass
class VagueSpan:
    start_line: int
    quote: str
    reason: str


@dataclass
class Span:
    start: int
    stop: int
    reason: str


def pinpoint_span(vague_span:VagueSpan, content:str, match_tolerance:float=0.9) -> Span:
    """
    Convert a vague span (given by an LLM) into a concrete span for the given content.
    > Note: ideally the vague span's quote would be an exact substring within content,
    >       however this function can tolerate minor mismatches

    Args:
        vague_span (VagueSpan): The vague span with start line and quote of the content to highlight.
        content (str): The full content over which to resolve the span.
        match_tolerance (float, optional): percentage (from 0.0 to 1.0) of how closely the quote must match the content. Defaults to 0.9.
    Returns:
        Span: A concrete span with start and stop indices.
    """
    lines = content.splitlines()
    start_line = vague_span.start_line - 1
    prefix = '\n'.join(lines[:start_line])  # everything before the start line
    subset = '\n'.join(lines[start_line:])  # everything from the start line onwards
    
    # TODO: better more tolerant matching here
    subset_start = subset.find(vague_span.quote)
    if subset_start == -1:
        raise ValueError(f"Quote not found in content starting from line {vague_span.start_line}: {vague_span.quote!r}. Specified start line's content is {lines[start_line]!r}")
    
    start = len(prefix) + subset_start + int(start_line > 0)
    stop = start + len(vague_span.quote)
    return Span(start=start, stop=stop, reason=vague_span.reason)



def add_line_numbers(program:str) -> str:
    """Add line numbers to a program. Line numbers start at 1"""
    start_index = 1 # this probably shouldn't be configurable. Best LLM performance was observed with 1-based line numbers
    lines = program.splitlines()
    width = len(str(len(lines) + start_index - 1)) # maximum width of the line numbers being added
    return '\n'.join([f"{i:>{width}}| {line}" for i, line in enumerate(lines, start_index)])
