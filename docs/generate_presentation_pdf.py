"""Academic PowerPoint / PDF Slide Deck Generator.
Compiles the 18-slide presentation deck into a widescreen (16:9) presentation PDF
with slide headers, bullet points, speaker notes, and aesthetic academic styling.

Project: AI-Driven CI/CD Pipeline Optimization
Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
"""

from pathlib import Path
import sys
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DOCS_DIR


class SlideCanvas(canvas.Canvas):
    """Draws slide borders, headers, and footer banners."""
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
            self.draw_slide_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_slide_decorations(self, total_slides):
        self.saveState()
        # Header banner line
        self.setFillColor(colors.HexColor("#1e3a8a"))
        self.rect(0, 7.2 * 72, 13.33 * 72, 0.3 * 72, fill=True, stroke=False)

        # Footer banner
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(1)
        self.line(0.5 * 72, 0.5 * 72, 12.83 * 72, 0.5 * 72)

        self.setFont("Helvetica-Bold", 9)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawString(0.5 * 72, 0.3 * 72, "AI-Driven CI/CD Pipeline Optimization — MCA Major Project")
        self.setFont("Helvetica", 9)
        self.drawString(5.0 * 72, 0.3 * 72, "NAGARJUNREDDY (1DS25MC052) | Guide: Prof. Mahendra Kumar B | DSCE")
        self.drawRightString(12.83 * 72, 0.3 * 72, f"Slide {self._pageNumber} of {total_slides}")
        self.restoreState()


def generate_presentation_pdf():
    slides_md = DOCS_DIR / "PRESENTATION_SLIDES.md"
    pdf_out = DOCS_DIR / "PRESENTATION_SLIDES.pdf"

    if not slides_md.exists():
        raise FileNotFoundError(f"Missing slides markdown at {slides_md}")

    # Widescreen 16:9 dimension: 13.33 x 7.5 inches
    widescreen = (13.33 * inch, 7.5 * inch)

    doc = SimpleDocTemplate(
        str(pdf_out),
        pagesize=widescreen,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )

    styles = getSampleStyleSheet()

    slide_title_style = ParagraphStyle(
        "SlideTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=12,
    )

    bullet_style = ParagraphStyle(
        "SlideBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=18,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=15,
        spaceAfter=6,
    )

    notes_style = ParagraphStyle(
        "SpeakerNotes",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#475569"),
        backColor=colors.HexColor("#f8fafc"),
        borderColor=colors.HexColor("#cbd5e1"),
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=10,
    )

    raw_text = slides_md.read_text(encoding="utf-8")
    sections = raw_text.split("### SLIDE ")

    story = []

    for idx, sec in enumerate(sections[1:], 1):
        lines = sec.strip().splitlines()
        slide_title = lines[0].split(":", 1)[1].strip() if ":" in lines[0] else lines[0].strip()

        story.append(Paragraph(f"Slide {idx}: {slide_title}", slide_title_style))
        story.append(Spacer(1, 8))

        bullets = []
        speaker_notes = []
        in_notes = False

        for line in lines[1:]:
            sline = line.strip()
            if sline.startswith("> **Speaker Notes:**"):
                in_notes = True
                speaker_notes.append(sline.replace("> **Speaker Notes:**", "").strip())
            elif in_notes:
                if sline.startswith(">"):
                    speaker_notes.append(sline.replace(">", "").strip())
                elif sline:
                    speaker_notes.append(sline)
            elif sline.startswith("- ") or sline.startswith("* "):
                bullets.append(sline[2:].strip())

        # Render bullets
        for b in bullets:
            story.append(Paragraph(f"• {b}", bullet_style))

        # Render speaker notes at bottom of slide
        if speaker_notes:
            story.append(Spacer(1, 10))
            notes_text = "<b>Speaker Notes:</b> " + " ".join(speaker_notes).replace('"', '')
            story.append(Paragraph(notes_text, notes_style))

        story.append(PageBreak())

    doc.build(story, canvasmaker=SlideCanvas)
    print(f"[+] Successfully generated Widescreen Presentation PDF: {pdf_out}")
    print(f"    - Total Slides: {len(sections)-1} slides")
    print(f"    - File size: {pdf_out.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    generate_presentation_pdf()
