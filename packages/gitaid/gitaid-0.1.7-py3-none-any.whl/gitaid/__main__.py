import click
from gitaid.commands import commit as commit_mod, explain as explain_mod

@click.group()
def cli():
    """Hello from GitAid!"""

@cli.command(name="commit")
def commit_command():
    """Run GitAid commit"""
    commit_mod.main()

@cli.command(name="explain")
def explain_command():
    """Run GitAid explain"""
    explain_mod.main()

if __name__ == "__main__":
    cli()