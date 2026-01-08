#!/usr/bin/env python3
import os
import re
import sys
import argparse

SOURCE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs')
GITHUB_BASE_URL = "https://github.com/openzfs/openzfs-docs/tree/master/docs"

def convert_rst_to_md(rst_content):
    lines = rst_content.splitlines()
    md_lines = []

    i = 0
    in_code_block = False
    block_indent = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Calculate indentation of the current line
        current_indent = 0
        if stripped:
            current_indent = len(line) - len(line.lstrip())

        # --- Handle Code Block Content ---
        if in_code_block:
            # If line is empty, it's part of the block (usually) or just spacing
            if not stripped:
                md_lines.append(line)
                i += 1
                continue

            # Check if indentation allows us to stay in block
            # If we are less indented than the block start, we exit.
            if current_indent < block_indent:
                in_code_block = False
                md_lines.append("```")
                # Fall through to process this line as normal text
            else:
                # Still in block
                md_lines.append(line)
                i += 1
                continue

        # --- Normal Line Processing ---

        # 1. Check for Headers
        # Look ahead for underline
        if i + 1 < len(lines):
            next_line = lines[i+1]
            next_stripped = next_line.strip()
            # RST headers are usually ===, ---, ~~~, ^^^, etc.
            # Must be at least as long as title or usually >= 3 chars
            if next_stripped and set(next_stripped).issubset({'=', '-', '~', '^', '"', '#', '*'}):
                if len(next_stripped) >= 3:
                    char = next_stripped[0]
                    # Approximate mapping
                    level = 2
                    if char == '=': level = 1
                    elif char == '-': level = 2
                    elif char == '~': level = 3
                    elif char == '^': level = 4
                    else: level = 3

                    md_lines.append(f"{'#' * level} {stripped}")
                    i += 2
                    continue

        # 2. Check for Directives
        # .. code-block:: or .. sourcecode::
        if stripped.startswith('.. code-block::') or stripped.startswith('.. sourcecode::'):
            parts = stripped.split('::', 1)
            lang = parts[1].strip() if len(parts) > 1 else ""

            # Determine indentation of the NEXT non-empty line
            j = i + 1
            next_indent = -1
            while j < len(lines):
                if lines[j].strip():
                    next_indent = len(lines[j]) - len(lines[j].lstrip())
                    break
                j += 1

            if next_indent > current_indent:
                in_code_block = True
                block_indent = next_indent
                md_lines.append(f"```{lang}")
                # We consume the directive line
                i += 1
                continue
            else:
                # No content? Just skip directive.
                i += 1
                continue

        # 3. Check for Literal Blocks (::)
        if stripped.endswith('::') and not stripped.startswith('..'):
            # Two cases:
            # "Some text::" -> "Some text:" and open block
            # "::" -> Open block (expanded from previous text usually)

            if stripped == '::':
                md_lines.append('')
            else:
                # Replace :: with :
                md_lines.append(line.rstrip()[:-2] + ':')

            # Check lookahead for indentation
            j = i + 1
            next_indent = -1
            while j < len(lines):
                if lines[j].strip():
                    next_indent = len(lines[j]) - len(lines[j].lstrip())
                    break
                j += 1

            if next_indent > current_indent:
                in_code_block = True
                block_indent = next_indent
                md_lines.append("```")
                i += 1
                continue
            else:
                # Not a code block, just text ending in :: (rare but possible)
                md_lines.append(line)
                i += 1
                continue

        # 4. Admonitions (Note, Warning, etc.)
        # .. note:: Content
        if stripped.startswith('.. '):
            # Check for standard admonitions
            admon_match = re.match(r'^\.\.\s+(note|warning|important|tip|caution|attention|danger|error|hint)::\s*(.*)', stripped, re.IGNORECASE)
            if admon_match:
                atype = admon_match.group(1).capitalize()
                acontent = admon_match.group(2)
                md_lines.append(f"> **{atype}:** {acontent}")
                i += 1
                continue

            # Other directives (image, toctree, etc.)
            img_match = re.match(r'^\.\.\s+image::\s+(.*)', stripped, re.IGNORECASE)
            if img_match:
                img_path = img_match.group(1).strip()
                md_lines.append(f"![Image]({img_path})")
                i += 1
                continue

            # Default: Skip the directive line, let subsequent indented lines be processed as text.
            i += 1
            continue

        # 5. Inline Formatting
        curr = line

        # Links: `Text <url>`_
        curr = re.sub(r'`([^`<]+) <([^>]+)>`_{1,2}', r'[\1](\2)', curr)

        # Roles: :doc:`Foo <path>` -> [Foo](path)
        # :ref:`Foo` -> Foo
        curr = re.sub(r':\w+:`([^`<]+) <([^>]+)>`', r'[\1](\2)', curr)
        curr = re.sub(r':\w+:`([^`]+)`', r'\1', curr)

        # Literals: ``text`` -> `text`
        curr = re.sub(r'``([^`]+)``', r'`\1`', curr)

        md_lines.append(curr)
        i += 1

    if in_code_block:
        md_lines.append("```")

    return "\n".join(md_lines)

def process_files(output_file):
    print(f"Generating {output_file} from {SOURCE_DIR}...")

    try:
        with open(output_file + ".tmp", 'w', encoding='utf-8') as outfile:
            # Write header
            outfile.write(f"# OpenZFS Documentation\n\n")
            outfile.write(f"Generated from source at {GITHUB_BASE_URL}\n\n")

            for root, _, files in os.walk(SOURCE_DIR):
                for file in sorted(files):
                    if file.endswith(".rst") and file != "404.rst":
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, SOURCE_DIR)
                        url = f"{GITHUB_BASE_URL}/{rel_path}"
                        url_encoded = url.replace(" ", "%20")

                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()

                            md_content = convert_rst_to_md(content)

                            outfile.write(f"## File: {rel_path}\n")
                            outfile.write(f"Source: {url_encoded}\n\n")
                            outfile.write(md_content)
                            outfile.write("\n\n---\n\n")

                        except Exception as e:
                            print(f"Error reading {file_path}: {e}", file=sys.stderr)

        os.replace(output_file + ".tmp", output_file)
        print(f"Successfully generated {output_file}")

    except Exception as e:
        print(f"Failed to generate {output_file}: {e}", file=sys.stderr)
        if os.path.exists(output_file + ".tmp"):
            os.remove(output_file + ".tmp")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate llms-full.txt from documentation.")
    parser.add_argument("--output", help="Path to the output file", default=os.path.join(SOURCE_DIR, 'llms-full.txt'))
    args = parser.parse_args()

    process_files(args.output)
