# CodeGen PR Agent

An agentic AI workflow that transforms task specifications into production-ready code and automatically creates pull requests.

## Overview

CodeGen PR Agent is an end-to-end development automation system that leverages large language models (LLMs) to:

- Generate code solutions from task descriptions
- Validate outputs through automated testing
- Manage Git workflows (branching, committing, pushing)
- Create pull requests for review

This project demonstrates how agentic systems can orchestrate real-world software engineering workflows with minimal human intervention.

---

## How It Works

The agent follows a structured pipeline:

1. **Initialize**
   - Clone target repository
   - Load task specification (`task.md`)

2. **Generate**
   - Use LLM to generate code, commit message, and PR details

3. **Test**
   - Execute validation logic on generated code
   - Retry generation on failure (up to N attempts)

4. **Create PR**
   - Create a new branch
   - Write generated code to file
   - Commit and push changes
   - Open a pull request via GitHub API

---

## Architecture

The workflow is orchestrated using a state-driven graph:

```
START → Generate → Test → (Retry or Continue) → Create PR → END
```

- **State Management**: Tracks task, generation output, retries, and repo metadata
- **LLM Integration**: Supports Anthropic or Hugging Face models
- **Git Automation**: Uses GitPython for local operations
- **PR Creation**: Uses GitHub API for pull request creation

---

## Project Structure

```
.
├── agent.ipynb               # Main agent workflow (Colab/Jupyter)
├── task.md                   # Task input specification
├── array_products.py         # Generated solution (example)
├── test_array_products.py    # Generated tests (example)
└── README.md
```

---

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/<your-username>/codegen-pr-agent.git
cd codegen-pr-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file:

```env
GITHUB_TOKEN=your_github_token
ANTHROPIC_API_KEY=your_anthropic_key   # optional
HF_TOKEN=your_huggingface_token        # optional
```

---

## Usage

Run the agent from your notebook or script:

```python
run_agent(GITHUB_TOKEN, "your-username/your-repo")
```

Expected outcome:

- ✅ Code is generated and validated
- ✅ A new branch is created
- ✅ Changes are committed and pushed
- ✅ A pull request is opened automatically

---

## Example Task

```markdown
# Array Product Calculator

Create a function that returns the product of all elements except itself for each index.
```

---

## Key Features

- ⚡ Automated code generation from natural language tasks
- 🔁 Built-in retry mechanism for failed generations
- 🔧 End-to-end Git workflow automation
- 🔌 Pluggable LLM providers (Anthropic, Hugging Face)
- 📐 Structured output validation using schemas

---

## Future Improvements

- [ ] Multi-file project support
- [ ] More robust test generation
- [ ] CI/CD integration
- [ ] Multi-agent collaboration (planner + executor)
- [ ] Model fallback strategies

---

## Use Cases

- Automating repetitive development tasks
- Rapid prototyping from specs
- AI-assisted code review workflows
- Developer productivity tooling
