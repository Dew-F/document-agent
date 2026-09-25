import re

MAX_CHUNK_SIZE = 2000


def chunk_markdown(text: str, max_chunk_size: int = MAX_CHUNK_SIZE) -> list[dict]:
    chunks: list[dict] = []

    heading_path: list[str] = []
    current_paragraphs: list[str] = []
    in_code_block = False

    def flush_chunk() -> None:
        if not current_paragraphs:
            return

        content = "\n\n".join(current_paragraphs).strip()

        if not content:
            return

        chunks.append(
            {
                "content": content,
                "heading_path": heading_path.copy(),
            }
        )

        current_paragraphs.clear()

    def add_paragraph(paragraph: str) -> None:
        paragraph = paragraph.strip()

        if not paragraph:
            return

        current_size = len("\n\n".join(current_paragraphs))

        if current_paragraphs and current_size + 2 + len(paragraph) <= max_chunk_size:
            current_paragraphs.append(paragraph)
            return

        if not current_paragraphs and len(paragraph) <= max_chunk_size:
            current_paragraphs.append(paragraph)
            return

        flush_chunk()

        if len(paragraph) <= max_chunk_size:
            current_paragraphs.append(paragraph)
            return

        for start in range(0, len(paragraph), max_chunk_size):
            chunks.append(
                {
                    "content": paragraph[start : start + max_chunk_size],
                    "heading_path": heading_path.copy(),
                }
            )

    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return

        paragraph = "\n".join(paragraph_lines)
        add_paragraph(paragraph)
        paragraph_lines.clear()

    for line in text.splitlines():
        fence_match = re.match(r"^\s*(`{3,}|~{3,})", line)

        if fence_match:
            in_code_block = not in_code_block
            paragraph_lines.append(line)
            continue

        if in_code_block:
            paragraph_lines.append(line)
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)

        if heading_match:
            flush_paragraph()
            flush_chunk()

            level = len(heading_match.group(1))
            title = heading_match.group(2)

            heading_path[:] = heading_path[: level - 1]
            heading_path.append(title)

            continue

        if not line.strip():
            flush_paragraph()
            continue

        paragraph_lines.append(line)

    flush_paragraph()
    flush_chunk()

    return chunks
