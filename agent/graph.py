"""LangGraph workflow wiring and top-level runner."""

from langgraph.graph import END, START, StateGraph

from agent.config import MAX_ITERATIONS
from agent.github_ops import create_pr
from agent.models import GraphState
from agent.nodes import generate_solution, initialize_state, test_solution


def after_generate(state: GraphState) -> str:
    """Determine next step based on status after generation."""
    if state["status"] == "generated":
        return "test"
    if state["iterations"] < MAX_ITERATIONS:
        return "generate"
    return "end"


def should_continue(state: GraphState) -> str:
    """Determine next step after testing."""
    if state["status"] == "tested":
        return "continue"
    if state["status"] == "failed" and state["iterations"] < MAX_ITERATIONS:
        return "generate"
    return "end"


def create_agent(github_token: str, repo_name: str):
    """Build and compile the LangGraph state machine."""
    workflow = StateGraph(GraphState)
    workflow.add_node("generate", generate_solution)
    workflow.add_node("test", test_solution)
    workflow.add_node("create_pr", create_pr)

    workflow.add_edge(START, "generate")

    workflow.add_conditional_edges(
        "generate",
        after_generate,
        {"test": "test", "generate": "generate", "end": END},
    )

    workflow.add_conditional_edges(
        "test",
        should_continue,
        {"generate": "generate", "continue": "create_pr", "end": END},
    )

    workflow.add_edge("create_pr", END)
    return workflow.compile()


def run_agent(github_token: str, repo_name: str):
    """Run the agent to generate and submit a solution."""
    try:
        agent = create_agent(github_token, repo_name)
        initial_state = initialize_state(github_token, repo_name)
        initial_state["repo_name"] = repo_name
        initial_state["github_token"] = github_token

        if initial_state["status"] == "failed":
            print(
                f"Failed to initialize agent: "
                f"{initial_state.get('error_message', 'Unknown error during initialization')}"
            )
            return {"status": "failed"}

        result = agent.invoke(initial_state)

        if result["status"] == "completed":
            print("Successfully created PR with solution!")
        else:
            print(
                f"Failed to create solution: "
                f"{result.get('error_message', 'No specific error message provided.')}"
            )

        return {
            "status": result["status"],
            "generation": result["generation"].code if result.get("generation") else None,
            "pr_url": result.get("pr_url"),
            "error_message": result.get("error_message"),
        }

    except Exception as e:
        print(f"Agent execution failed unexpectedly: {str(e)}")
        return {"status": "failed", "error_message": f"Agent execution failed unexpectedly: {str(e)}"}
