import re

from pathlib import Path
from tabulate import tabulate
from oat_tools.references import is_reference_line


def count_words(file_path: Path) -> int:
    """
    Count the number of words in a Markdown file, excluding code blocks, footnotes, and URLs.

    Args:
        file_path (str): Path to the Markdown file.

    Returns:
        int: The total word count in the file.
    """
    content = file_path.read_text(encoding="utf-8")

    # Remove code blocks
    content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)

    # Remove footnotes
    # content = re.sub(r'\[\d+\]:.*?\n', '', content)
    # Let's instead use the is_reference_line function to identify and remove footnotes
    lines = content.splitlines()
    content = "\n".join(line for line in lines if not is_reference_line(line))

    # Remove Markdown URLs [text](http*)
    content = re.sub(r"\[.*?\]\(http[^\)]+\)", "", content)

    # Split into words and count
    words = re.findall(r"\b\w+\b", content)

    return len(words)


def print_file_word_counts(file_paths: list[Path]) -> None:
    """
    Print the word count for each file.

    Args:
        file_paths (list): List of file paths to count words in.
    """

    table = []
    for file_path in file_paths:
        word_count = count_words(file_path)
        table.append([file_path, word_count])

    print(tabulate(table, headers=["File", "Word Count"]))
