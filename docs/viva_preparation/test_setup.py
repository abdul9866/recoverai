import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable, PageBreak
)
from reportlab.pdfgen import canvas

class MasterNumberedCanvas(canvas.Canvas):
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
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header (Top line and title)
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.75)
        self.line(36, 756, 576, 756)
        self.drawString(36, 762, "RecoverAI (CARP) — Complete Project Master Defense & Viva Guide")
        self.drawRightString(576, 762, "VIT AP UNIVERSITY | SCOPE")
        
        # Footer (Bottom line and page numbers)
        self.line(36, 42, 576, 42)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(36, 30, "Confidential Academic Document — Universal Team Defense Handbook")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 30, page_str)
        self.restoreState()

def get_master_styles():
    styles = getSampleStyleSheet()
    
    h1 = ParagraphStyle(
        'M_H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=15,
        textColor=colors.HexColor('#1A365D'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    h2 = ParagraphStyle(
        'M_H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body = ParagraphStyle(
        'M_Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=3
    )
    
    bullet = ParagraphStyle(
        'M_Bullet',
        parent=body,
        leftIndent=8,
        firstLineIndent=-5,
        spaceAfter=2
    )
    
    qa_q = ParagraphStyle(
        'M_QA_Q',
        parent=body,
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#9B2C2C'),
        spaceBefore=4,
        spaceAfter=1.5,
        keepWithNext=True
    )
    
    qa_a = ParagraphStyle(
        'M_QA_A',
        parent=body,
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.2,
        textColor=colors.HexColor('#1A202C'),
        leftIndent=5,
        spaceAfter=3.5
    )
    
    code_block = ParagraphStyle(
        'M_Code',
        parent=body,
        fontName='Courier',
        fontSize=6.8,
        leading=8.8,
        textColor=colors.HexColor('#2D3748'),
        backColor=colors.HexColor('#EDF2F7'),
        borderPadding=3,
        spaceAfter=3
    )
    
    callout = ParagraphStyle(
        'M_Callout',
        parent=body,
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor('#1A365D'),
        backColor=colors.HexColor('#EBF8FF'),
        borderPadding=4,
        spaceAfter=4
    )

    alert_box = ParagraphStyle(
        'M_Alert',
        parent=body,
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor('#742A2A'),
        backColor=colors.HexColor('#FFF5F5'),
        borderPadding=4,
        spaceAfter=4
    )
    
    return {
        'h1': h1,
        'h2': h2,
        'body': body,
        'bullet': bullet,
        'qa_q': qa_q,
        'qa_a': qa_a,
        'code': code_block,
        'callout': callout,
        'alert': alert_box,
        'styles': styles
    }

print("Base setup verified.")
