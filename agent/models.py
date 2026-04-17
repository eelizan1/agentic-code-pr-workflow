"""Pydantic schemas and typed state for the agent workflow."""

from typing import Optional, TypedDict

from pydantic import BaseModel, Field


class CodeSolution(BaseModel):
    """Schema for code solutions."""

    description: str = Field(description="Description of the solution approach")
    code: str = Field(description="Complete code including imports and docstring")
    branch_name: str = Field(
        description="Suggested branch name for the new feature or fix (e.g., 'feat/array-products-calculator')."
    )
    file_path: str = Field(
        description="Path relative to the repository root where the code should be saved (e.g., 'array_products.py')."
    )
    commit_message: str = Field(
        description="Commit message for the changes (e.g., 'feat: add array products calculator')."
    )
    pr_title: str = Field(
        description="Title for the pull request (e.g., 'Add Array Products Calculator')."
    )
    pr_description: str = Field(
        description="Detailed description for the pull request, including the solution approach and any relevant context."
    )


class GraphState(TypedDict, total=False):
    """State for the task processing workflow."""

    status: str
    task_content: str
    repo_dir: str
    generation: Optional[CodeSolution]
    iterations: int
    error_message: Optional[str]
    repo_name: str
    pr_url: str
    github_token: str
