"""
generate_chandu_viva.py
Generates the comprehensive PDF Viva Preparation Guide for Koduru Venkata Chandrika (Chandu) (Role: Evaluation & Reporting).
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

OUTPUT_PDF = BASE_DIR / "Chandu_Evaluation_Reporting_Viva_Guide.pdf"

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
        student_name="Koduru Venkata Chandrika (Chandu)",
        role_name="Evaluation & Reporting",
        email="koduruvenkatachandrika2006@gmail.com"
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A365D"), spaceBefore=4, spaceAfter=8))
    
    # Chapter 1
    story.append(Paragraph("Chapter 1: Role Overview & Executive Briefing", st['h1']))
    story.append(Paragraph("<b>Role Definition:</b> As the <b>Evaluation & Reporting Specialist</b> and Semantic Search Engineer, my core responsibility is transforming raw, cryptic carved files into semantically searchable evidence, formulating our multi-factor retrieval ranking function, evaluating information retrieval metrics (Precision@K), and engineering publication-grade visualization dashboards and automated PDF reports.", st['body']))
    
    story.append(Paragraph("Spoken Pitch for External Examiners (30-Second Version):", st['h2']))
    story.append(Paragraph('"Good morning, respected examiners. My name is Koduru Venkata Chandrika, and my individual responsibility is Evaluation, Reporting, and Semantic Search Architecture. When forensic carvers extract files, they dump thousands of documents into flat directories under cryptic names like carved_001.pdf, forcing analysts to manually inspect each file. I designed our dense vector retrieval pipeline using all-MiniLM-L6-v2 embeddings and ChromaDB vector indexing. Furthermore, I authored our Fused Ranking Function that blends semantic similarity with ML confidence and physical block completeness, achieving perfect Precision@1 and Precision@3 across our investigative query benchmarks while generating automated publication-grade evaluation dashboards."', st['callout']))
    
    story.append(Paragraph("The 1-Minute Technical Summary:", st['h2']))
    story.append(Paragraph('"Traditional keyword searching in digital forensics fails when documents are fragmented, paraphrased, or corrupted. In RecoverAI, I implemented an intelligent evidence indexing engine. First, I built an automated multi-format text extraction pipeline supporting PDF, DOCX, and TXT files. Second, I integrated the all-MiniLM-L6-v2 SentenceTransformer model to project text into a 384-dimensional dense latent space indexed inside ChromaDB using HNSW graphs. Third, recognizing that raw cosine similarity often surfaces corrupted text fragments containing coincidental keyword matches, I formulated the Fused Score: weighting cosine similarity at 60%, ML pre-carve confidence at 25%, and verified block completeness at 15%. This ensured that genuine, intact evidence consistently outranked damaged fragments, delivering Precision@1 = 1.000 across eight natural-language investigative test queries."', st['body']))

    # Chapter 2
    story.append(Spacer(1, 4))
    story.append(Paragraph("Chapter 2: Technical Deep Dive & Mathematical Formulations", st['h1']))
    story.append(Paragraph("1. Dense Vector Semantic Search Architecture:", st['h2']))
    story.append(Paragraph("I implemented the complete evidence indexing and query resolution pipeline in <code>semantic_search/</code>:", st['body']))
    story.append(Paragraph("• <b>Multi-Format Extraction (extract.py):</b> Ingests recovered raw files, determines MIME categories, and extracts clean textual payloads from PDFs (PyPDF), Word documents (python-docx), and plain text files. Fallback logic prevents crashes on partially corrupted headers.<br/>"
                           "• <b>Dense Representation (embed.py):</b> Deploys <code>all-MiniLM-L6-v2</code> mapping text chunks into a 384-dimensional unit-normalized latent space (||v||_2 = 1.0). Operates 5x faster than BERT-base with sub-millisecond inference per document.<br/>"
                           "• <b>Multimodal Extension:</b> Integrated OpenCLIP (<code>ViT-B-32</code>) for image embedding, enabling cross-modal visual evidence indexing.<br/>"
                           "• <b>ChromaDB Vector Store (index.py):</b> Configured persistent collection <code>recovered_files</code> using Hierarchical Navigable Small World (HNSW) graphs over cosine distance.", st['bullet']))
    
    story.append(Paragraph("2. The Fused Semantic Ranking Function Formula:", st['h2']))
    story.append(Paragraph("In digital forensics, ranking purely by text cosine similarity is dangerous because an overwritten text fragment can coincidentally contain query keywords while being 80% corrupt. I formulated the composite Fused Score:", st['body']))
    story.append(Paragraph("<b>F(q, d) = 0.60 * CosineSimilarity(q, d) + 0.25 * (P_FULL + P_PARTIAL) + 0.15 * BlockCompleteness</b><br/>"
                           "• <b>0.60 CosineSimilarity:</b> Ensures semantic query alignment remains the primary retrieval driver.<br/>"
                           "• <b>0.25 ML Confidence:</b> Rewards documents where Abdul's ML predictor independently confirmed intact cluster structure.<br/>"
                           "• <b>0.15 BlockCompleteness:</b> Rewards files where Asmin's verification proved non-zero byte payloads.", st['callout']))

    story.append(Paragraph("3. Information Retrieval Evaluation Metrics (evaluation/metrics.py):", st['h2']))
    story.append(Paragraph("I implemented the evaluation harness measuring search efficacy across eight representative investigative queries:", st['body']))
    story.append(Paragraph("• <b>Precision@K:</b> P@K = (Relevant Documents in Top K) / K.<br/>"
                           "• <b>Precision@1 = 1.000:</b> In 100% of test queries, the exact expected evidentiary document was returned at Rank #1.<br/>"
                           "• <b>Precision@3 = 1.000:</b> Across all queries, the top 3 results contained 100% relevant evidentiary targets.<br/>"
                           "• <b>Statistical Metrics:</b> I also co-authored <code>evaluation/metrics.py</code> calculating Categorical Accuracy (0.8270), Macro AUC-ROC (0.8371), Weighted F1 (0.7915), and False Retirement Rate (15.18%).", st['bullet']))

    story.append(Paragraph("4. Automated Reporting & Visualization Engine (docs/):", st['h2']))
    story.append(Paragraph("I authored the automated visualization and reporting scripts: <code>docs/generate_figures.py</code> (generating ROC curves, 3-class confusion matrices, and XGBoost feature importance rankings) and <code>docs/generate_master_results_pdf.py</code> (compiling publication-grade PDF results summaries).", st['body']))

    # Table of Semantic Search Queries
    story.append(Spacer(1, 4))
    search_data = [
        [Paragraph("<b>Natural Language Query</b>", st['body']), Paragraph("<b>Expected File Target</b>", st['body']), Paragraph("<b>Top Ranked Output</b>", st['body']), Paragraph("<b>P@1</b>", st['body']), Paragraph("<b>P@3</b>", st['body'])],
        [Paragraph("recipe for Italian pasta carbonara", st['body']), Paragraph("cooking_recipe.txt", st['body']), Paragraph("cooking_recipe.txt", st['body']), Paragraph("1.0", st['body']), Paragraph("1.0", st['body'])],
        [Paragraph("UEFA Champions League football match", st['body']), Paragraph("football_report.txt", st['body']), Paragraph("football_report.txt", st['body']), Paragraph("1.0", st['body']), Paragraph("1.0", st['body'])],
        [Paragraph("corporate tax invoice VAT payment", st['body']), Paragraph("tax_invoice.pdf", st['body']), Paragraph("tax_invoice.pdf", st['body']), Paragraph("1.0", st['body']), Paragraph("1.0", st['body'])],
        [Paragraph("Python data structures algorithm", st['body']), Paragraph("python_tutorial.txt", st['body']), Paragraph("python_tutorial.txt", st['body']), Paragraph("1.0", st['body']), Paragraph("1.0", st['body'])],
        [Paragraph("James Webb telescope exoplanet", st['body']), Paragraph("astronomy_article.txt", st['body']), Paragraph("astronomy_article.txt", st['body']), Paragraph("1.0", st['body']), Paragraph("1.0", st['body'])],
        [Paragraph("penetration testing cybersecurity", st['body']), Paragraph("cybersecurity_guide.txt", st['body']), Paragraph("cybersecurity_guide.txt", st['body']), Paragraph("1.0", st['body']), Paragraph("1.0", st['body'])],
        [Paragraph("machine learning gradient boosting", st['body']), Paragraph("ml_research_notes.txt", st['body']), Paragraph("ml_research_notes.txt", st['body']), Paragraph("1.0", st['body']), Paragraph("1.0", st['body'])],
        [Paragraph("Japan travel itinerary Tokyo Kyoto", st['body']), Paragraph("travel_itinerary.docx", st['body']), Paragraph("travel_itinerary.docx", st['body']), Paragraph("1.0", st['body']), Paragraph("1.0", st['body'])],
        [Paragraph("<b>Mean Evaluation Benchmark Score</b>", st['body']), Paragraph("<b>---</b>", st['body']), Paragraph("<b>---</b>", st['body']), Paragraph("<b>1.000</b>", st['body']), Paragraph("<b>1.000</b>", st['body'])],
    ]
    t_search = Table(search_data, colWidths=[2.2*inch, 1.6*inch, 1.6*inch, 0.8*inch, 0.8*inch])
    t_search.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EBF8FF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_search)

    # Chapter 3
    story.append(Spacer(1, 4))
    story.append(Paragraph("Chapter 3: Codebase Ownership & Key Functions", st['h1']))
    story.append(Paragraph("• <code>semantic_search/extract.py</code>: Implements <code>extract_text()</code>, handling PDF, DOCX, and TXT decoding with fallback handling.<br/>"
                           "• <code>semantic_search/embed.py</code>: Implements <code>embed_text()</code> (all-MiniLM-L6-v2), <code>embed_image()</code> (CLIP), and fallback vectors.<br/>"
                           "• <code>semantic_search/index.py</code>: Manages ChromaDB collections, persistent HNSW indexing, and executes <code>fused_search()</code>.<br/>"
                           "• <code>semantic_search/search_cli.py</code>: Command-line interface for forensic queries.<br/>"
                           "• <code>evaluation/metrics.py</code>: Implements <code>precision_at_k()</code>, <code>detection_accuracy()</code>, and <code>false_retirement_rate()</code>.<br/>"
                           "• <code>docs/generate_figures.py</code>: Generates ROC curves, confusion matrices, and model comparison bar charts.", st['body']))

    # Chapter 4
    story.append(Spacer(1, 4))
    story.append(Paragraph("Chapter 4: Cross-Module Integration (How My Work Connects)", st['h1']))
    story.append(Paragraph("1. <b>Integration with Abdul (ML Predictor):</b> Abdul's ensemble outputs P_FULL and P_PARTIAL probabilities. My Fused Ranking Function takes these values directly as a 25% weight in scoring search candidates.<br/>"
                           "2. <b>Integration with Asmin (Carving & Ground Truth):</b> Asmin's xCarver engine produces the carved files that my extraction pipeline reads. Her SHA-256 block match ratio supplies the BlockCompleteness metric for my fused score.<br/>"
                           "3. <b>Integration with Shashwath (Database & QA):</b> Shashwath maps my ChromaDB document IDs into the <code>search_index</code> table and tests my embedding dimensions in <code>test_semantic.py</code>.", st['body']))

    # Chapter 5: Top 25 Viva Questions
    story.append(Spacer(1, 4))
    story.append(Paragraph("Chapter 5: Top 25 Viva Questions & Defense Answers for Chandu", st['h1']))
    
    qas = [
        ("Q1: What was your individual role in RecoverAI?",
         "I was the Evaluation & Reporting Specialist and Semantic Search Engineer. I built the dense vector search pipeline using all-MiniLM-L6-v2 and ChromaDB, formulated the Fused Ranking Function, evaluated Precision@K metrics, and generated publication-grade visualization dashboards."),
        ("Q2: Why is raw cosine similarity dangerous in digital forensics?",
         "In forensics, unallocated sectors often contain fragmented or overwritten text. A corrupt text fragment might coincidentally contain matching keywords and score high on raw cosine similarity. The Fused Score penalizes corrupted fragments by factoring in ML confidence and block completeness."),
        ("Q3: Explain your Fused Ranking Function formula.",
         "F(q, d) = 0.60 * CosineSimilarity(q, d) + 0.25 * (P_FULL + P_PARTIAL) + 0.15 * BlockCompleteness. It guarantees that high query relevance only ranks top if the file has verified structural and block integrity."),
        ("Q4: Why choose all-MiniLM-L6-v2 instead of BERT-base?",
         "all-MiniLM-L6-v2 generates 384-dimensional embeddings (compared to 768 for BERT-base) and executes 5x faster with minimal semantic loss. In forensic triage on edge laptops, low latency and small memory footprints are critical."),
        ("Q5: What was your Precision@1 and Precision@3 score across test queries?",
         "Precision@1 = 1.000 and Precision@3 = 1.000 across all eight representative natural-language test queries."),
        ("Q6: How does ChromaDB index vectors?",
         "ChromaDB uses Hierarchical Navigable Small World (HNSW) graphs, an approximate nearest neighbor (ANN) indexing structure that delivers logarithmic search time O(log N) over vector spaces."),
        ("Q7: What distance metric did you configure in ChromaDB?",
         "Cosine distance (1 - cosine_similarity). Since our embeddings are L2 unit-normalized, cosine distance is monotonically equivalent to squared Euclidean distance."),
        ("Q8: How does your text extractor handle corrupted PDFs?",
         "extract_text() catches parsing exceptions (e.g., EOF marker missing or broken zlib streams) and falls back to filename string embeddings, preventing pipeline crashes on corrupted evidence."),
        ("Q9: What happens if ChromaDB is offline or unavailable?",
         "embed.py contains an automated fallback (_fallback_vector) that generates deterministic pseudo-embeddings from SHA-256 byte hashes, allowing unit tests and offline pipelines to function."),
        ("Q10: What is Precision@K and how is it calculated?",
         "Precision@K measures the proportion of relevant documents within the top K returned results: P@K = (Relevant in Top K) / min(K, total returned)."),
        ("Q11: What were the 8 test query categories evaluated in Deliverable C?",
         "Cooking recipe, football match, corporate tax invoice, Python algorithm, astronomy James Webb telescope, cybersecurity penetration testing, machine learning notes, and travel itinerary."),
        ("Q12: How does your module integrate with Abdul's work?",
         "I ingest Abdul's predicted recovery confidence (P_FULL + P_PARTIAL) as the 0.25-weighted term in my fused search ranking formula."),
        ("Q13: How does your module integrate with Asmin's work?",
         "Asmin provides the carved file artifacts that I parse for text, and her byte-level block match ratio provides the BlockCompleteness metric for my fused score."),
        ("Q14: How does your module integrate with Shashwath's work?",
         "Shashwath links my ChromaDB document IDs to the relational search_index table and validates my vector dimensions in test_semantic.py."),
        ("Q15: Why did you include OpenCLIP in embed.py?",
         "To support multimodal forensic search, allowing investigators to search recovered JPEG images using natural-language descriptive queries via ViT-B-32."),
        ("Q16: How do you normalize embeddings?",
         "Vectors are divided by their Euclidean L2 norm: v_norm = v / np.linalg.norm(v). This ensures dot products directly equal cosine similarities."),
        ("Q17: What was the macro AUC-ROC score of the ensemble?",
         "0.8371, demonstrating strong discrimination across all three classes despite heavy class imbalance."),
        ("Q18: What was the weighted F1 score of the ensemble?",
         "0.7915 under 5-fold stratified cross-validation."),
        ("Q19: What scripts did you use to generate the paper figures?",
         "docs/generate_figures.py generated confusion_matrices_all.png, roc_curves.png, model_comparison.png, and feature_importance.png."),
        ("Q20: What did the XGBoost feature importance chart reveal?",
         "Post-deletion filler volume (filler_MB) was the dominant feature (>35% split gain), followed by pre-deletion occupancy (>20%), proving that post-deletion overwriting is the primary threat to file recovery."),
        ("Q21: How does your system compare to Amato et al. (2020)?",
         "Amato et al. introduced ontology-based semantic indexing for forensics. RecoverAI advances beyond ontologies by using deep sentence vector embeddings combined with pre-carving ML confidence scoring."),
        ("Q22: Why did you evaluate 8 queries instead of random keyword searches?",
         "The 8 queries represent diverse real-world investigative scenarios spanning financial crime, corporate leaks, personal travel, and technical data, rigorously testing semantic synonym matching."),
        ("Q23: How fast is query execution in ChromaDB?",
         "Query encoding via all-MiniLM-L6-v2 takes ~12 ms, and HNSW vector traversal takes under 2 ms, delivering total query turnaround under 15 ms."),
        ("Q24: What is the benefit of generating automated PDF reports?",
         "In law enforcement and digital forensics, investigative findings must be presented in court-admissible technical summary reports. Our automated generator produces complete, audited PDF evidence summaries."),
        ("Q25: What is the single biggest improvement you would make to semantic search?",
         "Implementing hybrid search combining dense vector embeddings with sparse BM25 keyword matching (Reciprocal Rank Fusion), ensuring exact alphanumeric terms like serial numbers or IP addresses are never missed.")
    ]
    
    for q, a in qas:
        story.append(Paragraph(f"<b>{q}</b>", st['qa_q']))
        story.append(Paragraph(a, st['qa_a']))

    # Chapter 6: Cheat Sheet
    story.append(Spacer(1, 4))
    story.append(Paragraph("Chapter 6: Rapid Revision Cheat Sheet for Chandu", st['h1']))
    story.append(Paragraph("• <b>Embedding Model:</b> <code>all-MiniLM-L6-v2</code> (384-dimensional dense vectors, unit-normalized)<br/>"
                           "• <b>Vector Database:</b> ChromaDB with persistent HNSW index over cosine distance (<code>semantic_search/index.py</code>)<br/>"
                           "• <b>Fused Score:</b> <code>F(q,d) = 0.60*Cosine + 0.25*(P_FULL + P_PARTIAL) + 0.15*BlockCompleteness</code><br/>"
                           "• <b>Retrieval Benchmark:</b> Precision@1 = 1.000, Precision@3 = 1.000 across 8 investigative test queries<br/>"
                           "• <b>Reporting Engine:</b> <code>generate_figures.py</code> (ROC curves, confusion matrices) and <code>generate_pdf_report.py</code><br/>"
                           "• <b>Key Code:</b> <code>semantic_search/embed.py</code>, <code>extract.py</code>, <code>index.py</code>, <code>evaluation/metrics.py</code>", st['callout']))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
