# from switchai import SwitchAI
from .utils import Example, VagueSpan, Span, pinpoint_span, add_line_numbers
from archytas.tool_utils import tool
from archytas.react import ReActAgent

import pdb


review_tasks = [
    'Identify all constrained parameters in the code. constrained parameters in this context are any parameters that were selected either explicitly or implicitly that are somehow indicated by the original query. Parameters in this context means anything that would affect the output from the code were it changed, think function arguments, api request parameters, other various settings, etc.',
    'Identify all free parameters in the code. This is the opposite of constrained, i.e. query does not mention or touch on them implicitly or explicitly, and so the code is directly making an assumption about what they should be',
    'Is there anything the code does that a domain expert would take issue with? Less about things like the structuring or software design, and more about the particular approach the code takes to solve the task.',
    'In this program do you see any potential bugs? things like:\n- unreachable code\n- logic errors\n- off-by-one errors\n- out of bounds\n- race conditions\n- infinite loops\n- etc.\n\n',
    'Do you see any faulty assumptions in the code?'

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
    def add_span(self, span: VagueSpan) -> bool:
        """
        Identify a span of code that matches the given criteria, and save it to the list of spans.

        Args:
            span (VagueSpan): A span object containing the start line `start_line`, code quote `quote`, and reasoning `reason` for selection. 
        
        Returns:
            bool: returns True if the span was successfully added
        """
            # TBD if tell the agent this below, perhaps pinpoint span will check against both versions
            # Note: the code quote should not include the line numbers
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
        
    

def review_code(example: Example) -> list[Span]:
    task0 = review_tasks[0]
    review = CodeReview(example)
    tools = [review]
    agent = ReActAgent(model='gpt-4o', tools=tools, allow_ask_user=False, verbose=False)
    res = agent.react(f'''\
I have the following piece of code that I would like your help reviewing. At a high level, our goal it to identify portions of the code that we might want a domain expert to review.
                
Code:
```python
# Query: {example['query']}

{add_line_numbers(example['code'])}
```

Task:
{task0}

Please use the CodeReview.add_span tool to indicate your selections.
''')
    print(res)
    for taskN in review_tasks[1:]:
        res = agent.react(f'''\
Now I would like you to review the code again (select spans) for this task:
{taskN}
''')
        print(res)

    # print out the result
    for span in review.spans:
        print(f'Span:\n```\n{example["code"][span.start:span.stop]}\n```\n\nReason: {span.reason}\n')
    
    # client = SwitchAI(provider="openai", model_name="gpt-4o")
    # lined_code = add_line_numbers(example['code'])
    # res = client.chat()
    # run through each of the review steps which return spans in the code
    pdb.set_trace()
    ...