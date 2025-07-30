import os
import sys
import shutil
import pyperclip
from rich import print as printf

from .pdf_tools import PDFTools
from .tui import SelectionMenu, ReorderMenu
from .utils import get_files, get_save_path

OPTIONS = ["Merge PDFs", "Exit"]


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")
    terminal_width = shutil.get_terminal_size((80, 20)).columns
    title = "PDFwerks"
    centered_title = title.center(terminal_width)
    printf(f"[bold #FFAA66  ]{centered_title}[/bold #FFAA66  ]")
    underline = "─" * terminal_width
    printf(f"[#FFECB3]{underline}[/#FFECB3]")


def run_tui():
    try:
        clear_screen()
        tool = PDFTools()

        menu_choice = SelectionMenu("Please select one of the tools:", OPTIONS).run()

        if menu_choice == "Merge PDFs":
            files = get_files()
            files = ReorderMenu(
                "Reorder the files if required: (Use ↑/↓ to navigate, SPACE to select/unselect, ENTER to confirm)",
                files,
            ).run()

            if len(files) < 2:
                printf("[bold red]✗ Merge Failed: At least 2 files are required to merge. Only 1 was selected!\n[/bold red]")
                sys.exit(1)

            tool.merge(files)
            save_path = get_save_path()
            tool.export(save_path)
            pyperclip.copy(save_path)
            printf("[#A3BE8C]✔[/#A3BE8C] [bold #FFD580] Merged PDF saved!\n[/bold #FFD580]")

        elif menu_choice == "Exit":
            sys.exit(0)

    except KeyboardInterrupt:
        printf("[bold red]PDFwerks was terminated due to KeyboardInterrupt!\n[/bold red]")

    finally:
        printf("[bold #A3BE8C]Goodbye![/bold #A3BE8C]")
