import pytest
import tempfile
import os
from pathlib import Path

from oat_tools.references import (
    ReferenceCollection,
    Reference,
    extract_id,
    is_reference_line,
    MarkdownFile,
    UnusedRefRecord,
    OrphanRefRecord,
)
from textwrap import dedent


class TestExtractId:
    """Test the extract_id function."""

    def test_extract_id_valid_reference(self):
        """Test extracting ID from a valid Vancouver style reference."""
        assert extract_id("[^1]: Author, A. (2023). Title. Journal.") == "1"
        assert extract_id("[^ref1]: Smith, J. (2024). Research paper.") == "ref1"
        assert extract_id("[^my-ref]: Doe, J. et al. (2022). Study.") == "my-ref"

    def test_extract_id_empty_line(self):
        """Test that empty lines raise ValueError."""
        with pytest.raises(ValueError, match="The reference line is empty"):
            extract_id("")
        with pytest.raises(ValueError, match="The reference line is empty"):
            extract_id("   ")

    def test_extract_id_invalid_format(self):
        """Test that invalid reference formats raise ValueError."""
        with pytest.raises(ValueError, match="Invalid reference ID format"):
            extract_id("1: Invalid format")
        with pytest.raises(ValueError, match="Invalid reference ID format"):
            extract_id("[1]: Missing caret")
        with pytest.raises(ValueError, match="Invalid reference ID format"):
            extract_id("[^1] Missing colon")
        with pytest.raises(ValueError, match="Invalid reference ID format"):
            extract_id("[^this contains a whitespace]:")


class TestIsReferenceLine:
    """Test the is_reference_line function."""

    def test_valid_reference_lines(self):
        """Test that valid reference lines are identified correctly."""
        assert is_reference_line("[^1]: Author, A. (2023). Title.")
        assert is_reference_line("[^ref1]: Smith, J. (2024). Research.")
        assert is_reference_line("[^my-ref]: Doe, J. et al. (2022). Study.")
        assert is_reference_line("[^complex-id_123]: Complex reference with ID.")

    def test_invalid_reference_lines(self):
        """Test that non-reference lines return False."""
        assert not is_reference_line("This is just normal text")
        assert not is_reference_line("# Heading")
        assert not is_reference_line("Some text with [^1] citation")
        assert not is_reference_line("")
        assert not is_reference_line("[^complex id 123]: Complex reference with ID.")

    def test_reference_line_without_text(self):
        """Test that reference lines without text after ID raise ValueError."""
        with pytest.raises(ValueError):
            is_reference_line("[^1]:")
        with pytest.raises(ValueError):
            is_reference_line("[^ref]:")


class TestReference:
    """Test the Reference class."""

    def test_reference_creation(self):
        """Test creating a Reference object."""
        ref = Reference("[^1]: Author, A. (2023). Title of paper.")
        assert ref.full_reference_line == "[^1]: Author, A. (2023). Title of paper."
        assert ref.reference_id == "1"
        assert ref.first_appearance_pos is None
        assert ref.number_of_appearances == 0

    def test_reference_creation_with_complex_id(self):
        """Test creating a Reference with complex ID."""
        ref = Reference("[^my-ref-123]: Complex reference.")
        assert ref.reference_id == "my-ref-123"

    def test_reference_invalid_format(self):
        """Test that invalid reference format raises ValueError."""
        with pytest.raises(ValueError):
            Reference("Invalid reference format")

    def test_record_appearance_first_time(self):
        """Test recording the first appearance of a reference."""
        ref = Reference("[^1]: Test reference.")
        ref.record_appearance(100)

        assert ref.first_appearance_pos == 100
        assert ref.number_of_appearances == 1

    def test_record_appearance_multiple_times(self):
        """Test recording multiple appearances."""
        ref = Reference("[^1]: Test reference.")
        ref.record_appearance(100)
        ref.record_appearance(200)
        ref.record_appearance(50)  # Earlier position

        assert ref.first_appearance_pos == 50  # Should be the earliest position
        assert ref.number_of_appearances == 3

    def test_record_appearance_same_position(self):
        """Test recording appearance at the same position multiple times."""
        ref = Reference("[^1]: Test reference.")
        ref.record_appearance(100)
        ref.record_appearance(100)

        assert ref.first_appearance_pos == 100
        assert ref.number_of_appearances == 2


class TestReferenceCollection:
    """Test the ReferenceCollection class."""

    def test_empty_collection(self):
        """Test creating an empty reference collection."""
        collection = ReferenceCollection()
        assert len(collection.references) == 0
        assert collection.get_unappearing_references() == []
        assert collection.get_ordered_by_pos() == []

    def test_add_reference(self):
        """Test adding a reference to the collection."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")

        assert len(collection.references) == 1
        assert collection.references[0].reference_id == "1"
        assert collection.references[0].full_reference_line == "[^1]: First reference."

    def test_add_multiple_references(self):
        """Test adding multiple references."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")
        collection.add_reference("[^2]: Second reference.")
        collection.add_reference("[^ref3]: Third reference.")

        assert len(collection.references) == 3
        ids = [ref.reference_id for ref in collection.references]
        assert "1" in ids
        assert "2" in ids
        assert "ref3" in ids

    def test_add_duplicate_reference(self):
        """Test that adding duplicate reference raises ValueError."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")

        with pytest.raises(ValueError, match="Reference with ID 1 already exists"):
            collection.add_reference("[^1]: Duplicate reference.")

    def test_get_reference_by_id(self):
        """Test retrieving a reference by its ID."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")
        collection.add_reference("[^test]: Test reference.")

        ref1 = collection.get_reference_by_id("1")
        assert ref1 is not None
        assert ref1.reference_id == "1"
        assert ref1.full_reference_line == "[^1]: First reference."

        ref_test = collection.get_reference_by_id("test")
        assert ref_test is not None
        assert ref_test.reference_id == "test"

    def test_get_reference_by_id_nonexistent(self):
        """Test that getting a nonexistent reference raises ValueError."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")

        with pytest.raises(ValueError, match="Reference with ID nonexistent not found"):
            collection.get_reference_by_id("nonexistent")

    def test_get_unappearing_references(self):
        """Test getting references that don't appear in text."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: Used reference.")
        collection.add_reference("[^2]: Unused reference.")
        collection.add_reference("[^3]: Another unused reference.")

        # Mark one reference as appearing
        ref1 = collection.get_reference_by_id("1")
        assert isinstance(ref1, Reference)
        ref1.record_appearance(100)

        unused = collection.get_unappearing_references()
        assert len(unused) == 2
        unused_ids = [ref.reference_id for ref in unused]
        assert "2" in unused_ids
        assert "3" in unused_ids
        assert "1" not in unused_ids

    def test_get_ordered_by_pos(self):
        """Test getting references ordered by first appearance position."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")
        collection.add_reference("[^2]: Second reference.")
        collection.add_reference("[^3]: Third reference.")

        # Record appearances in different order
        collection.get_reference_by_id("2").record_appearance(50)
        collection.get_reference_by_id("1").record_appearance(200)
        collection.get_reference_by_id("3").record_appearance(100)

        ordered = collection.get_ordered_by_pos()
        assert len(ordered) == 3
        assert ordered[0].reference_id == "2"  # Position 50
        assert ordered[1].reference_id == "3"  # Position 100
        assert ordered[2].reference_id == "1"  # Position 200

    def test_get_ordered_by_pos_with_unappearing(self):
        """Test ordering when some references don't appear in text."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: Appearing reference.")
        collection.add_reference("[^2]: Non-appearing reference.")
        collection.add_reference("[^3]: Another appearing reference.")

        # Only record appearances for some references
        collection.get_reference_by_id("3").record_appearance(50)
        collection.get_reference_by_id("1").record_appearance(100)
        # ref2 has no appearances

        ordered = collection.get_ordered_by_pos()
        assert len(ordered) == 3
        assert ordered[0].reference_id == "3"  # Position 50
        assert ordered[1].reference_id == "1"  # Position 100
        assert ordered[2].reference_id == "2"  # No position (math.inf)

    def test_get_ordered_by_pos_only_appearing(self):
        """Test get_ordered_by_pos with only_appearing=True filters out non-appearing references."""
        collection = ReferenceCollection()
        collection.add_reference("[^1]: First reference.")
        collection.add_reference("[^2]: Second reference.")
        collection.add_reference("[^3]: Third reference.")
        collection.add_reference("[^4]: Fourth reference.")

        # Record appearances for only some references
        collection.get_reference_by_id("3").record_appearance(50)
        collection.get_reference_by_id("1").record_appearance(100)
        collection.get_reference_by_id("4").record_appearance(25)
        # ref2 has no appearances (number_of_appearances == 0)

        # Test with only_appearing=False (default behavior)
        all_ordered = collection.get_ordered_by_pos(only_appearing=False)
        assert len(all_ordered) == 4
        assert all_ordered[0].reference_id == "4"  # Position 25
        assert all_ordered[1].reference_id == "3"  # Position 50
        assert all_ordered[2].reference_id == "1"  # Position 100
        assert all_ordered[3].reference_id == "2"  # No position (math.inf)

        # Test with only_appearing=True (should exclude ref2)
        appearing_only = collection.get_ordered_by_pos(only_appearing=True)
        assert len(appearing_only) == 3
        assert appearing_only[0].reference_id == "4"  # Position 25
        assert appearing_only[1].reference_id == "3"  # Position 50
        assert appearing_only[2].reference_id == "1"  # Position 100
        # ref2 should not be in the list since it has number_of_appearances == 0

        # Verify that ref2 is not in the appearing_only list
        appearing_ids = [ref.reference_id for ref in appearing_only]
        assert "2" not in appearing_ids

    def test_integration_scenario(self):
        """Test a complete scenario simulating typical usage."""
        collection = ReferenceCollection()

        # Add references as they would be found in a markdown file
        collection.add_reference(
            "[^1]: Smith, J. (2023). Research on AI. Journal of AI, 15(3), 123-145."
        )
        collection.add_reference(
            "[^doe2024]: Doe, J. et al. (2024). Machine Learning Advances. Tech Review."
        )
        collection.add_reference("[^unused]: Unused reference that should be removed.")
        collection.add_reference(
            "[^brown]: Brown, A. (2022). Data Science Methods. Data Journal."
        )

        # Simulate finding citations in the text (in order of appearance)
        collection.get_reference_by_id("doe2024").record_appearance(
            500
        )  # Second citation in text
        collection.get_reference_by_id("1").record_appearance(
            200
        )  # First citation in text
        collection.get_reference_by_id("brown").record_appearance(
            800
        )  # Third citation in text
        collection.get_reference_by_id("doe2024").record_appearance(
            1200
        )  # Cited again later

        # Test getting unused references
        unused = collection.get_unappearing_references()
        assert len(unused) == 1
        assert unused[0].reference_id == "unused"

        # Test getting references ordered by appearance
        ordered = collection.get_ordered_by_pos()
        assert len(ordered) == 4
        assert ordered[0].reference_id == "1"  # Position 200
        assert ordered[1].reference_id == "doe2024"  # Position 500
        assert ordered[2].reference_id == "brown"  # Position 800
        assert ordered[3].reference_id == "unused"  # No position (last)

        # Test appearance counts
        assert collection.get_reference_by_id("1").number_of_appearances == 1
        assert collection.get_reference_by_id("doe2024").number_of_appearances == 2
        assert collection.get_reference_by_id("brown").number_of_appearances == 1
        assert collection.get_reference_by_id("unused").number_of_appearances == 0


class TestMarkdownFile:
    """Test the MarkdownFile class."""

    def create_temp_markdown_file(self, content: str) -> Path:
        """Helper method to create a temporary markdown file with given content."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            return Path(f.name)

    def test_load_references_method(self):
        """Test the _load_references method."""
        content = dedent("""
            # Heading

            Body text with [^cite1] citation.

            [^cite1]: Citation text.
            [^cite2]: Another citation.
            """).strip()
        temp_file = self.create_temp_markdown_file(content)

        try:
            md_file = MarkdownFile(temp_file, auto_load=False)
            md_file._load_references()

            # Verify references were loaded
            assert len(md_file.reference_collection.references) == 2
            ref_ids = [
                ref.reference_id for ref in md_file.reference_collection.references
            ]
            assert "cite1" in ref_ids
            assert "cite2" in ref_ids

            # Verify body lines (non-reference lines)
            expected_body = ["# Heading", "", "Body text with [^cite1] citation.", ""]
            assert md_file.body_lines == expected_body

        finally:
            os.unlink(temp_file)

    def test_get_tabular_orphan_references(self):
        """Test the get_tabular_orphan_references method."""
        content = dedent("""
            Text with [^existing] and [^orphan1].

            More text with [^orphan2] and [^orphan1] again.

            [^existing]: This reference exists.
            """).strip()
        temp_file = self.create_temp_markdown_file(content)

        try:
            md_file = MarkdownFile(temp_file)
            orphan_refs = md_file.get_orphan_references()

            # Should return list of OrphanRefRecord objects
            assert len(orphan_refs) == 2

            # Convert to dict for easier testing
            orphan_dict = {
                ref.reference_id: ref.number_of_appearances for ref in orphan_refs
            }

            assert "orphan1" in orphan_dict
            assert "orphan2" in orphan_dict
            assert orphan_dict["orphan1"] == 2  # appears twice
            assert orphan_dict["orphan2"] == 1  # appears once

            # Verify the OrphanRefRecord properties
            for ref in orphan_refs:
                assert isinstance(ref, OrphanRefRecord)
                assert ref.file_path == temp_file
                assert ref.reference_id in ["orphan1", "orphan2"]
                assert ref.number_of_appearances > 0

        finally:
            os.unlink(temp_file)

    def test_get_tabular_orphan_references_no_orphans(self):
        """Test get_tabular_orphan_references when there are no orphan references."""
        content = dedent("""
            Text with [^ref1] only.

            [^ref1]: Existing reference.
            """).strip()
        temp_file = self.create_temp_markdown_file(content)

        try:
            md_file = MarkdownFile(temp_file)
            orphan_refs = md_file.get_orphan_references()

            assert orphan_refs == []

        finally:
            os.unlink(temp_file)

    def test_get_missing_appearance_record(self):
        """Test the get_missing_appearance_record method."""
        content = dedent("""
            Text with [^used] citation.

            [^used]: Used reference.
            [^unused1]: First unused reference.
            [^unused2]: Second unused reference.
            """).strip()
        temp_file = self.create_temp_markdown_file(content)

        try:
            md_file = MarkdownFile(temp_file)
            missing_records = md_file.get_unused_references()

            assert len(missing_records) == 2

            # Verify each record is a MissingAppearanceRecord
            for record in missing_records:
                assert isinstance(record, UnusedRefRecord)
                assert record.file_path == temp_file
                assert record.number_of_appearances == 0
                assert record.reference_id in ["unused1", "unused2"]

        finally:
            os.unlink(temp_file)

    def test_get_missing_appearance_record_no_missing(self):
        """Test get_missing_appearance_record when all references are used."""
        content = dedent("""
            Text with [^ref1] and [^ref2].

            [^ref1]: First reference.
            [^ref2]: Second reference.
            """).strip()
        temp_file = self.create_temp_markdown_file(content)

        try:
            md_file = MarkdownFile(temp_file)
            missing_records = md_file.get_unused_references()

            assert missing_records == []

        finally:
            os.unlink(temp_file)

    def test_get_final_content_method(self):
        """Test the _get_final_content method - the key method to test."""
        content = dedent("""
            # Document Title

            This text contains [^second] and [^first] references.

            More text with [^first] again.

            [^first]: First reference (appears first in text).
            [^second]: Second reference (appears second in text).
            [^unused]: This reference should be removed.
            """).strip()
        temp_file = self.create_temp_markdown_file(content)

        try:
            md_file = MarkdownFile(temp_file)
            final_content = md_file._get_final_content()

            # Split into lines for easier verification
            lines = final_content.split("\n")

            # Verify body content comes first
            expected_body = [
                "# Document Title",
                "",
                "This text contains [^second] and [^first] references.",
                "",
                "More text with [^first] again.",
                "",
                "[^second]: Second reference (appears second in text).",
                "[^first]: First reference (appears first in text).",
                "",
            ]

            assert len(lines) == len(expected_body)
            assert lines == expected_body

            assert "[^second]: Second reference (appears second in text)." in lines
            assert "[^first]: First reference (appears first in text)." in lines
            # Verify unused reference is not included
            assert "[^unused]:" not in final_content

            # Verify final content ends with newline
            assert final_content.endswith("\n")

        finally:
            os.unlink(temp_file)

    def test_get_final_content_empty_file(self):
        """Test _get_final_content with an empty file."""
        temp_file = self.create_temp_markdown_file("")

        try:
            md_file = MarkdownFile(temp_file)
            final_content = md_file._get_final_content()

            # Should just be empty body with separator and newline
            expected = ""  # body + nl + empty references + final nl
            assert final_content == expected

        finally:
            os.unlink(temp_file)

    def test_get_final_content_no_references(self):
        """Test _get_final_content with body text but no references."""
        content = dedent("""
            # Title

            Just body text, no references.
            """).strip()
        temp_file = self.create_temp_markdown_file(content)

        try:
            md_file = MarkdownFile(temp_file)
            final_content = md_file._get_final_content()

            expected = "# Title\n\nJust body text, no references."
            assert final_content == expected

        finally:
            os.unlink(temp_file)

    def test_get_final_content_only_unused_references(self):
        """Test _get_final_content when all references are unused."""
        content = dedent("""
            # Title

            Just body text.

            [^unused1]: Unused reference 1.
            [^unused2]: Unused reference 2.
            """).strip()
        temp_file = self.create_temp_markdown_file(content)

        try:
            md_file = MarkdownFile(temp_file)
            final_content = md_file._get_final_content()

            # Should just be body text, no references
            expected = "# Title\n\nJust body text.\n"
            assert final_content == expected

        finally:
            os.unlink(temp_file)

    def test_fix_references_integration(self):
        """Test the fix_references method integration."""
        content = dedent("""
            # Document

            Text with [^ref2] and [^ref1] citations.

            [^ref1]: Reference 1.
            [^ref2]: Reference 2.
            [^unused]: Unused reference.
            """).strip()
        temp_file = self.create_temp_markdown_file(content)

        try:
            md_file = MarkdownFile(temp_file)
            md_file.fix_references()

            # Read the fixed content
            fixed_content = temp_file.read_text(encoding="utf-8")

            # Verify unused reference is removed and order is by appearance
            assert "[^unused]" not in fixed_content
            assert "[^ref1]:" in fixed_content
            assert "[^ref2]:" in fixed_content

            # Verify body text is preserved
            assert "# Document" in fixed_content
            assert "Text with [^ref2] and [^ref1] citations." in fixed_content

        finally:
            os.unlink(temp_file)

    def test_markdown_file_with_complex_ids(self):
        """Test MarkdownFile with complex reference IDs containing hyphens and numbers."""
        content = dedent("""
            # Document

            Text with [^complex-ref_123] and [^simple] citations.

            [^complex-ref_123]: Complex reference with hyphens and numbers.
            [^simple]: Simple reference.
            [^another-complex_456]: Another complex unused reference.
            """).strip()
        temp_file = self.create_temp_markdown_file(content)

        try:
            md_file = MarkdownFile(temp_file)

            # Verify complex IDs are handled correctly
            ref_ids = [
                ref.reference_id for ref in md_file.reference_collection.references
            ]
            assert "complex-ref_123" in ref_ids
            assert "simple" in ref_ids
            assert "another-complex_456" in ref_ids

            # Verify appearance counting works with complex IDs
            complex_ref = md_file.reference_collection.get_reference_by_id(
                "complex-ref_123"
            )
            simple_ref = md_file.reference_collection.get_reference_by_id("simple")
            unused_complex = md_file.reference_collection.get_reference_by_id(
                "another-complex_456"
            )

            assert complex_ref.number_of_appearances == 1
            assert simple_ref.number_of_appearances == 1
            assert unused_complex.number_of_appearances == 0

        finally:
            os.unlink(temp_file)

    def test_markdown_file_with_meaningful_whitespace(self):
        """Test that leading whitespace (e.g. admonition) are not removed."""
        content = dedent("""
            # Document

            !!! note
                This is a note admonition. [^admonition]
                         
            This is a body text without a reference.

            [^admonition]: Admonition reference.
            """).strip()
        
        temp_file = self.create_temp_markdown_file(content)

        try:
            md_file = MarkdownFile(temp_file)

            # Verify admonition is preserved
            assert "!!! note" in md_file.body_lines
            assert "    This is a note admonition. [^admonition]" in md_file.body_lines

            # Verify reference is loaded correctly
            ref_ids = [
                ref.reference_id for ref in md_file.reference_collection.references
            ]
            assert "admonition" in ref_ids

            admonition_ref = md_file.reference_collection.get_reference_by_id("admonition")
            assert admonition_ref.number_of_appearances == 1
        finally:
            os.unlink(temp_file)


    def test_markdown_file_with_existing_test_data(self):
        """Test MarkdownFile using the existing test data file."""
        test_file = Path("tests/data/testing.md")

        if test_file.exists():
            md_file = MarkdownFile(test_file)

            # Based on the content in file
            # - [^foo] appears but is no reference (is orphan)
            # - [^kissa] is appears and has a reference
            # - [^marsu] does not appear but has a reference (unused)

            ref_ids = [
                ref.reference_id for ref in md_file.reference_collection.references
            ]
            assert "kissa" in ref_ids
            assert "marsu" in ref_ids
            assert "foo" not in ref_ids  # foo is an orphan

            kissa_ref = md_file.reference_collection.get_reference_by_id("kissa")
            marsu_ref = md_file.reference_collection.get_reference_by_id("marsu")

            assert kissa_ref.number_of_appearances == 1
            assert marsu_ref.number_of_appearances == 0

            # Test orphan references
            orphan_refs = md_file.get_orphan_references()
            assert len(orphan_refs) == 1
            assert orphan_refs[0].reference_id == "foo"
            assert orphan_refs[0].number_of_appearances == 1
            assert isinstance(orphan_refs[0], OrphanRefRecord)
            assert orphan_refs[0].file_path == test_file
