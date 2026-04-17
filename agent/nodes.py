"""Graph node implementations: initialize, generate, test."""

import time
import traceback

from anthropic import APIConnectionError, APITimeoutError
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from agent.config import ANTHROPIC_API_KEY, ANTHROPIC_MAX_TOKENS, ANTHROPIC_MODEL
from agent.github_ops import clone_repository, read_task_file
from agent.models import CodeSolution, GraphState

_TRANSIENT_NETWORK_ERRORS = (APIConnectionError, APITimeoutError)
_NETWORK_RETRIES = 3
_NETWORK_BACKOFF_SECONDS = 2.0


def _invoke_with_network_retry(chain, payload):
    """Retry the chain on transient network errors with exponential backoff."""
    last_exc: Exception | None = None
    for attempt in range(1, _NETWORK_RETRIES + 1):
        try:
            return chain.invoke(payload)
        except _TRANSIENT_NETWORK_ERRORS as e:
            last_exc = e
            if attempt == _NETWORK_RETRIES:
                break
            delay = _NETWORK_BACKOFF_SECONDS * (2 ** (attempt - 1))
            print(
                f"Network error ({type(e).__name__}); retrying in {delay:.1f}s "
                f"(attempt {attempt}/{_NETWORK_RETRIES})"
            )
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc


def initialize_state(github_token: str, repo_name: str) -> dict:
    """Initialize the workflow state by cloning the repo and reading task.md."""
    repo_dir, error = clone_repository(github_token, repo_name)
    if error:
        return {
            "status": "failed",
            "task_content": "",
            "repo_dir": "",
            "generation": None,
            "iterations": 0,
            "error_message": error,
        }

    task_content, error = read_task_file(repo_dir)
    if error:
        return {
            "status": "failed",
            "task_content": "",
            "repo_dir": repo_dir,
            "generation": None,
            "iterations": 0,
            "error_message": error,
        }

    return {
        "status": "ready",
        "task_content": task_content,
        "repo_dir": repo_dir,
        "generation": None,
        "iterations": 0,
        "error_message": None,
    }


def generate_solution(state: GraphState):
    """Generate code solution based on task description."""
    current_iterations = state.get("iterations", 0) + 1
    print(f"Generating solution - Attempt #{current_iterations}")

    task_content = state["task_content"]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a Python developer. Generate a solution based on the task requirements.
        Include complete code with imports, type hints, docstring, and examples.
        Also provide a suggested branch name, file path relative to the repository root, a concise commit message,
        a title for the pull request, and a detailed description for the pull request.
        The file path should be a Python file, e.g., 'src/my_solution.py'.""",
            ),
            ("human", "Task description:\n{task}"),
        ]
    )

    try:
        llm = ChatAnthropic(
            model=ANTHROPIC_MODEL,
            temperature=0,
            max_tokens=ANTHROPIC_MAX_TOKENS,
            anthropic_api_key=ANTHROPIC_API_KEY,
        )
        chain = prompt | llm.with_structured_output(CodeSolution)

        solution = _invoke_with_network_retry(chain, {"task": task_content})

        for attr in ["branch_name", "file_path", "commit_message", "pr_title", "pr_description"]:
            if not hasattr(solution, attr) or getattr(solution, attr) is None or getattr(solution, attr) == "":
                raise ValueError(f"Generated CodeSolution missing or empty required attribute: '{attr}'")

        return {
            **state,
            "status": "generated",
            "generation": solution,
            "iterations": current_iterations,
            "error_message": None,
        }
    except Exception as e:
        print(f"Generation failed on attempt #{current_iterations}: {type(e).__name__}: {e}")
        traceback.print_exc()
        cause = getattr(e, "__cause__", None) or getattr(e, "__context__", None)
        if cause is not None:
            print(f"Underlying cause: {type(cause).__name__}: {cause}")
        return {
            **state,
            "status": "failed",
            "iterations": current_iterations,
            "error_message": f"Solution generation failed: {type(e).__name__}: {e}",
        }


def test_solution(state: GraphState):
    """Test the generated code solution against the task-specific test cases."""
    if state["status"] != "generated" or not state["generation"]:
        return {
            **state,
            "status": "failed",
            "error_message": state.get("error_message")
            or "Cannot test solution: not generated or no generation found.",
        }

    try:
        namespace: dict = {}
        exec(state["generation"].code, namespace)

        if "uncompress" not in namespace:
            return {
                **state,
                "status": "failed",
                "error_message": "Test failed: 'uncompress' function not found in generated code.",
            }

        test_cases = [
            ("2c3a1t", "ccaaat"),
            ("4s2b", "ssssbb"),
            ("2p1o5p", "ppoppppp"),
            ("3n12e2z", "nnneeeeeeeeeeeezz"),
            ("127y", "y" * 127),
        ]

        for input_str, expected_output in test_cases:
            result = namespace["uncompress"](input_str)
            if result != expected_output:
                return {
                    **state,
                    "status": "failed",
                    "error_message": (
                        f"Test failed for input '{input_str}': "
                        f"Expected '{expected_output}', got '{result}'"
                    ),
                }

        return {**state, "status": "tested", "error_message": None}

    except Exception as e:
        return {**state, "status": "failed", "error_message": f"Test execution failed: {str(e)}"}
