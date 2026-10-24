"""
build_all_viva_pdfs.py
Generates 4 comprehensive, publication-grade, role-specific PDF preparation guides for RecoverAI external viva.
Roles:
1. Abdul Rahamtulla Shaik - Adversarial Verification
2. Asmin Shaik - Research & Threat Model
3. Polusani Shashwath - Dependency & Recovery Surface
4. Koduru Venkata Chandrika (Chandu) - Evaluation & Reporting
"""

import os
import sys
import shutil
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable, PageBreak
)
from reportlab.pdfgen import canvas

# Running page numbering canvas
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
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
        self.drawString(36, 762, "RecoverAI (CARP) — Major Project External Viva Preparation")
        self.drawRightString(576, 762, "VIT-AP University | SCOPE")
        
        # Footer (Bottom line and page numbers)
        self.line(36, 42, 576, 42)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(36, 30, "Confidential Academic Document — Major Project Viva Defense Guide")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 30, page_str)
        self.restoreState()

def get_base_styles():
    styles = getSampleStyleSheet()
    
    h1 = ParagraphStyle(
        'V_H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1A365D'),
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True
    )
    
    h2 = ParagraphStyle(
        'V_H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body = ParagraphStyle(
        'V_Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=4
    )
    
    bullet = ParagraphStyle(
        'V_Bullet',
        parent=body,
        leftIndent=10,
        firstLineIndent=-6,
        spaceAfter=2
    )
    
    qa_q = ParagraphStyle(
        'V_QA_Q',
        parent=body,
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#9B2C2C'),
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )
    
    qa_a = ParagraphStyle(
        'V_QA_A',
        parent=body,
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#1A202C'),
        leftIndent=6,
        spaceAfter=4
    )
    
    code_block = ParagraphStyle(
        'V_Code',
        parent=body,
        fontName='Courier',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#2D3748'),
        backColor=colors.HexColor('#EDF2F7'),
        borderPadding=3,
        spaceAfter=4
    )
    
    callout = ParagraphStyle(
        'V_Callout',
        parent=body,
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#2C5282'),
        backColor=colors.HexColor('#EBF8FF'),
        borderPadding=4,
        spaceAfter=5
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
        'styles': styles
    }

def create_header_banner(student_name, role_name, email):
    header_data = [
        [
            Paragraph(f"<b><font size='12' color='#1A365D'>RecoverAI: Predictive Deleted File Recovery</font></b><br/>"
                      f"<b><font size='9' color='#2B6CB0'>CARP: Confidence-Adaptive Recovery Prioritization</font></b><br/>"
                      f"<font size='7.5' color='#718096'>Major Project External Viva Comprehensive Preparation Guide</font>", 
                      ParagraphStyle('BannerL', fontName='Helvetica', leading=11)),
            Paragraph(f"<b>Candidate:</b> {student_name}<br/>"
                      f"<b>Role:</b> <font color='#9B2C2C'><b>{role_name}</b></font><br/>"
                      f"<b>Email:</b> {email}<br/>"
                      f"<b>Affiliation:</b> VIT-AP University (SCOPE)",
                      ParagraphStyle('BannerR', fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=2))
        ]
    ]
    t = Table(header_data, colWidths=[3.7 * inch, 3.8 * inch])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    return t
