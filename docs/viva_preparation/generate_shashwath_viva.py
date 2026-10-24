"""
generate_shashwath_viva.py
Generates the comprehensive PDF Viva Preparation Guide for Polusani Shashwath (Role: Dependency & Recovery Surface).
"""

import os
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable, PageBreak
)

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
from base_helper import NumberedCanvas, get_base_styles, create_header_banner

OUTPUT_PDF = BASE_DIR / "Shashwath_Dependency_Recovery_Surface_Viva_Guide.pdf"

def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )
    
    st = get_base_styles()
    story = []
    
    # Header Banner
    story.append(create_header_banner(
        student_name="Polusani Shashwath",
        role_name="Dependency & Recovery Surface",
        email="polusanishashwath123@gmail.com"
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A365D"), spaceBefore=4, spaceAfter=8))
    
    # Chapter 1
    story.append(Paragraph("Chapter 1: Role Overview & Executive Briefing", st['h1']))
    story.append(Paragraph("<b>Role Definition:</b> As the <b>Dependency & Recovery Surface Specialist</b> and Systems Architect, my core responsibility is system reliability, dependency containerization, forensic surface minimization, data persistence, and rigorous automated testing across the entire RecoverAI pipeline. I ensure that forensic operations never contaminate evidence media, that all C and Python dependencies run deterministically across platforms, and that our automated test suites mathematically verify system constraints.", st['body']))
    
    story.append(Paragraph("Spoken Pitch for External Examiners (30-Second Version):", st['h2']))
    story.append(Paragraph('"Good morning, respected examiners. My name is Polusani Shashwath, and my individual responsibility is Dependency Management and Recovery Surface Architecture. In digital forensics, tools must guarantee absolute environment reproducibility, strict chain of custody, and zero evidence contamination. I architected our containerized Docker deployment, managed Linux and C-extension dependencies for xCarver\'s Aho-Corasick scanner, engineered our SQLAlchemy SQLite relational database layer across six forensic tables, and authored our automated pytest suite that formally verifies budget caps and cost-value monotonicity across our recovery tiers."', st['callout']))
    
    story.append(Paragraph("The 1-Minute Technical Summary:", st['h2']))
    story.append(Paragraph('"Digital forensics software operates in high-stakes environments where courtroom admissibility depends on immutable auditability and zero host contamination. In my role, I mapped and minimized the recovery attack surface: establishing read-only disk block access (open in rb mode) to prevent evidence tampering, and containing volatile memory execution to prevent malicious code embedded in carved polyglots from executing during inspection. To eliminate fragmented CSV logging, I architected db_layer.py using SQLAlchemy 2.0 ORM over an ACID-compliant SQLite database across six normalized relational tables, permanently binding experiment runs to SHA-256 ground truth hashes and knapsack allocations. Finally, I authored our four automated test suites in tests/, writing property-based test cases that mathematically prove cost-yield monotonicity and budget ceiling enforcement."', st['body']))

    # Chapter 2
    story.append(Spacer(1, 4))
    story.append(Paragraph("Chapter 2: Technical Deep Dive & Systems Architecture", st['h1']))
    story.append(Paragraph("1. Forensic Recovery Surface & Chain of Custody Minimization:", st['h2']))
    story.append(Paragraph("The recovery surface defines the physical and logical boundaries where RecoverAI interacts with evidence drives, memory buffers, and operating system kernels:", st['body']))
    story.append(Paragraph("• <b>Read-Only Block Stream Isolation:</b> Disk images and raw sector buffers are accessed strictly in read-only binary mode (<code>open(path, 'rb')</code> or <code>losetup -r</code>). No temporary files, swap space, or indexing caches are ever written back to the source media.<br/>"
                           "• <b>Active Memory Containment:</b> Carved payload extraction and vector embedding generation occur in isolated user-space memory buffers, neutralizing weaponized polyglots or corrupted binaries embedded in unallocated sectors.<br/>"
                           "• <b>Air-Gapped Operational Independence:</b> The entire stack (PyTorch, ChromaDB, Sentence-Transformers, SQLite) runs 100% locally on CPU/GPU without outbound internet dependencies, preserving evidentiary confidentiality.", st['bullet']))
    
    story.append(Paragraph("2. Containerized Dependency Management (Dockerfile & docker-compose.yml):", st['h2']))
    story.append(Paragraph("Forensic reproducibility requires identical runtime environments. I built a containerized Ubuntu 22.04 LTS deployment packaging:<br/>"
                           "• <b>System C Toolchain:</b> <code>gcc</code>, <code>make</code>, and <code>libc-dev</code> required to compile xCarver's multithreaded Aho-Corasick C scanner (<code>scanner.c</code>).<br/>"
                           "• <b>Python Runtime:</b> Python 3.11 with pinned wheels for PyTorch 2.2+, XGBoost 2.0, Sentence-Transformers, ChromaDB, and SQLAlchemy 2.0.<br/>"
                           "• <b>WSL2 Kernel Boundary Handling:</b> Standardized environment variables and loop device permissions bridging Windows 11 host storage to Linux virtual filesystems.", st['body']))
    
    story.append(Paragraph("3. Relational Persistence Layer (db_layer.py):", st['h2']))
    story.append(Paragraph("I authored <code>db_layer.py</code>, replacing loose flat CSV exports with a structured SQLite database via SQLAlchemy 2.0 ORM across six normalized relational tables:", st['body']))
    story.append(Paragraph("• <code>experiments</code>: Tracks unique run_id, timestamps, git commit hash, and condition counts.<br/>"
                           "• <code>manifest</code>: Stores pre-deletion metadata (original filename, size_bytes, pre-deletion SHA-256).<br/>"
                           "• <code>verdicts</code>: Stores post-carving verification (recovered SHA-256, verdict enum, carving execution time).<br/>"
                           "• <code>predictions</code>: Logs out-of-fold ML probabilities (p_full, p_partial, expected_fraction).<br/>"
                           "• <code>allocations</code>: Logs knapsack scheduler assignments (effort_level, cost_allocated_s, yield).<br/>"
                           "• <code>search_index</code>: Maps carved files to ChromaDB document IDs and embedding model versions.", st['callout']))

    story.append(Paragraph("4. Automated Testing & Verification Suite (tests/):", st['h2']))
    story.append(Paragraph("I authored and maintained four automated test modules in <code>tests/</code>:", st['body']))
    story.append(Paragraph("• <code>test_orchestrator.py</code>: Formally proves cost-value monotonicity: <code>cost(SKIP) < cost(HEADER_CHECK) < cost(SCOPED_CARVE) < cost(FULL_CARVE)</code> and proves the knapsack optimizer never exceeds budget B.<br/>"
                           "• <code>test_predictor.py</code>: Verifies 7-dimensional feature vectors and confirms softmax probabilities sum to 1.0.<br/>"
                           "• <code>test_semantic.py</code>: Validates 384-dimensional embedding norms and verifies fused score monotonicity.<br/>"
                           "• <code>test_integration.py</code>: End-to-end integration smoke test verifying the complete recovery lifecycle.", st['bullet']))

    # Database Schema Table
    story.append(Spacer(1, 4))
    schema_data = [
        [Paragraph("<b>Table Name</b>", st['body']), Paragraph("<b>Primary Keys & FKs</b>", st['body']), Paragraph("<b>Forensic Purpose & Relational Link</b>", st['body'])],
        [Paragraph("experiments", st['body']), Paragraph("id (PK), run_id (Unique)", st['body']), Paragraph("Audit trail recording run metadata, timestamps, and commit hashes", st['body'])],
        [Paragraph("manifest", st['body']), Paragraph("id (PK), experiment_id (FK)", st['body']), Paragraph("Pre-deletion baseline storing original file names, sizes, and SHA-256", st['body'])],
        [Paragraph("verdicts", st['body']), Paragraph("id (PK), experiment_id (FK)", st['body']), Paragraph("Physical ground truth storing recovered SHA-256 and match ratios", st['body'])],
        [Paragraph("predictions", st['body']), Paragraph("id (PK), experiment_id (FK)", st['body']), Paragraph("ML audit log tracking predicted probabilities and survival fractions", st['body'])],
        [Paragraph("allocations", st['body']), Paragraph("id (PK), experiment_id (FK)", st['body']), Paragraph("Scheduler audit log tracking effort tiers, costs, and expected yields", st['body'])],
        [Paragraph("search_index", st['body']), Paragraph("id (PK), experiment_id (FK)", st['body']), Paragraph("ChromaDB linkage cross-referencing vector IDs with database records", st['body'])],
    ]
    t_schema = Table(schema_data, colWidths=[1.5*inch, 2.1*inch, 3.6*inch])
    t_schema.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_schema)

    # Chapter 3
    story.append(Spacer(1, 4))
    story.append(Paragraph("Chapter 3: Codebase Ownership & Key Functions", st['h1']))
    story.append(Paragraph("• <code>db_layer.py</code>: Implements SQLAlchemy ORM models, database engine initialization, and transaction session makers.<br/>"
                           "• <code>Dockerfile</code> & <code>docker-compose.yml</code>: Configures multi-stage containerized execution, toolchain setup, and volumes.<br/>"
                           "• <code>common/schema.py</code>: Defines immutable dataclasses and enums (<code>Filesystem</code>, <code>Medium</code>, <code>EffortLevel</code>).<br/>"
                           "• <code>tests/test_orchestrator.py</code>: Implements <code>test_cost_value_monotonicity()</code> and <code>test_budget_knapsack_allocation()</code>.<br/>"
                           "• <code>tests/test_integration.py</code>: Implements <code>test_full_recoverai_pipeline()</code> smoke test.", st['body']))

    # Chapter 4
    story.append(Spacer(1, 4))
    story.append(Paragraph("Chapter 4: Cross-Module Integration (How My Work Connects)", st['h1']))
    story.append(Paragraph("1. <b>Integration with Abdul (ML & Knapsack):</b> I test Abdul's knapsack allocation logic in <code>test_orchestrator.py</code> and persist his model predictions and knapsack schedules into the <code>predictions</code> and <code>allocations</code> database tables.<br/>"
                           "2. <b>Integration with Asmin (Threat Model & Raw Carver):</b> I manage the C-compiler toolchain and loop device mount permissions needed for Asmin's xCarver scanner, and persist her SHA-256 ground truth verdicts into the <code>verdicts</code> table.<br/>"
                           "3. <b>Integration with Chandrika (Semantic Search):</b> I test Chandrika's embedding dimensions and fused scoring logic in <code>test_semantic.py</code>, and link her ChromaDB vector collection to the <code>search_index</code> table.", st['body']))

    # Chapter 5: Top 25 Viva Questions
    story.append(Spacer(1, 4))
    story.append(Paragraph("Chapter 5: Top 25 Viva Questions & Defense Answers for Shashwath", st['h1']))
    
    qas = [
        ("Q1: What was your individual role in RecoverAI?",
         "I was the Dependency & Recovery Surface Specialist. I architected our Docker containerization, managed C and Python dependencies, minimized the forensic attack surface, built the SQLite relational database layer, and authored the automated pytest verification suite."),
        ("Q2: Why use an embedded SQLite database instead of PostgreSQL or MySQL?",
         "Digital forensics workstations operate in air-gapped, isolated environments. A client-server database like PostgreSQL introduces external server daemons, port vulnerabilities, and network configuration overhead. SQLite is an ACID-compliant, self-contained database stored as a single file that can be archived directly with case evidence."),
        ("Q3: How do you guarantee zero evidence contamination on disk images?",
         "Disk images are accessed strictly in read-only binary mode using 'rb' flags or read-only loop devices ('losetup -r'). No temporary files or indexing data are ever written to the evidence media."),
        ("Q4: What is the recovery surface and how did you minimize it?",
         "The recovery surface is the logical boundary where the tool touches raw disk sectors, memory buffers, and OS APIs. I minimized it by restricting file operations to read-only block streams and isolating carved payload inspection in memory to prevent polyglot exploit execution."),
        ("Q5: What are the 6 tables in your database schema?",
         "experiments, manifest, verdicts, predictions, allocations, and search_index."),
        ("Q6: How does test_cost_value_monotonicity verify strategy logic?",
         "It tests that time costs and accessible yields increase strictly monotonically across effort tiers: cost(SKIP) < cost(HEADER_CHECK) < cost(SCOPED_CARVE) < cost(FULL_CARVE). This proves the strategy model is mathematically sound."),
        ("Q7: What does test_budget_knapsack_allocation test?",
         "It tests that when budget B = 0.0s, all files are assigned SKIP. It also tests that under budget B = 0.50s, the sum of allocated costs never exceeds 0.50s."),
        ("Q8: Why is Docker containerization important for forensic software?",
         "Courtroom admissibility requires complete reproducibility. A container encapsulates the exact compiler (gcc), C-libraries, Python version (3.11), and ML framework versions, guaranteeing identical behavior regardless of the host OS."),
        ("Q9: What C dependencies were required for xCarver v4?",
         "gcc, make, and libc-dev were required to compile scanner.c, which implements the multithreaded Aho-Corasick automaton."),
        ("Q10: What happens if an image path does not exist when db_layer writes records?",
         "SQLAlchemy transactions wrap inserts in try-except blocks with session.rollback(), preventing partial database writes and maintaining database integrity."),
        ("Q11: How do you handle schema migrations or versioning?",
         "Our schema is managed declaratively via SQLAlchemy declarative_base(), allowing automated table creation on initial startup via Base.metadata.create_all(engine)."),
        ("Q12: What is the purpose of the allocations table?",
         "It records the knapsack scheduler's operational decision for every file, logging the assigned tier (SKIP, FULL_CARVE), allocated cost, and expected yield for forensic auditing."),
        ("Q13: How does test_integration.py validate the full pipeline?",
         "It executes an end-to-end smoke test: creating a synthetic disk image -> predicting recoverability -> running knapsack carving -> indexing in ChromaDB -> querying via natural language."),
        ("Q14: How did you test ChromaDB embedding dimensionality?",
         "In test_semantic.py, test_embedding_dimensions asserts that embed_text() returns a vector of length exactly 384 and has an L2 norm of 1.0 +/- 10^-4."),
        ("Q15: How does your database ensure chain of custody?",
         "Every experiment run generates a unique run_id timestamped at start and finish, tied to the git commit hash and storing SHA-256 pre- and post-carving hashes."),
        ("Q16: Why did you use SQLAlchemy ORM instead of raw sqlite3 queries?",
         "SQLAlchemy provides strict type safety, relationship mapping between foreign keys (e.g., verdicts tied to experiments), and connection pooling while preventing SQL injection vulnerabilities."),
        ("Q17: What environment variable configures your database path?",
         "DB_PATH, which defaults to './db/recoverai.db' if not explicitly defined."),
        ("Q18: How does the system handle corrupted or zero-byte files during text extraction?",
         "extract_text() catches extraction exceptions and falls back to filename string embeddings, preventing crashes on corrupted documents."),
        ("Q19: What is the primary bottleneck in disk I/O during testing?",
         "Repeatedly mounting and unmounting ext4 loop devices in WSL2. We mitigated this by testing against in-memory raw binary streams where possible."),
        ("Q20: How do you verify that Softmax probabilities sum to 1.0?",
         "In test_predictor.py, we assert that torch.sum(probs, dim=1) equals 1.0 within a floating-point tolerance of 10^-5."),
        ("Q21: How does your module connect to Abdul's work?",
         "I test Abdul's knapsack solver in test_orchestrator.py and persist his model predictions and allocations in the database."),
        ("Q22: How does your module connect to Asmin's work?",
         "I manage the C-compiler dependencies and loop device mount permissions for Asmin's xCarver engine, and persist her ground truth verdicts."),
        ("Q23: How does your module connect to Chandrika's work?",
         "I validate Chandrika's vector dimensions and search scoring in test_semantic.py and maintain the search_index table mapping vector IDs."),
        ("Q24: What happens if an investigator provides a corrupted SQLite file?",
         "The database engine initializes with WAL (Write-Ahead Logging) mode, enabling automatic crash recovery and transaction rollback."),
        ("Q25: What is the single most important architectural improvement you would introduce?",
         "Migrating raw sector reads to asynchronous direct I/O (O_DIRECT / io_uring in Linux) to bypass OS buffer cache and achieve true non-blocking disk saturation.")
    ]
    
    for q, a in qas:
        story.append(Paragraph(f"<b>{q}</b>", st['qa_q']))
        story.append(Paragraph(a, st['qa_a']))

    # Chapter 6: Cheat Sheet
    story.append(Spacer(1, 4))
    story.append(Paragraph("Chapter 6: Rapid Revision Cheat Sheet for Shashwath", st['h1']))
    story.append(Paragraph("• <b>Database Schema:</b> 6 relational tables: <code>experiments</code>, <code>manifest</code>, <code>verdicts</code>, <code>predictions</code>, <code>allocations</code>, <code>search_index</code><br/>"
                           "• <b>ORM Framework:</b> SQLAlchemy 2.0 over self-contained, air-gapped SQLite database (<code>db_layer.py</code>)<br/>"
                           "• <b>Forensic Integrity:</b> Read-only block access (<code>'rb'</code>), immutable SHA-256 auditing, zero evidence contamination<br/>"
                           "• <b>Testing Suites:</b> 4 pytest modules in <code>tests/</code>: <code>test_orchestrator.py</code>, <code>test_predictor.py</code>, <code>test_semantic.py</code>, <code>test_integration.py</code><br/>"
                           "• <b>Monotonicity Rule:</b> <code>cost(SKIP) < cost(HDR) < cost(SCOPED) < cost(FULL)</code> mathematically verified<br/>"
                           "• <b>Containerization:</b> Ubuntu 22.04 LTS Docker container with Python 3.11, PyTorch 2.2+, and C compiler (<code>gcc</code>, <code>make</code>)", st['callout']))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
