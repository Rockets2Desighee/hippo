

# THIS WORKED:




# import click
# from .commands.search import search_cmd
# from .commands.download import download_cmd
# from .commands.quicklook import quicklook_cmd

# @click.group()
# @click.version_option(package_name="sat-ingest")
# def cli():
#     """sat — satellite ingestion CLI"""

# @cli.command("env")
# def env_cmd():
#     """Show where this 'sat' is running from (debug helper)."""
#     import sys, sat_ingest, pathlib
#     click.echo(f"python: {sys.executable}")
#     click.echo(f"sat_ingest: {pathlib.Path(sat_ingest.__file__).resolve()}")
#     click.echo(f"cwd: {pathlib.Path().resolve()}")

# cli.add_command(search_cmd, name="search")
# cli.add_command(download_cmd, name="download")
# cli.add_command(quicklook_cmd, name="quicklook")

# def main():
#     cli()

# if __name__ == "__main__":
#     main()



# THIS IS TO TAKE THE AWS CREDENTIALS FROM ENV.EXAMPLE FILE INTO ACCOUNT:


import os
import pathlib
import click

# NEW: auto-load .env or env.example
def _autoload_env() -> str | None:
    """
    Load environment variables for the CLI.
    Preference:
      1) .env (in CWD)
      2) env.example (in CWD)
    Returns the filename that was loaded, or None.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        # If python-dotenv isn't installed, silently skip; CLI still works.
        return None

    cwd = pathlib.Path().resolve()
    env_path = cwd / ".env"
    example_path = cwd / "env.example"

    # Try .env first
    if env_path.exists():
        loaded = load_dotenv(env_path, override=False)
        return ".env" if loaded else None

    # Fallback to env.example
    if example_path.exists():
        loaded = load_dotenv(example_path, override=False)
        if loaded:
            # Friendly note once per process
            click.echo(
                "No .env found — using values from env.example. "
                "Create a .env to override.",
                err=True,
            )
            return "env.example"

    return None

# Do this as early as possible so subcommands see the env
_LOADED_ENV_FILE = _autoload_env()

from .commands.search import search_cmd
from .commands.download import download_cmd
from .commands.quicklook import quicklook_cmd

@click.group()
@click.version_option(package_name="sat-ingest")
def cli():
    """sat — satellite ingestion CLI"""

@cli.command("env")
def env_cmd():
    """Show where this 'sat' is running from and which env file was used."""
    import sys, sat_ingest
    here = pathlib.Path().resolve()
    pkg_path = pathlib.Path(sat_ingest.__file__).resolve()
    click.echo(f"python: {sys.executable}")
    click.echo(f"sat_ingest: {pkg_path}")
    click.echo(f"cwd: {here}")
    # NEW: show which env file we loaded
    which = _LOADED_ENV_FILE or "(none)"
    click.echo(f"env loaded from: {which}")

cli.add_command(search_cmd, name="search")
cli.add_command(download_cmd, name="download")
cli.add_command(quicklook_cmd, name="quicklook")



def main():
    cli()

if __name__ == "__main__":
    main()
