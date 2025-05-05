# LLM Performance Review
Automatically evaluating how well an LLM performed a given task in some environment. 


## Problem
Often when working on complicated tasks, LLMs may produce work or key decisions that are questionable and might need review and correction from the human who initiated the task. Usually this will present as a sort of needle mixed into a haystack of the largely correct surrounding work the LLM has done. This often makes it infeasible for the human to review the entire thing due to the volume of content. Some process is needed to bubble up the most critical sections so the human can skip the bulk (which often doesn't require any review), and focus on only what matters.

## Experiment
The goal of this repo is to start exploring how well these "critical-review-sections" can be automatically identified by an agent vs are some review points fundamentally difficult for an LLM to identify.

### Process
The main test involves having an LLM select spans from code for pre-written query+code pairs according to a set of instructions on different things to look for that count as critical review. The current set of example query+code pairs can be found in [examples/](examples/). The specific review tasks indicating what the agent should look for as it goes are outlined here: [src/review.py#L17-L25](src/review.py#L17-L25).

For the main experiment, the agent looks at the selected code+query and for each review task will flag spans that match that criteria. For each selected span, the agent is also prompted to provide an explanation for why it needs review. When done, overlapping spans are merged, and then the selected spans are displayed to the user by highlighting the selections in the terminal and displaying that side-by-side with the corresponding explanations


## How to Use
### Install Dependencies
1. Install uv
    ```bash
    # via curl:
    curl -LsSf https://astral.sh/uv/install.sh | less
    
    # or via pip
    pip install uv
    ```

1. Install dependencies
    ```bash
    # if you know how to use uv
    uv sync
    ```

    > Note: By default, uv creates a local virtual environment it installs into. uv can install into a specific/external environment e.g. a conda environment via environment variable like so:
    ```bash
    conda create -y -n myenv python=3.10
    conda activate myenv
    VIRTUAL_ENV=$(echo $CONDA_PREFIX)
    UV_PROJECT_ENVIRONMENT=$(echo $VIRTUAL_ENV)
    
    # uv should now operate inside the conda env
    # `uv sync` doesn't seem to respect the environment variables
    # so use this command instead
    uv pip sync pyproject.toml
    ```

### Running Experiment
```bash
# from the root of the repo
python -m src.test
```
This will run the currently set up test which pulls in a single example and has the agent analyze and highlight it.

To run different examples, modify the code for selecting which example here:
[src/test.py#L63-L64](src/test.py#L63-L64)