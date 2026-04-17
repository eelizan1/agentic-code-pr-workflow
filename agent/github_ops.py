"""GitHub and Git operations: clone repositories, read tasks, open pull requests."""

import os
import shutil
from datetime import datetime

from git import Repo
from github import Auth, Github
from github.GithubException import GithubException

from agent.models import GraphState


def _unique_branch_name(gh_repo, base_name: str) -> str:
    """Return a branch name that doesn't already exist on the remote."""
    try:
        gh_repo.get_branch(base_name)
    except GithubException:
        return base_name
    suffix = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    return f"{base_name}-{suffix}"


def clone_repository(github_token: str, repo_name: str) -> tuple[str, str]:
    """Clone the repository and return the local directory."""
    try:
        script_dir = os.getcwd()
        repo_dir = os.path.join(script_dir, "agent-task")

        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)

        g = Github(auth=Auth.Token(github_token))
        repo = g.get_repo(repo_name)
        Repo.clone_from(repo.clone_url, repo_dir)
        return repo_dir, ""
    except Exception as e:
        return "", f"Repository setup failed: {str(e)}"


def read_task_file(repo_dir: str) -> tuple[str, str]:
    """Read the task markdown file."""
    try:
        task_path = os.path.join(repo_dir, "task.md")
        with open(task_path, "r") as f:
            return f.read(), ""
    except Exception as e:
        return "", f"Failed to read task: {str(e)}"


def create_pr(state: GraphState):
    """Commit the generated code to a new branch and open a pull request."""
    try:
        repo = Repo(state["repo_dir"])
        github_token = state["github_token"]
        repo_name = state["repo_name"]

        g = Github(auth=Auth.Token(github_token))
        gh_repo = g.get_repo(repo_name)

        branch_name = _unique_branch_name(gh_repo, state["generation"].branch_name)

        auth_url = f"https://{github_token}@github.com/{repo_name}.git"
        repo.remotes.origin.set_url(auth_url)

        if branch_name not in repo.heads:
            repo.git.checkout("-b", branch_name)
        else:
            repo.git.checkout(branch_name)

        file_path = os.path.join(state["repo_dir"], state["generation"].file_path)
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        with open(file_path, "w") as f:
            f.write(state["generation"].code)

        repo.git.add(A=True)
        repo.index.commit(state["generation"].commit_message)

        repo.remotes.origin.push(branch_name)

        pr = gh_repo.create_pull(
            title=state["generation"].pr_title,
            body=state["generation"].pr_description,
            head=branch_name,
            base="main",
        )

        print(f"Created PR: {pr.html_url}")

        return {
            **state,
            "status": "completed",
            "pr_url": pr.html_url,
        }

    except Exception as e:
        print(f"PR creation failed: {e}")
        return {
            **state,
            "status": "failed",
            "error_message": f"PR creation failed: {str(e)}",
        }
