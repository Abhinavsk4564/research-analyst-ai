from fpdf import FPDF

def _sanitize(text: str) -> str:
    """Keeps only safe printable ASCII characters; replaces everything else with a space."""
    result = []
    for ch in text:
        code = ord(ch)
        if ch == "\n" or (32 <= code <= 126):
            result.append(ch)
        else:
            result.append(" ")
    return "".join(result)

def _wrap_text(pdf, text, max_width):
    """Manually wraps text into lines that fit max_width, breaking long words if needed."""
    words = text.split(" ")
    lines = []
    current = ""

    for word in words:
        if word == "":
            continue
        test = f"{current} {word}".strip()
        if pdf.get_string_width(test) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            if pdf.get_string_width(word) > max_width:
                chunk = ""
                for ch in word:
                    if pdf.get_string_width(chunk + ch) <= max_width:
                        chunk += ch
                    else:
                        lines.append(chunk)
                        chunk = ch
                current = chunk
            else:
                current = word

    if current:
        lines.append(current)
    return lines if lines else [""]

def _write_paragraph(pdf, text, line_height=7):
    max_width = pdf.epw
    for line in _wrap_text(pdf, text, max_width):
        pdf.cell(0, line_height, line, new_x="LMARGIN", new_y="NEXT")

def create_pdf(topic: str, style: str, report_text: str) -> bytes:
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 16)
    _write_paragraph(pdf, _sanitize(f"Research Report: {topic}"), line_height=10)
    pdf.ln(2)

    pdf.set_font("Helvetica", "I", 10)
    _write_paragraph(pdf, _sanitize(f"Report style: {style}"), line_height=8)
    pdf.ln(4)

    pdf.set_font("Helvetica", size=11)
    clean_text = _sanitize(report_text.replace("**", ""))

    for para in clean_text.split("\n"):
        para = para.strip()
        if para == "":
            pdf.ln(4)
            continue
        _write_paragraph(pdf, para)

    return bytes(pdf.output())
