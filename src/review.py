# from switchai import SwitchAI
from .utils import Example, VagueSpan, Span, serialize_span, deserialize_span, vectorize, pinpoint_span, add_line_numbers
from .cache import diskcache

from archytas.tool_utils import tool
from archytas.react import ReActAgent
# from archytas.agent import Message, Role
from langchain_core.messages import HumanMessage
from pathlib import Path


here = Path(__file__).parent

import pdb


review_tasks = [
    'Identify all constrained parameters in the code. constrained parameters in this context are any parameters that were selected either explicitly or implicitly that are somehow indicated by the original query. Parameters in this context means anything that would affect the output from the code were it changed, think function arguments, api request parameters, other various settings, etc.',
    'Identify all free parameters in the code. This is the opposite of constrained, i.e. query does not mention or touch on them implicitly or explicitly, and so the code is directly making an assumption about what they should be',
    'Is there anything the code does that a domain expert would take issue with? Assume said expert was the one who made the original query. This is less about things like the structuring or software design, and more about the particular approach the code takes to solve the task',
    'In this program do you see any potential bugs? things like:\n- unreachable code\n- logic errors\n- off-by-one errors\n- out of bounds\n- race conditions\n- infinite loops\n- etc.\n\n',
    'Based on the kinds of examples of code issues, are there any other issues in the code that you should to point out?',

    # <TODO: pull other tasks from document>
]


# REVIEW_PROMPT = """\
# You are an expert code reviewer. You will be provided with a piece of code (and the user query that the code is attempting to solve). You will be tasked with identifying portions of the code that match some specific criteria. Your output for each task will be a list of spans that indicate which parts of the code you have selected, along with a brief explanation of the reasoning your selection. The format for a span is as follows:
#     start_line: int  # The line number on which the span starts. The provided code will include line numbers for you to reference
#     quote: str  # A verbatim string of the entire portion code that you are selecting
#     reason: str  # A brief explanation of why you selected this span

    
# So when you are given a task on some code, you will respond with a list of spans
# """

class CodeReview:
    def __init__(self, example: Example):
        self.example = example
        self.spans: list[Span] = []
    
    @tool
    def add_span(self, start_line:int, quote: str, reason: str) -> bool:
        """
        Identify a span of code that matches the given criteria, and save it to the list of spans.

        Args:
            start_line (int): The line number on which the span starts (use line numbers as they appear in the code)
            quote (str): A verbatim string of the entire portion of code that you are selecting. Do not include line numbers in this quote
            reason (str): A brief explanation of why you selected this span
        
        Returns:
            bool: returns True if the span was successfully added
        """
            # TBD if tell the agent this below, perhaps pinpoint span will check against both versions
            # Note: the code quote should not include the line numbers
        span = VagueSpan(start_line=start_line, quote=quote, reason=reason)
        span = pinpoint_span(span, self.example['code'])
        self.spans.append(span)
        return True
    

    # @tool
    def view_code(self) -> str:
        """
        View the source code being reviewed
        
        Returns:
            str: The source code (with line numbers included for reference)
        """
        return add_line_numbers(self.example['code'])
        


@diskcache(serializer=vectorize(serialize_span), deserializer=vectorize(deserialize_span))
def review_code(example: Example) -> list[Span]:
    task0 = review_tasks[0]
    review = CodeReview(example)
    tools = [review]
    prompt_message = HumanMessage(content=f'''\
You are an expert code reviewer. Your job is to identify various assumptions or deficiencies in given pieces of code.
Here is a large collection of the kinds of issues you should be looking for: 
{(here / 'code-issues-examples.md').read_text()}


{'-'*80}

In general, I will give you a piece of code, the task that the code was attempting to complete, and a specific direction for the kind of issues to look for. At a high level, the goal is to identify sections that might need review from a domain expert.
''')
    agent = ReActAgent(model='gpt-4o', tools=tools, messages=[prompt_message], allow_ask_user=False, verbose=False)
    res = agent.react(f'''\
Please review the following code
                
Code:
```python
# Query: {example['query']}

{add_line_numbers(example['code'])}
```

Task:
{task0}

Please use the CodeReview.add_span tool to indicate your selections.
''')
    # print(res)
    for taskN in review_tasks[1:]:
        res = agent.react(f'''\
Now I would like you to review the code again (select spans) for this task:
{taskN}
''')
        # print(res)
    return review.spans

    # # print out the result
    # for span in review.spans:
    #     print(f'Span:\n```\n{example["code"][span.start:span.stop]}\n```\n\nReason: {span.reason}\n')
    
    # client = SwitchAI(provider="openai", model_name="gpt-4o")
    # lined_code = add_line_numbers(example['code'])
    # res = client.chat()
    # run through each of the review steps which return spans in the code
    pdb.set_trace()
    ...