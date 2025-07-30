# gitaid: AI-powered Git Productivity

[![PyPI version](https://img.shields.io/pypi/v/gitaid)](https://pypi.org/project/gitaid/)
[![Python Versions](https://img.shields.io/pypi/pyversions/gitaid)](https://pypi.org/project/gitaid/)
[![License](https://img.shields.io/pypi/l/gitaid)](https://pypi.org/project/gitaid/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/mayaailabs/gitaid)
Supercharge your developer workflow with **gitaid** — the AI-powered companion for Git that generates intelligent commit messages, explains your changes, and streamlines your git CLI productivity.

---

## Features

- **AI-generated commit messages:** Instantly create clear, context-aware commit messages for your staged changes with one command.
- **Code review explanations:** Get professional, readable explanations of your staged Git changes using advanced AI.
- **Simple CLI:** One command, everything you need (`gitaid commit`, `gitaid explain`).
- **Tab-completion support:** Easy discovery and shell autocompletion with Click.
- **Fast and lightweight:** No complex setup; works with your existing repositories.
- **Pluggable AI:** Uses OpenAI GPT-3/4, with future support for more providers.

---

## Installation

```sh
pip install gitaid
```

Note: You’ll also need an OpenAI API key.

## Usage
Run gitaid --help for a full list of options and commands.

Generate an AI-powered commit message for your staged changes
```sh
gitaid commit
```

Get an AI explanation of the current staged diff
```sh
gitaid explain
```


## Why gitaid?
Save time: Let AI do the heavy lifting for your commit hygiene and documentation.
Improve quality: Always provide clear, team-friendly commit messages and explanations for your changes.
Boost productivity: Reduce git mistakes, context-switching, and manual review work.
Level up collaboration: Make your PRs more readable and ready for both bots and humans.

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
Apache 2.0 License

