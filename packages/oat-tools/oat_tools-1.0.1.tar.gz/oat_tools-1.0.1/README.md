## OAT Tools

OAT Tools is a CLI tool written in Python. It is installed as executable `oat` using `uv tool install` or as one-off run using `uvx`. The tool has been designed to help you manage Markdown files written to learning diary written using OAT Spec (as described in [Oppimispäiväkirja 101](https://sourander.github.io/oat)).

The idea is to keep the tool minimalistic and simple. It will handle the following tasks:

* Detect unused references (Footnotes in Vancouver style)
* Order references by first appearance
* Remove unused references
* Count words in Markdown files, excluding code blocks, footnotes and urls.

## Installation

You can install OAT Tools using `uv`:

```bash
uv tool install oat-tools
```

The output will some something like this:

```
Resolved 3 packages in 1ms
Installed 3 packages in 3ms
 + click==8.2.1
 + oat-tools==1.0.0
 + tabulate==0.9.0
Installed 1 executable: oat
```

From now on, you can use the `oat` command in your terminal to run the tool.

## Usage

### References

To detect unused references, order them by first appearance, and remove unused references, you can use the following command:

```bash
# Abstract
oat references [--fix] <FILE...>

# Concrete example (check diary, another and all Markdown files in docs directory)
oat references check diary.md another.md docs/**/*.md

# Concrete example (fix the same files)
oat references fix diary.md another.md docs/**/*.md
```

Where `<FILE...>` is any number or Markdown files you want to process. You can use wildcards since your shell will expand them. Note that the `--fix` option will modify the files in place, so use it with caution. It is recommended to run the command without `--fix` first to see what changes will be made. Any unused references will be REMOVED, which is a destructive operation. It is recommended to run these commands after a Git commit, so you can easily revert the changes if needed, and can also review the changes using various diff tools.

Terminology used in this tool:

* **appearance**: Means that the `[^ref]` is used in the body text.
* **reference**: Means that the `[^ref]:` is defined in the footnotes section.
* **unused**: The `[^ref]:` is defined in the footnotes section, but has no appearance in the body text.
* **orphan**: Opposite situation. The `[^ref]` is used in the body text without a corresponding `[^ref]:`.

### Word Count

To count words in Markdown files, excluding code blocks, footnotes, and URLs, you can use the following command:

```bash
# Abstract
oat wordcount <FILE...>

# Concrete example
oat wordcount diary.md another.md docs/**/*.md
```

Where `<FILE...>` is any number of Markdown files you want to process. Again, you can use wildcards.

