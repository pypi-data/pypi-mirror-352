# Git<ins>Ai</ins>d: AI-powered Git Productivity Tool from [MayaAI](https://github.com/mayaailabs)

[![PyPI version](https://img.shields.io/pypi/v/gitaid)](https://pypi.org/project/gitaid/)
[![License](https://img.shields.io/pypi/l/gitaid)](https://github.com/mayaailabs/gitaid/blob/main/LICENSE.txt)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/mayaailabs/gitaid)

Supercharge your developer workflow with **GitAid** — the AI-powered companion for Git that generates intelligent commit messages, explains your changes, and streamlines your git CLI productivity.

---

## Features

- **AI-generated commit messages:** Instantly create clear, context-aware commit messages for your staged changes with one command.
- **Code review explanations:** Get professional, readable explanations of your staged Git changes using advanced AI.
- **Simple CLI:** One command, everything you need.
- **Tab-completion support:** Easy discovery and shell autocompletion with Click.
- **Fast and lightweight:** No complex setup; works with your existing repositories.
- **Pluggable AI:** Uses OpenAI GPT-3/4, with future support for more providers.

---

## Installation

```sh
pip install gitaid
```

You’ll also need an OpenAI API key: ```export OPENAI_API_KEY="sk-xxxxxxx..."```

(On Windows Command Prompt: `set OPENAI_API_KEY=sk-xxxxxxx...`)

For a setup checklist, just run:

```sh
gitaid setup
```

## Usage
For a full list of options and commands,
```sh
gitaid --help
```

Example:

Generate an AI-powered commit message for your staged changes
```sh
gitaid commit
```

### (Optional) Enable Tab Completion

For Linux/Bash users (Bash 4.4+), run:

```sh
eval "$(_GITAID_COMPLETE=bash_source gitaid)"
```

Add to your `~/.bashrc` to persist.

For Zsh users (Linux or Mac):

```sh
eval "$(_GITAID_COMPLETE=zsh_source gitaid)"
```

Add to your `~/.zshrc` to persist.

For Windows (Git Bash)

```sh
eval "$(_GITAID_COMPLETE=bash_source gitaid)"
```

Add to your `~/.bash_profile` to persist.


## Why GitAid?
- Save time: Let AI do the heavy lifting for your commit hygiene and documentation.
- Improve quality: Always provide clear, team-friendly commit messages and explanations for your changes.
- Boost productivity: Reduce git mistakes, context-switching, and manual review work.
- Level up collaboration: Make your PRs more readable and ready for both bots and humans.

## Requirements
- Python 3.7+
- OpenAI API key

## Roadmap
- Multi-LLM and self-hosted AI support
- Automatic codebase coverage and test detection
- Support for monorepo and multi-repo workflows
- Integration with project management tools (Jira, GitHub Issues, etc.)
- Advanced pre-commit checks and suggestions

## License
[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) License

