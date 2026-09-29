# RecoverAI: Predictive Deleted File Recovery with Semantic Search

**Authors**: ABDUL RAHAMTULLA et al.  
**Target Venue**: IEEE Transactions on Information Forensics and Security / Digital Investigation Journal  

---

## Abstract

Digital forensics investigators frequently encounter storage media containing thousands of deleted file entry artifacts, where running full signature-based file carving across every unallocated cluster becomes computationally prohibitive under strict time constraints. Standard carving utilities like xCarver v4 scan unallocated space agnostically, allocating equal processing effort to high-yield and heavily overwritten disk sectors alike. 

In this work, we propose **RecoverAI**, a predictive forensic recovery framework powered by **CARP (Confidence-Adaptive Recovery Prioritization)**. CARP introduces three core novel contributions:
1. **Case-Adaptive Recoverability Predictor**: An online-updating machine learning model that predicts the expected byte recovery fraction ($\hat{y} \in [0, 1]$) and categorical status (*full*, *partial*, *none*) for deleted files based on filesystem metadata, storage medium characteristics (HDD vs. SSD TRIM), disk occupancy, and post-deletion temporal decay, dynamically adjusting per-case online bias ($\theta$).
2. **Knapsack-Based Recovery Orchestration**: A multi-choice greedy knapsack allocator that optimizes investigative time budgets by dynamically selecting targeted carving effort levels (*SKIP*, *HEADER_CHECK*, *SCOPED_CARVE*, *FULL_CARVE*).
3. **CARP Fused Semantic Vector Search**: A multi-modal vector search assistant (built on Sentence-Transformers, CLIP, and ChromaDB) that ranks candidate hits by fusing semantic vector similarity with recovery confidence and byte completeness.

Empirical evaluation on a controlled 180-condition experimental matrix (2,700 file deletion samples) demonstrates that CARP improves prediction classification accuracy to **90.37%** (with an $R^2$ regression score of **0.8260**), outperforming baseline models while eliminating false file retirement under strict time budgets.

---

## 1. Introduction & Motivation

Digital forensic investigations increasingly involve multi-terabyte storage devices where tens of thousands of files have been deleted. Traditional file carving tools (such as Scalpel, Foremost, and xCarver v4) scan raw unallocated sectors byte-by-byte looking for file headers and footers. However, full-disk carving on large devices requires hours or days of execution time, generating massive volumes of fragmented false-positive outputs.

In real-world incident response, digital investigators operate under strict time budgets (e.g., 1 to 4 hours per drive). When faced with thousands of unallocated entries, an unprioritized tool spends equal computation scanning unrecoverable zero-filled TRIM sectors on solid-state drives (SSDs) as it does recovering intact documents on magnetic hard disk drives (HDDs).

To solve this gap, we present **RecoverAI**, a system that transforms file carving from a blind brute-force scan into a predictive, confidence-guided, and semantically searchable recovery workflow.

---

## 2. Related Work & Distinctions

### 2.1 Base Framework: xCarver v4
xCarver v4 is a state-of-the-art open-source signature-based file carver supporting 119 binary signature categories across diverse document, image, database, and executable formats. While xCarver v4 provides high carving precision when executed over identified sector ranges, it lacks predictive intelligence regarding whether a deleted file remains intact before scanning starts, and provides no budget-aware scheduling.

### 2.2 Advanced F2FS Metadata Carving (Oh & Hwang, 2025)
Recent forensic research by Oh & Hwang (*Forensic Science International: Digital Investigation*, 2025) demonstrated that Flash-Friendly File Systems (F2FS) store transient inode updates in Node Address Table (NAT) journals and checkpoint structures. RecoverAI incorporates an extended F2FS Virtual Address Table parser derived from Oh & Hwang's structural findings to reconstruct virtual-to-physical block mappings prior to carving.

### 2.3 Novel Contribution: CARP
Unlike existing carvers that treat every unallocated region uniformly, **RecoverAI introduces CARP (Confidence-Adaptive Recovery Prioritization)**. CARP unites machine learning recoverability prediction, multi-choice knapsack effort allocation, and confidence-fused semantic retrieval into a single unified architecture.

---

## 3. System Architecture & Methodology

RecoverAI consists of three primary stages:

```
+-----------------------------------------------------------------------------------+
|                                 RECOVERAI ENGINE                                  |
+-----------------------------------------------------------------------------------+
|  [Stage 1: Predictor]     -->  [Stage 2: Recovery Orchestrator]  -->  [Stage 3: Search] |
|  - Feature Vector Extraction   - Greedy Knapsack Allocation        - Text/CLIP Embed  |
|  - Stacking Ensemble (90.37%)  - Multi-Level Effort Dispatch       - CARP Score Fusion|
|  - Online Bias Update (\theta) - xCarver v4 / F2FS Driver           - Vector DB Index  |
+-----------------------------------------------------------------------------------+
```

### 3.1 Stage 1: Case-Adaptive Recoverability Predictor (CARP Component 1)
Given a deleted file record $r$ containing filesystem metadata, storage medium $M \in \{\text{HDD}, \text{SSD\_TRIM\_ON}, \text{SSD\_TRIM\_OFF}\}$, elapsed deletion time $t_{\text{elapsed}}$, disk usage percentage $U$, file size $S$, and allocation state $A$, we construct an enriched feature vector $\mathbf{x}$:

$$\mathbf{x} = \Big[ \text{Enc}(FS), \text{Enc}(M), \log(1 + t_{\text{elapsed}}), U, \log(1 + S), \text{Enc}(A), \text{Enc}(Cat), M \cdot \log(1 + t_{\text{elapsed}}), U \cdot \log(1 + t_{\text{elapsed}}), S_{\log} \cdot U, \text{IsTRIM}, t_{\text{log}}^2, U^2 \Big]$$

An offline Stacking Meta-Learner (comprising Random Forest, XGBoost, and Extra Trees base estimators combined by a Logistic Regression meta-classifier) outputs calibrated probabilities $[p_{\text{none}}, p_{\text{partial}}, p_{\text{full}}]$, while an XGBoost regressor estimates the expected byte recovery fraction $\hat{y} \in [0, 1]$.

To adapt to disk-specific controller wear, garbage collection rates, and aging, CARP introduces an **online adaptive parameter** $\theta$ (initialized to $1.0$). After each actual recovery attempt yielding true recovered fraction $y_{\text{actual}}$, $\theta$ updates via exponential moving average:

$$\text{Ratio} = \text{clip}\left(\frac{y_{\text{actual}}}{\hat{y}}, 0.1, 3.0\right)$$
$$\theta \leftarrow (1 - \eta) \cdot \theta + \eta \cdot \text{Ratio} \quad (\eta = 0.15)$$

Adjusted predictions become:
$$\hat{y}_{\text{adj}} = \text{clip}(\hat{y} \cdot \theta, 0.0, 1.0)$$

### 3.2 Stage 2: Recovery Orchestrator & Knapsack Allocator (CARP Component 2)
RecoverAI defines four distinct effort levels $e \in \{\text{SKIP}, \text{HEADER\_CHECK}, \text{SCOPED\_CARVE}, \text{FULL\_CARVE}\}$. Each level incurs a computational time cost $c(S, e)$ (seconds) and yields expected recovered bytes $v(\hat{y}_{\text{adj}}, S, e)$:

$$c(S, e) = \left(\frac{S}{1048576}\right) \cdot \text{CostPerMB}[e]$$
$$v(\hat{y}_{\text{adj}}, S, e) = \hat{y}_{\text{adj}} \cdot S \cdot \text{YieldFactor}[e]$$

The orchestrator ranks candidate choices by marginal efficiency ratio $R(r, e) = \frac{v}{c}$ and assigns optimal effort levels using a greedy multi-choice knapsack allocation under investigator budget constraint $B_{\text{seconds}}$.

### 3.3 Stage 3: CARP Fused Semantic Search (CARP Component 3)
Recovered artifacts are embedded into vector space using `sentence-transformers` (`all-MiniLM-L6-v2`) for text documents and `open_clip` (`ViT-B-32`) for visual image evidence.

When an investigator queries the evidence repository, search hits are ranked by **CARP Fused Score**:

$$\text{FusedScore} = \alpha \cdot \text{Similarity} + \beta \cdot \text{RecoveryConfidence} + \gamma \cdot \text{CompletenessFraction}$$

where default weights $\alpha = 0.60$, $\beta = 0.25$, and $\gamma = 0.15$ ensure that highly intact, confident recoveries are prioritized over partial, corrupted fragments that happen to match keywords.

---

## 4. Experimental Setup & Empirical Results

### 4.1 Dataset & Condition Matrix
To evaluate RecoverAI, we constructed a comprehensive experimental dataset spanning 180 distinct operating conditions:
- **Filesystems**: FAT32, NTFS, ext4, F2FS
- **Media Types**: HDD, SSD (TRIM Enabled), SSD (TRIM Disabled)
- **Post-Deletion Delays**: 0s, 10 min, 1 hr, 24 hr, 1 week
- **Disk Usage Levels**: 20%, 50%, 80%

A total of **2,700 sample file deletion records** across 5 signature categories (JPEG, PDF, DOCX, MP3, SQLite DB) were generated and evaluated.

### 4.2 Model Performance

| Model Architecture | Accuracy (%) | R² Score |
|---|---|---|
| Baseline Logistic Regression | 89.81% | - |
| Extra Trees Classifier | 85.93% | - |
| Random Forest Classifier | 88.89% | - |
| XGBoost Classifier | 89.44% | - |
| **RecoverAI Stacking Meta-Ensemble** | **90.37%** | **0.8260** |

The Stacking Meta-Ensemble achieved **90.37% classification accuracy** and an **R² score of 0.8260** on continuous fraction prediction, outperforming single-model baselines.

### 4.3 Ablation Study Benchmark

We evaluated RecoverAI across four system configurations on a benchmark evaluation suite:

| Configuration | Time Spent (s) | Files Recovered | False Retirement Rate (FRR) | Avg Time per Recovery (s) |
|---|---|---|---|---|
| **CARP-Full** | **0.42 s** | **Optimal** | **0.00%** | **0.42 s** |
| CARP-NoAdaptive | 0.42 s | Baseline | 0.00% | 0.42 s |
| CARP-NoKnapsack | 2.09 s | Sub-optimal | 12.00% | 2.09 s |
| Baseline-xCarver | 1.95 s | Unprioritized | 25.00% | 1.95 s |

---

## 5. Conclusion

RecoverAI presents a predictive, confidence-adaptive file recovery framework for digital forensics. By combining Stacking Ensemble recoverability prediction (**90.37% accuracy**, **0.8260 R² score**), greedy knapsack time-budget allocation, F2FS virtual address table parsing, and CARP fused semantic vector search, RecoverAI eliminates unprioritized scanning overhead and maximizes evidence retrieval under strict investigation time budgets.
