"""Academic Project Report PDF Generator.
Compiles the comprehensive 33-chapter project report into a publication-grade PDF
using ReportLab with formal academic styling, cover page, and page numbering.

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

from pathlib import Path
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DOCS_DIR


class NumberedCanvas(canvas.Canvas):
    """Adds running headers and footers with dynamic page counts."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            # Header
            self.drawString(54, 750, "AI-Driven CI/CD Pipeline Optimization — MCA Major Project (DSCE)")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

            # Footer
            self.line(54, 45, 558, 45)
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 32, page_text)
            self.drawString(54, 32, "Student: NAGARJUNREDDY (1DS25MC052) | Guide: Prof. Mahendra Kumar B")
            self.restoreState()


def generate_pdf_report():
    report_md_path = DOCS_DIR / "FINAL_PROJECT_REPORT.md"
    pdf_out_path = DOCS_DIR / "FINAL_PROJECT_REPORT.pdf"

    if not report_md_path.exists():
        raise FileNotFoundError(f"Markdown report missing at {report_md_path}")

    md_content = report_md_path.read_text(encoding="utf-8")

    doc = SimpleDocTemplate(
        str(pdf_out_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    
    # Custom Academic Styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f172a"),
        alignment=1,
        spaceAfter=15,
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#334155"),
        alignment=1,
        spaceAfter=30,
    )
    h1_style = ParagraphStyle(
        "CustomH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "CustomH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "CustomBullet",
        parent=body_style,
        leftIndent=15,
        spaceAfter=3,
    )

    story = []

    # Title Page Banner
    story.append(Spacer(1, 40))
    story.append(Paragraph("AI-DRIVEN CI/CD PIPELINE OPTIMIZATION", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("A Major Project Report Submitted in Partial Fulfillment of the Requirements for the Award of the Degree of<br/><b>MASTER OF COMPUTER APPLICATIONS</b>", subtitle_style))
    story.append(Spacer(1, 40))

    meta_text = """
    <b>Candidate:</b> NAGARJUNREDDY (USN: 1DS25MC052)<br/><br/>
    <b>Project Guide:</b> Prof. Mahendra Kumar B<br/><br/>
    <b>Department:</b> Master of Computer Applications (MCA)<br/>
    <b>Institution:</b> Dayananda Sagar College of Engineering, Bangalore-560078<br/>
    <b>Affiliation:</b> Visvesvaraya Technological University (VTU), Belagavi<br/>
    <b>Academic Year:</b> 2026–2027
    """
    story.append(Paragraph(meta_text, subtitle_style))
    story.append(PageBreak())

    # Parse markdown content into ReportLab flowables
    lines = md_content.splitlines()
    in_table = False
    table_rows = []

    for line in lines:
        stripped = line.strip()

        # Handle Tables
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if not in_table:
                in_table = True
                table_rows = [cells]
            else:
                # Check if separator row (contains ---)
                if any("---" in c for c in cells):
                    continue
                table_rows.append(cells)
            continue
        elif in_table:
            # End of table block
            in_table = False
            if table_rows:
                # Format table
                data = [[Paragraph(f"<b>{c}</b>" if idx == 0 else c, body_style) for c in row] for idx, row in enumerate(table_rows)]
                t = Table(data, colWidths=[504 / max(1, len(table_rows[0]))] * len(table_rows[0]))
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(t)
                story.append(Spacer(1, 8))
            table_rows = []

        if not stripped:
            story.append(Spacer(1, 4))
            continue

        if stripped.startswith("# "):
            # Top level title already handled on cover
            continue
        elif stripped.startswith("## "):
            text = stripped[3:].strip()
            story.append(Paragraph(text, h1_style))
        elif stripped.startswith("### "):
            text = stripped[4:].strip()
            story.append(Paragraph(text, h2_style))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            text = f"• {stripped[2:].strip()}"
            story.append(Paragraph(text, bullet_style))
        elif stripped.startswith("---"):
            story.append(Spacer(1, 6))
        else:
            story.append(Paragraph(stripped, body_style))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully generated official PDF Project Report: {pdf_out_path}")
    print(f"    - File size: {pdf_out_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    generate_pdf_report()
