from pathlib import Path
from .utils import load_examples
from .review import review_code

here = Path(__file__).parent


import pdb






from switchai import SwitchAI
from switchai.types import ChatResponse
from easyrepl import REPL
from typing import Generator, Callable
from functools import partial

no_op = lambda: None
def stream_do(gen:Generator[ChatResponse, None, None], fn: Callable[[str], None], final:Callable[[], None]=no_op) -> str:
    """
    Perform some action while streaming LLM messages, and then return the whole result as a string.
    
    Args:
        gen (Generator[ChatResponse, None, None]): The generator yielding chat responses.
        fn (Callable[[str], None]): A function to call for each message content.
        final (Callable[[], None], optional): A final function to call after all messages have been processed. Defaults to no-op
    
    Returns:
        str: The full combined output from the streamed messages.
    """
    chunks = []
    for i in gen:
        if content:=i.message.content:
            fn(content)
            chunks.append(content)
    final()
    return ''.join(chunks)




def test_switch():
    client = SwitchAI(provider="openai", model_name="gpt-4o")
    messages = []
    for query in REPL(history_file='.chat'):
        messages.append({"role": "user", "content": query})
        gen = client.chat(messages, stream=True)
        res = stream_do(gen, partial(print, end='', flush=True), print)
        messages.append({"role": "assistant", "content": res})


def test_example():
    examples = load_examples(here/'../examples/cbioportal_examples.yaml')
    pdb.set_trace()
    ...


def test_review():
    from .display import explain_code
    examples = load_examples(here/'../examples/gdc_examples.yaml')
    example = examples[0]
    spans = review_code(example)
    explain_code(example['code'], spans)
    
    # print('-'*120)
    # for span in spans:
    #     selection = example['code'][span.start:span.stop]
    #     print(f'```\n{selection}\n```\n\nReason: {span.reason}\n')



if __name__ == '__main__':
    # test_switch()
    # test_example()
    test_review()
