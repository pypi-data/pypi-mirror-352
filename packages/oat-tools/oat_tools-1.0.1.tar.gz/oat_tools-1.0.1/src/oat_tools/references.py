import math
import re

from dataclasses import dataclass, field
from pathlib import Path
from tabulate import tabulate
from collections import defaultdict


def extract_id(full_reference_line: str) -> str:
    """
    Extract a valid reference ID from the full reference line.
    """
    words = full_reference_line.split()
    if not words:
        raise ValueError("The reference line is empty or does not contain a valid ID.")

    first_word = words[0]

    # Use regex to match the Vancouver style reference ID
    match = re.match(r"^\[\^([\w-]+)\]:", first_word)
    if match:
        return match.group(1)
    else:
        raise ValueError(
            f"Invalid reference ID format: {first_word}. Expected format is [^id]:"
        )


def is_reference_line(line: str) -> bool:
    """
    Identify if a line in a Markdown file is a Vancouver style reference line.
    Args:
        line (str): The line to check.
    Returns:
        bool: True if the line is a reference line, False otherwise.
    Raises:
        ValueError: If the line is a reference line but does not contain any text after the ID.
    """

    words = line.split()
    if not words:
        return False

    first_word = words[0]
    rest = words[1:]

    if len(rest) == 0 and first_word.startswith("[^") and first_word.endswith("]:"):
        raise ValueError(
            f"A line with reference {first_word} does not contain any text after the ID."
        )

    if first_word.startswith("[^") and first_word.endswith("]:"):
        return True
    return False


@dataclass
class Reference:
    """
    A class that represents a Vancouver style reference in a Markdown file.

    Attributes:
        full_reference_line (str): The full reference line as it appears in the Markdown file.
        first_appearance_pos (int | None): The character position where the reference first appears.
        number_of_appearances (int): The number of times the reference appears in the file.
    """

    full_reference_line: str
    first_appearance_pos: int | None = None
    number_of_appearances: int = 0

    def __post_init__(self):
        self.reference_id = extract_id(self.full_reference_line)

    def record_appearance(self, position: int):
        if self.first_appearance_pos is None:
            self.first_appearance_pos = position
        elif self.first_appearance_pos > position:
            self.first_appearance_pos = position
        else:
            pass

        self.number_of_appearances += 1


@dataclass
class UnusedRefRecord:
    """
    A class to record the appearance of a reference in a Markdown file.

    Attributes:
        reference_id (str): The ID of the reference.
        first_appearance_pos (int): The character position where the reference first appears.
        number_of_appearances (int): The number of times the reference appears in the file.
    """

    file_path: Path
    reference_id: str
    number_of_appearances: int


@dataclass
class OrphanRefRecord:
    """
    A class to represent an orphan reference in a Markdown file.

    Attributes:
        reference_id (str): The ID of the orphan reference.
        number_of_appearances (int): The number of times the orphan reference appears in the body text.
    """

    file_path: Path
    reference_id: str
    number_of_appearances: int


@dataclass
class ReferenceCollection:
    """
    A class that represents the Vancouver style references in a given Markdown file.

    Attributes:
        references (list[Reference]): A list of Reference objects representing the references in the file.

    Methods:
        add_reference(full_reference_line: str): Add a new reference to the collection.
        get_reference_by_id(reference_id: str): Get a reference by its ID.
        get_unappearing_references(): Get references that do not appear in the body text.
        get_ordered_by_pos(only_appearing=False): Get the references ordered by their first appearance position.

    Raises:
        ValueError: If a reference with the same ID already exists or if a reference line is invalid.
    """

    references: list[Reference] = field(default_factory=list)

    def add_reference(self, full_reference_line: str):
        """
        Add a new reference to the collection.
        """
        reference_id = extract_id(full_reference_line)

        # Check if reference already exists by iterating through references
        for ref in self.references:
            if ref.reference_id == reference_id:
                raise ValueError(f"Reference with ID {reference_id} already exists.")

        reference = Reference(full_reference_line)
        self.references.append(reference)

    def get_reference_by_id(self, reference_id: str) -> Reference:
        """
        Get a reference by its ID.
        """
        for ref in self.references:
            if ref.reference_id == reference_id:
                return ref
        raise ValueError(
            f"Reference with ID {reference_id} not found. Existing references: {[r.reference_id for r in self.references]}"
        )

    def get_unappearing_references(self) -> list[Reference]:
        """
        Get references that do not appear in the body text.
        """
        return [ref for ref in self.references if ref.number_of_appearances == 0]

    def get_ordered_by_pos(self, only_appearing=False) -> list[Reference]:
        """
        Get the references ordered by their first appearance position.
        """
        references = sorted(
            self.references, key=lambda ref: ref.first_appearance_pos or math.inf
        )
        if only_appearing:
            references = [ref for ref in references if ref.number_of_appearances > 0]
        return references


class MarkdownFile:
    """
    A class to manage Vancouver style references in a Markdown file.

    Attributes:
        file_path (Path): The path to the Markdown file.
        reference_collection (ReferenceCollection): The collection of references in the file.
        auto_load (bool): Whether to automatically load references from the file upon initialization.

    Methods:
        _load_references(): Load references from the Markdown file.

    """

    def __init__(self, file_path: Path, auto_load: bool = True):
        self.file_path = file_path
        self.reference_collection = ReferenceCollection()

        self.body_lines: list[str] = []

        if auto_load:
            self._load_references()
            self._count_appearances()

    def _load_references(self):
        """
        Load references from the Markdown file. Move all non-reference lines to body_lines.
        """

        content = self.file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        for line in lines:
            if is_reference_line(line):
                self.reference_collection.add_reference(line.strip())
            else:
                self.body_lines.append(line)

    def _count_appearances(self):
        """
        Count the appearances of each reference in the body text. The position is the byte offset in the file.
        """
        for ref in self.reference_collection.references:
            ref.number_of_appearances = 0
            ref.first_appearance_pos = None

        # Find the position of each reference in the body text
        body_text = "\n".join(self.body_lines)
        for ref in self.reference_collection.references:
            ref_id = ref.reference_id
            pattern = re.compile(r"\[\^" + re.escape(ref_id) + r"\]")
            matches = list(pattern.finditer(body_text))

            for match in matches:
                ref.record_appearance(match.start())

    def get_orphan_references(self) -> list[OrphanRefRecord]:
        """
        Count [^refs] in the body text that are not in the reference collection so that we can print them later on using tabulate.
        It should contain the (unexiasting) reference ID and the number of appearances.

        Returns:
            list[OrphanRefRecord]: A list of OrphanRefRecord objects containing the reference ID and the number of appearances.
        """
        body_text = "\n".join(self.body_lines)
        pattern = re.compile(r"\[\^([\w-]+)\]")
        matches = list(pattern.finditer(body_text))

        # Let's use sets to track existing references
        existing_references = {
            ref.reference_id for ref in self.reference_collection.references
        }

        orphan_references = defaultdict(int)
        for match in matches:
            ref_id = match.group(1)
            if ref_id not in existing_references:
                orphan_references[ref_id] += 1

        # Convert to a list of OrphanRefRecord objects
        orphan_references_list = [
            OrphanRefRecord(
                file_path=self.file_path,
                reference_id=ref_id,
                number_of_appearances=count,
            )
            for ref_id, count in orphan_references.items()
        ]
        return orphan_references_list

    def get_unused_references(self) -> list[UnusedRefRecord]:
        """
        Return the a line we can later on print using tabulate.
        It should contain the reference ID, first appearance position, and number of appearances (0)
        """

        return [
            UnusedRefRecord(
                file_path=self.file_path,
                reference_id=ref.reference_id,
                number_of_appearances=ref.number_of_appearances,
            )
            for ref in self.reference_collection.get_ordered_by_pos(
                only_appearing=False
            )
            if ref.number_of_appearances == 0
        ]

    def _materialize(self, content: str, md_path: Path | None = None):
        """
        Materialize the file, overwriting the original file with the updated references unless new path is provided.
        """
        if md_path is None:
            md_path = self.file_path

        md_path = self.file_path
        md_path.write_text(content, encoding="utf-8")

    def _get_final_content(self) -> str:
        """
        Join the body lines and references into a final content string.
        """

        body = "\n".join(self.body_lines)
        references = self.reference_collection.get_ordered_by_pos(only_appearing=True)
        reference_lines = [ref.full_reference_line for ref in references]

        if not reference_lines:
            # If there are no references, just return the body
            return body

        # Delete the trailing newlines to avoid extra empty lines at the end
        if body.endswith("\n"):
            body = body.rstrip("\n")
        # Ensure that the references are separated by exactly two newlines (one empty line)
        final_content = body + "\n" + "\n" + "\n".join(reference_lines) + "\n"
        return final_content

    def fix_references(self):
        """
        Fix the references in the Markdown file by removing unused references and reordering by first appearance.
        """

        self._materialize(self._get_final_content())


def print_references_table(reference_managers: list[MarkdownFile]):
    """
    Print a table of references from multiple MarkdownFile instances.

    Args:
        reference_managers (list[MarkdownFile]): List of hanled files.
    """
    appearance_records = []
    for manager in reference_managers:
        ar = manager.get_unused_references()
        appearance_records.extend(ar)

    if not appearance_records:
        print("✅ No unused references found.")
        return

    print("")
    print("Unused references:")
    print(tabulate(appearance_records, headers="keys"))


def print_orphan_references(reference_managers: list[MarkdownFile]):
    """
    Print a table of orphan references from multiple MarkdownReferenceManager instances.
    Args:
        reference_managers (list[MarkdownReferenceManager]): List of MarkdownReferenceManager instances.
    """
    orphan_references = []
    for manager in reference_managers:
        orphan_references.extend(manager.get_orphan_references())

    if not orphan_references:
        print("✅ No orphan references found.")
        return

    print("")
    print("Orphan references:")
    print(tabulate(orphan_references, headers="keys"))
