from __future__ import annotations

from pathlib import Path
import textwrap


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "project-architecture-execution-guide.md"
EXPORT_DIR = ROOT / "docs" / "exports"
EXPORT_MD = EXPORT_DIR / "project-architecture-execution-guide.md"
EXPORT_PDF = EXPORT_DIR / "project-architecture-execution-guide.pdf"


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _markdown_to_lines(markdown: str, width: int = 95) -> list[str]:
    lines: list[str] = []
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line:
            lines.append("")
            continue
        if line.startswith("```"):
            continue
        if line.startswith("# "):
            lines.append(line[2:].upper())
            lines.append("")
            continue
        if line.startswith("## "):
            lines.append(line[3:])
            lines.append("-" * min(len(line[3:]), width))
            continue
        if line.startswith("### "):
            lines.append(line[4:])
            continue
        bullet_prefix = ""
        content = line
        if line.startswith("- "):
            bullet_prefix = "- "
            content = line[2:]
        elif line[:2].isdigit() and line[2:4] == ". ":
            bullet_prefix = line[:4]
            content = line[4:]
        wrapped = textwrap.wrap(content, width=max(20, width - len(bullet_prefix))) or [""]
        for idx, part in enumerate(wrapped):
            prefix = bullet_prefix if idx == 0 else " " * len(bullet_prefix)
            lines.append(prefix + part)
    return lines


def _build_pdf(lines: list[str]) -> bytes:
    page_width = 612
    page_height = 792
    margin_left = 54
    margin_top = 54
    font_size = 10
    leading = 13
    max_lines = int((page_height - 2 * margin_top) / leading)

    pages = [lines[i : i + max_lines] for i in range(0, len(lines), max_lines)] or [[]]
    objects: list[bytes] = []

    def add_object(payload: str | bytes) -> int:
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        objects.append(payload)
        return len(objects)

    font_obj = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    page_obj_ids: list[int] = []
    content_obj_ids: list[int] = []
    pages_obj_placeholder = add_object("<< >>")

    for page_number, page_lines in enumerate(pages, start=1):
        content_lines = ["BT", f"/F1 {font_size} Tf", f"{margin_left} {page_height - margin_top} Td", f"{leading} TL"]
        for line in page_lines:
            content_lines.append(f"({_escape_pdf_text(line)}) Tj")
            content_lines.append("T*")
        content_lines.append(f"(Page {page_number} of {len(pages)}) Tj")
        content_lines.append("ET")
        stream = "\n".join(content_lines).encode("utf-8")
        content_obj_ids.append(
            add_object(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
        )
        page_obj_ids.append(
            add_object(
                f"<< /Type /Page /Parent {pages_obj_placeholder} 0 R /MediaBox [0 0 {page_width} {page_height}] "
                f"/Resources << /Font << /F1 {font_obj} 0 R >> >> /Contents {content_obj_ids[-1]} 0 R >>"
            )
        )

    kids = " ".join(f"{page_id} 0 R" for page_id in page_obj_ids)
    objects[pages_obj_placeholder - 1] = (
        f"<< /Type /Pages /Count {len(page_obj_ids)} /Kids [ {kids} ] >>".encode("utf-8")
    )
    catalog_obj = add_object(f"<< /Type /Catalog /Pages {pages_obj_placeholder} 0 R >>")

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_obj} 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    markdown = SOURCE.read_text(encoding="utf-8")
    EXPORT_MD.write_text(markdown, encoding="utf-8")
    EXPORT_PDF.write_bytes(_build_pdf(_markdown_to_lines(markdown)))
    print(f"generated architecture guide markdown: {EXPORT_MD}")
    print(f"generated architecture guide pdf: {EXPORT_PDF}")


if __name__ == "__main__":
    main()
