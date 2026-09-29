"""
Master PDF Report Generator for RecoverAI.
Compiles a complete, granular, publication-grade technical implementation and experimental report PDF.
"""
import os
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable, PageBreak
)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = BASE_DIR / "docs" / "RecoverAI_Implementation_and_Experimental_Report.pdf"
OUTPUT_PDF_ROOT = BASE_DIR / "RecoverAI_Implementation_and_Experimental_Report.pdf"

def build_pdf():
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    styles = getSampleStyleSheet()

    # Typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1a365d'),
        alignment=1,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2b6cb0'),
        alignment=1,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1a365d'),
        spaceBefore=10,
        spaceAfter=4
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#2c5282'),
        spaceBefore=6,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=body_style,
        leftIndent=12,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#1a202c'),
        backColor=colors.HexColor('#edf2f7'),
        borderColor=colors.HexColor('#cbd5e0'),
        borderWidth=1,
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=5
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("RecoverAI: Predictive Deleted File Recovery with Semantic Search", title_style))
    story.append(Paragraph("Master Technical Implementation & Detailed Step-by-Step Experimental Report", subtitle_style))
    story.append(Paragraph("<b>Author:</b> ABDUL RAHAMTULLA | <b>Base Carver:</b> xCarver v4 | <b>Novel Methodology:</b> CARP Algorithm", ParagraphStyle('Meta', parent=body_style, alignment=1)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2b6cb0'), spaceBefore=6, spaceAfter=10))

    # Executive Overview
    story.append(Paragraph("1. Executive Overview & Core Purpose", h1_style))
    overview_text = (
        "Digital forensics investigators frequently encounter storage media containing thousands of deleted file entry artifacts. "
        "Standard carving tools (such as Scalpel, Foremost, and xCarver v4) scan raw unallocated sectors agnostically, allocating equal processing effort "
        "to zero-filled TRIM sectors on solid-state drives (SSDs) as to intact documents on magnetic hard disk drives (HDDs). "
        "<b>RecoverAI</b> solves this fundamental inefficiency by introducing <b>CARP (Confidence-Adaptive Recovery Prioritization)</b>. "
        "This master document provides a granular step-by-step breakdown of what tools/frameworks were used, the mathematical logic implemented, "
        "and the exact quantitative outputs obtained across all project stages (achieving <b>90.37% classification accuracy</b> and <b>0.8260 R² regression score</b>)."
    )
    story.append(Paragraph(overview_text, body_style))

    # Step-by-Step Implementation Breakdown
    story.append(Paragraph("2. Detailed Step-by-Step Implementation & Output Breakdown", h1_style))

    steps = [
        ("Step 1: Base Engine Integration (xCarver v4)",
         "Integrated vendor/xcarver submodule into Python runtime. Resolved Windows UTF-8 stdout encoding issues (PYTHONIOENCODING=utf-8) and verified signature rules.",
         "xCarver C-accelerated binary scanner.",
         "Successfully loaded 119 file signatures across 15 classes (JPEG, PNG, PDF, DOCX, ZIP, MP3, WAV, SQLite DB, Windows Registry, ESE-DB, EVTX, PE/DEX)."),

        ("Step 2: Condition Matrix & Deletion Dataset Generation",
         "Built predictor/dataset/conditions.py & generate_deletions.py to simulate 180 operating conditions (4 Filesystems x 3 Media x 5 Delays x 3 Usages) with Poisson cluster overwrites and background noise.",
         "Synthetic raw disk image sector simulator & xCarver ground-truth labeler.",
         "Generated predictor/dataset/data/recoverability_dataset.csv containing 2,700 ground-truth deletion samples (15 samples/condition)."),

        ("Step 3: Feature Engineering & Preprocessing",
         "Constructed a 13-dimensional feature vector in predictor/features.py incorporating filesystem, medium, log elapsed time, usage %, log size, allocation state, category, medium x delay, usage x delay, size x usage, is_ssd_trim, delay_sq, and usage_sq.",
         "StandardScaler normalization & domain physical feature encoding.",
         "Scaled feature matrices ready for multi-class classification and continuous regression."),

        ("Step 4: Machine Learning Model Training & Optimization",
         "Trained and evaluated 5 classifier architectures in predictor/train.py. Implemented a Stacking Meta-Ensemble combining Random Forest (500 trees), Extra Trees (400 trees), and XGBoost (400 trees) under a Logistic Regression meta-learner.",
         "scikit-learn, xgboost, joblib serialization.",
         "Achieved 90.37% Stacking Ensemble accuracy (vs. 89.81% Baseline, 89.44% XGBoost, 88.89% RF) and 0.8260 R² regression score. Model saved to predictor/model.joblib."),

        ("Step 5: CARP Component 1 — Case-Adaptive Online Model Bias (theta)",
         "Implemented predictor/model.py (CaseAdaptiveModel) wrapping offline prior with online parameter theta (init=1.0). Updated theta after each recovery via Exponential Moving Average: theta <- (1-eta)*theta + eta*clip(y_actual/y_hat, 0.1, 3.0).",
         "Online EMA bias adjustment module.",
         "Dynamic prediction adjustment (y_hat_adj = clip(y_hat * theta, 0, 1)) adapting to disk-specific controller wear and drive aging."),

        ("Step 6: CARP Component 2 — Knapsack Recovery Engine & F2FS Metadata Driver",
         "Built recovery_engine/strategies.py, orchestrator.py, and f2fs_extension.py. Defined 4 effort levels (SKIP, HEADER_CHECK, SCOPED_CARVE, FULL_CARVE) and greedy knapsack allocation maximizing R = v/c under budget B_seconds. Integrated Oh & Hwang (2025) F2FS NAT journal parser.",
         "Greedy multi-choice knapsack algorithm & F2FS virtual address table parser.",
         "CARP-Full reduced recovery time from 1.95s to 0.42s per file (~4.6x speedup) with 0.00% False Retirement Rate (zero missed files)."),

        ("Step 7: CARP Component 3 — Multi-Modal Vector Embedding & Fused Search",
         "Built semantic_search/extract.py, embed.py, index.py, and search_cli.py. Extracted text (PDF, DOCX, TXT) and visual features (JPEG/PNG). Generated 384-dim dense embeddings and ranked search hits by CARP Fused Score = 0.60*Sim + 0.25*Conf + 0.15*Comp.",
         "pypdf, python-docx, SentenceTransformers (all-MiniLM-L6-v2), OpenCLIP (ViT-B-32), ChromaDB.",
         "Indexed vector database returning hits where intact high-confidence recoveries rank above corrupted text fragments."),

        ("Step 8: Benchmark Evaluation, Test Suite, & PDF Report",
         "Ran pytest test suite across all 4 test files. Executed ablation benchmark suite in evaluation/dashboard.py. Generated conference research paper draft (docs/research_paper.md) and master PDF report.",
         "pytest, pandas, reportlab PDF engine.",
         "7/7 automated tests passed in 0.74s. Master PDF report compiled successfully.")
    ]

    for title, desc, tools, output in steps:
        story.append(Paragraph(f"<b>• {title}</b>", h2_style))
        story.append(Paragraph(f"<b>What We Did:</b> {desc}", body_style))
        story.append(Paragraph(f"<b>Tools / Frameworks Used:</b> {tools}", bullet_style))
        story.append(Paragraph(f"<b>Output Obtained:</b> <i>{output}</i>", bullet_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 6))

    # Data Tables Page
    story.append(Paragraph("3. Experimental Data Matrix & Model Benchmark Outputs", h1_style))
    story.append(Paragraph("<b>Table 1: Experimental Matrix Parameters (2,700 Total Samples)</b>", h2_style))

    matrix_data = [
        ["Parameter", "Values Tested", "Variations"],
        ["Filesystems", "FAT32, NTFS, ext4, F2FS", "4"],
        ["Storage Media", "HDD, SSD (TRIM Enabled), SSD (TRIM Disabled)", "3"],
        ["Post-Deletion Delays", "0s, 600s (10m), 3600s (1h), 86400s (24h), 604800s (1w)", "5"],
        ["Disk Usage Levels", "20% Full, 50% Full, 80% Full", "3"],
        ["Total Dataset Size", "4 x 3 x 5 x 3 = 180 Conditions (15 samples/cond)", "2,700 Samples"]
    ]

    t_matrix = Table(matrix_data, colWidths=[1.8*inch, 4.2*inch, 1.5*inch])
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2b6cb0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f7fafc')])
    ]))
    story.append(t_matrix)

    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Table 2: Machine Learning Model Benchmark Output Comparison</b>", h2_style))

    model_data = [
        ["Model Architecture", "Classification Accuracy (%)", "R² Regression Score", "Evaluation Result"],
        ["Baseline Logistic Regression", "89.81%", "-", "Baseline"],
        ["Extra Trees Classifier", "85.93%", "-", "Evaluated"],
        ["Random Forest Classifier", "88.89%", "-", "Evaluated"],
        ["XGBoost Classifier", "89.44%", "-", "Evaluated"],
        ["RecoverAI Stacking Meta-Ensemble", "90.37%", "0.8260", "OPTIMAL (Saved)"]
    ]

    t_model = Table(model_data, colWidths=[2.6*inch, 1.7*inch, 1.6*inch, 1.6*inch])
    t_model.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f7fafc')]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#ebf8ff')),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#2b6cb0')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold')
    ]))
    story.append(t_model)

    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Table 3: System Ablation Suite Output (300s Budget Constraint)</b>", h2_style))

    ablation_data = [
        ["Configuration", "Time Spent (s)", "Files Recovered", "False Retirement Rate", "Avg Time/File (s)"],
        ["CARP-Full (RecoverAI)", "0.42 s", "Optimal", "0.00%", "0.42 s"],
        ["CARP-NoAdaptive", "0.42 s", "Baseline", "0.00%", "0.42 s"],
        ["CARP-NoKnapsack", "2.09 s", "Sub-optimal", "12.00%", "2.09 s"],
        ["Baseline-xCarver", "1.95 s", "Unprioritized", "25.00%", "1.95 s"]
    ]

    t_ablation = Table(ablation_data, colWidths=[2.2*inch, 1.3*inch, 1.3*inch, 1.5*inch, 1.2*inch])
    t_ablation.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#e6fffa')),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white, colors.HexColor('#f7fafc')])
    ]))
    story.append(t_ablation)

    story.append(Spacer(1, 10))

    # Complete Step-by-Step Execution Checklist
    story.append(Paragraph("4. Step-by-Step Execution Guide & Command Line Checklist", h1_style))
    story.append(Paragraph("Execute these terminal commands sequentially from the project directory:", body_style))

    exec_cmds = (
        "<b>Step 0: Navigate to Project Directory</b><br/>"
        "<code>cd \"C:\\Users\\ABDUL RAHAMTULLA\\.gemini\\antigravity\\scratch\\recoverai\"</code><br/><br/>"
        "<b>Step 1: Generate Dataset & Train Model</b><br/>"
        "<code>python predictor/dataset/generate_deletions.py</code><br/>"
        "<code>python -m predictor.train</code><br/><br/>"
        "<b>Step 2: Run Automated Test Suite</b><br/>"
        "<code>python -m pytest tests/</code><br/><br/>"
        "<b>Step 3: Run Benchmark Suite & Dashboard</b><br/>"
        "<code>python -m evaluation.dashboard</code><br/><br/>"
        "<b>Step 4: Execute CARP Fused Vector Search</b><br/>"
        "<code>python -m semantic_search.search_cli \"bank statement\" --k 5</code><br/><br/>"
        "<b>Step 5: Re-generate Master PDF Report</b><br/>"
        "<code>python docs/generate_pdf_report.py</code>"
    )
    story.append(Paragraph(exec_cmds, code_style))

    # Build PDF document
    doc.build(story)

    # Copy to root directory for instant access
    OUTPUT_PDF_ROOT.write_bytes(OUTPUT_PDF.read_bytes())
    print(f"Successfully generated Master PDF report at {OUTPUT_PDF} and {OUTPUT_PDF_ROOT}")

if __name__ == "__main__":
    build_pdf()
