import click
import os
from gitaid.commands import commit as commit_mod, explain as explain_mod

@click.group()
def cli():
    """Hello from GitAid!"""
    # <-- API Key check: print tip ONCE, for any command if key is missing
    if not os.getenv("OPENAI_API_KEY"):
        click.echo("Please set your OpenAI API Key before using gitaid: export OPENAI_API_KEY=sk-xxxx...")

@cli.command(name="commit")
def commit_command():
    """Run GitAid commit"""
    commit_mod.main()

@cli.command(name="explain")
def explain_command():
    """Run GitAid explain"""
    explain_mod.main()

@cli.command(name="setup")
def setup_command():
    """Show setup instructions and recommended environment configuration."""
    click.echo("""\n
   GitAid Quick Setup

1. Set your OpenAI API key (required):

   export OPENAI_API_KEY="sk-xxxx..."

2. (Optional) Enable tab-completion for super-fast CLI:

   Zsh:
       eval "$(_GITAID_COMPLETE=zsh_source gitaid)"      # add to ~/.zshrc to persist

   Bash:
       eval "$(_GITAID_COMPLETE=bash_source gitaid)"     # add to ~/.bashrc

For more, see:
https://pypi.org/project/gitaid/
""")

if __name__ == "__main__":
    cli()