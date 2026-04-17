"""Entry point for the agentic code PR workflow."""

from agent.config import GITHUB_TOKEN, REPO_NAME, require_env
from agent.graph import run_agent


def main() -> None:
    require_env()

    result = run_agent(GITHUB_TOKEN, REPO_NAME)

    if result["status"] == "completed":
        print("\nSolution generated successfully!")
        if result.get("pr_url"):
            print(f"\nPull Request created at: {result['pr_url']}")
        if result.get("generation"):
            print("\nGenerated Code:")
            print(result["generation"])
    else:
        print("\nFailed to generate solution")
        if result.get("error_message"):
            print(f"Error: {result['error_message']}")


if __name__ == "__main__":
    main()
