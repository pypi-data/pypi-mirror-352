# freeai_utils/cli.py
import sys
import click
from ._setup import install_model

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        # no subcommand given: show help and exit with error
        click.echo(ctx.get_help())
        sys.exit(1)

@main.command(help="Download default models for this library through hugging face ")
@click.argument("target", required=False)
def setup(target : str  = ""):
    install_model(target)
    
@main.command(help="Detail guide on command line")
def guide():
    print("*" * 100)
    print("HELP")
    print("*" * 100)
    print("Usage: freeai-utils setup [FLAG]\n")
    print(" Flags:")
    print("   A   Default models             →  freeai-utils setup A")
    print("   S   Speech-to-Text models      →  freeai-utils setup S")
    print("   D   Document-related models     →  freeai-utils setup D")
    print("   I   Image OCR models            →  freeai-utils setup I")
    print("   T   Translation models          →  freeai-utils setup T")
    print("   L   Default LLM models          →  freeai-utils setup L")
    print("   ICF Image generator models      →  freeai-utils setup ICF")
    print("*" * 100)

if __name__ == "__main__":
    main()
