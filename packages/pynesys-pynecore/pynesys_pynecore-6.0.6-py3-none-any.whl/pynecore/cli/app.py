import os
import sys
from pathlib import Path
from dataclasses import dataclass

try:
    import typer
except ImportError:
    print("You need to install typer to run Pyne CLI. Please run `pip install typer`.", file=sys.stderr)
    raise SystemExit(1)

__all__ = ["app", "app_state"]

app = typer.Typer(
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_markup_mode="rich",
)


@dataclass(slots=True)
class AppState:
    """
    Application state variables
    """
    _workdir: Path | None = None

    def __post_init__(self):
        # If no workdir was explicitly set, find it automatically
        if self._workdir is None:
            self._workdir = self._find_workdir()

    @staticmethod
    def _find_workdir() -> Path:
        """
        Recursively searches for the workdir folder in the current and parent directories.
        If not found, uses the current directory.
        """
        current_dir = Path().resolve()
        # Maximum search depth in parent directories
        max_depth = 10

        # Start with the current directory and move upwards
        for _ in range(max_depth):
            workdir_candidate = current_dir / "workdir"
            if workdir_candidate.exists() and workdir_candidate.is_dir():
                return workdir_candidate

            # Check if we've reached the filesystem root
            parent = current_dir.parent
            if parent == current_dir:  # Reached the root
                break

            current_dir = parent

        # If no workdir folder was found, use the current directory
        return (Path() / "workdir").resolve()

    @property
    def workdir(self) -> Path:
        """
        The path to the working directory
        """
        return self._workdir or self._find_workdir()

    @workdir.setter
    def workdir(self, path: Path):
        """
        Sets the working directory
        """
        self._workdir = path

    @property
    def scripts_dir(self):
        return self.workdir / "scripts"

    @property
    def output_dir(self):
        return self.workdir / "output"

    @property
    def data_dir(self):
        return self.workdir / "data"

    @property
    def config_dir(self):
        return self.workdir / "config"


app_state = AppState()


def print_logo():
    try:
        from rich import print as rprint
        from rich.console import Console

        console = Console()

        if console.color_system and not os.getenv("NO_COLOR"):
            rprint("")
            rprint("           [dark_green] █ [/]")
            rprint(
                "           [blue on dark_green]   [/]             "
                "[bright_red] ____ [/]"
            )
            rprint(
                "         [blue on dark_green] ▄▄▄▄  [/]           "
                "[bright_red]|  _ \\ _   _ _ __   ___ [/]"
            )
            rprint(
                "       [blue on dark_green]  █▄████[/][yellow on dark_green]▄▄ [/]         "
                "[bright_red]| |_) | | | | '_ \\ / _ \\ [/]"
            )
            rprint(
                "     [blue on dark_green]  ▄▇▇▇▇▇██[/][dark_green on yellow]   [/][yellow on dark_green]  [/]       "
                "[bright_red]|  __/| |_| | | | |  __/ [/]"
            )
            rprint(
                "   [blue on dark_green]    ███[/][dark_green on yellow]  ▁▁▁▁▁▄[/][yellow on dark_green]    [/]     "
                "[bright_red]|_|    \\__, |_| |_|\\___| [/]"
            )
            rprint(
                " [blue on dark_green]       ▀▀[/][dark_green on yellow]    ▄ [/][yellow on dark_green]        [/]   "
                "[bright_red]       |___/ [/]"
            )
            rprint("         [yellow on dark_green]  ▀▀▀▀ [/]")
        else:
            raise ImportError  # Force the except block

    except (UnicodeEncodeError, ImportError):
        print("  ____")
        print(" |  _ \\ _   _ _ __   ___")
        print(" | |_) | | | | '_ \\ / _ \\")
        print(" |  __/| |_| | | | |  __/")
        print(" |_|    \\__, |_| |_|\\___|")
        print("        |___/")


if (not os.getenv("PYNE_NO_LOGO") and not os.getenv("PYNE_QUIET")
        # Don't print logo when completion is requested
        and not os.getenv("_TYPER_COMPLETE_ARGS")):
    print_logo()
