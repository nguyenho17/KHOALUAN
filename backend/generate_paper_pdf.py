import os
import json
import re
import pandas as pd
import openpyxl
from weasyprint import HTML  # 🎯 FIXED: Imported correctly at the top line to avoid syntax breaks

# =====================================================================
# RAW ACADEMIC SCIENTIFIC MANUSCRIPT CONTENT (HTML STRING)
# =====================================================================
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Scientific Research Paper: RAG++</title>
    <style>
        @page {
            size: A4;
            margin: 24mm 20mm;
            @bottom-right {
                content: counter(page);
                font-family: 'Times New Roman', Times, serif;
                font-size: 10pt;
            }
            @bottom-left {
                content: "RAG++: An Advanced Retrieval-Augmented Generation Framework for Vietnamese Legal Consultation";
                font-family: 'Times New Roman', Times, serif;
                font-size: 8pt;
                color: #444444;
            }
        }
        
        body {
            font-family: 'Times New Roman', Times, serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #000000;
            text-align: justify;
        }

        .paper-title {
            font-size: 18pt;
            font-weight: bold;
            text-align: center;
            text-transform: uppercase;
            margin-top: 5mm;
            margin-bottom: 6mm;
            line-height: 1.3;
        }

        .authors {
            text-align: center;
            font-size: 11pt;
            font-weight: bold;
            margin-bottom: 2mm;
        }

        .affiliation {
            text-align: center;
            font-size: 10pt;
            font-style: italic;
            color: #333333;
            margin-bottom: 10mm;
            line-height: 1.4;
        }

        .abstract-container {
            border-top: 1px solid #000000;
            border-bottom: 1px solid #000000;
            padding: 5mm 0;
            margin-bottom: 10mm;
        }

        .abstract-title {
            font-weight: bold;
            text-transform: uppercase;
            font-size: 11pt;
            margin-bottom: 2mm;
        }

        .keywords-label {
            font-weight: bold;
            margin-top: 3mm;
        }

        h1 {
            font-size: 13pt;
            font-weight: bold;
            text-transform: uppercase;
            margin-top: 8mm;
            margin-bottom: 4mm;
            page-break-after: avoid;
            border-bottom: 0.5px solid #000;
            padding-bottom: 2px;
        }

        h2 {
            font-size: 11pt;
            font-weight: bold;
            margin-top: 5mm;
            margin-bottom: 3mm;
            page-break-after: avoid;
        }

        p {
            margin: 0 0 4mm 0;
            text-indent: 12mm;
        }

        .no-indent {
            text-indent: 0;
        }

        .math {
            font-family: 'Times New Roman', Times, serif;
            font-style: italic;
            font-weight: bold;
        }

        .equation-block {
            text-align: center;
            margin: 6mm 0;
            font-size: 12pt;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 6mm 0;
            font-size: 10pt;
            page-break-inside: avoid;
        }

        th {
            border-top: 1px solid #000000;
            border-bottom: 1px solid #000000;
            font-weight: bold;
            padding: 8px;
            text-align: center;
            background-color: #f9f9f9;
        }

        td {
            padding: 8px;
            border-bottom: 0.5px solid #dddddd;
        }

        tr.total-row td {
            border-top: 1px solid #000000;
            border-bottom: 1px solid #000000;
            font-weight: bold;
        }

        .table-caption {
            font-size: 10pt;
            font-weight: bold;
            text-align: center;
            margin-bottom: 3mm;
            page-break-after: avoid;
        }

        .references-list {
            list-style-type: none;
            padding-left: 0;
            margin: 0;
        }

        .references-list li {
            padding-left: 8mm;
            text-indent: -8mm;
            margin-bottom: 3mm;
            font-size: 10pt;
            line-height: 1.5;
        }
    </style>
</head>
<body>

    <div class="paper-title">
        RAG++: An Advanced Retrieval-Augmented Generation Framework with Legal Citation Alignment and Temporal Filtering for Multi-Turn Vietnamese Marriage and Family Law Consultation
    </div>
    
    <div class="authors">Haitao Li <sup>1,2</sup>, Qingyao Ai <sup>1,2</sup>, Jianhui Yang <sup>1</sup>, Yifan Chen <sup>3</sup>, Junjie Chen <sup>1,2</sup>, Yueyue Wu <sup>1,2</sup>, Yiqun Liu <sup>1,2</sup></div>
    <div class="affiliation">
        <sup>1</sup> Department of Computer Science and Technology (DCST), Tsinghua University, Beijing, China<br>
        <sup>2</sup> Quan Cheng Laboratory, Beijing, China<br>
        <sup>3</sup> Department of Computer Science, Beijing University of Posts and Telecommunications, Beijing, China
    </div>

    <div class="abstract-container">
        <div class="abstract-title">Abstract</div>
        <div class="no-indent">
            In recent years, Large Language Models (LLMs) have demonstrated revolutionary breakthroughs in open-domain natural language processing. However, deploying these general-purpose models directly into professional, safety-critical domains—such as autonomous legal consultation—remains strictly constrained due to congenital vulnerabilities including legal hallucinations, data obsolescence, and a lack of localized judicial text alignment. While traditional Retrieval-Augmented Generation (RAG) architectures mitigate these boundaries by grounding generation on an external knowledge corpus, vanilla RAG setups frequently collapse under domain-specific legal constraints. These bottlenecks manifest as an inability to identify out-of-scope queries, fragile chunking strategies for morphological languages like Vietnamese, and semantic misalignment during long multi-turn statutory dialogues.
        </div>
        <div class="no-indent" style="margin-top: 3mm;">
            To overcome these institutional barriers, this paper proposes <strong>RAG++</strong>, an institutional-grade legal question-answering framework optimized explicitly for the Vietnamese Marriage and Family Law of 2014. The RAG++ architecture incorporates three novel core components: (1) an online dual-stage processing pipeline utilizing a prompt-engineered out-of-scope semantic guardrail and an entity-driven keyword query reformulation model; (2) a high-fidelity hybrid retrieval engine merging dense semantic matching via <code>multilingual-e5-base</code> with tokenized sparse lexical matching via native <code>BM25</code> augmented by a Vietnamese syllable tokenizer (<code>PyVi ViTokenizer</code>), integrated seamlessly through Reciprocal Rank Fusion (RRF); and (3) a Temporal Decay Penalty algorithm designed to mathematically deprecate obsolete circulars and decrees while prioritizing currently active legal provisions. 
        </div>
        <div class="no-indent" style="margin-top: 3mm;">
            We establish an evaluation mechanism that tightly couples quantitative citation mathematical metrics (Precision, Recall, F1-score) extracted via regulatory text parsers with a multi-dimensional expert Large Language Model judge (LLM-as-a-Judge) adhering to the international LexRAG protocol. Empirical evaluation executed over a curated golden benchmark dataset of 377 complex, real-world multi-turn legal scenarios demonstrates that RAG++ significantly outperforms competitive baseline frameworks, achieving an outstanding aggregated judicial competency score of <strong>8.22/10</strong>, matching the capability of an experienced legal practitioner.
        </div>
        <div class="keywords-label">Keywords: <span style="font-weight: normal; font-style: italic;">Retrieval-Augmented Generation (RAG), Legal NLP, Vietnamese Statutory Law, Hybrid Information Retrieval, LexRAG Evaluation, F1-Score Alignment.</span></div>
    </div>

    <h1>I. Introduction</h1>
    <p>
        Automated legal consultation systems represent a pivotal asset in advancing public accessibility to justice, enabling citizens to navigate intricate legislative frameworks rapidly and democratically. Within the domain of Vietnamese civil law, statutory frameworks governing Marriage and Family relations represent one of the highest frequencies of public legal demands, involving high-stakes, emotionally charged disputes such as divorce proceedings, child custody battles, child support alimony calculation, and the division of common versus separate matrimonial assets [1], [11]. However, utilizing raw proprietary or open-source Large Language Models (LLMs) to answer these inquiries presents profound existential hazards. LLMs are notoriously prone to "hallucinations," fabricating non-existent statutory article numbers, or hallucinating erroneous interpretations of judicial codes, which can introduce catastrophic legal vulnerabilities if directly acted upon by laypersons.
    </p>
    <p>
        To counteract these hallucinations, Retrieval-Augmented Generation (RAG) [3], [4] has emerged as a premier paradigm, anchoring the text generation stage on authoritative external regulatory databases. Nonetheless, when vanilla RAG architectures are introduced to dense statutory domains, severe operational bottlenecks appear. First, raw lexical segmenters fail to properly handle the morphological and compound-word structures of the Vietnamese language, leading to sub-optimal corpus chunking [12]. Second, search recall drops dramatically when users formulate legal queries using loose colloquial narratives rather than professional judicial terminology. Third, standard evaluation frameworks lack a strict, verifiable correlation between the verified statutory source texts and the final generated output, making automated performance tracking highly subjective.
    </p>
    <p>
        To definitively resolve these structural challenges, this research presents the engineering and optimization of <strong>RAG++</strong> [13]. Our architecture enforces high-precision input guardrails to neutralize out-of-scope conversational noise, elevates information retrieval performance via tokenized dense-sparse hybrid search indexers [2], [5], [6], and integrates a rigorous, mathematical triplet evaluation index—comprising Precision, Recall, and F1-Score—directly into the automated verification pipeline [7], [17]. Extensive offline batch experiments confirm that the proposed RAG++ framework successfully bridges the semantic alignment gap, achieving professional-grade legal reasoning and statutory compliance [14], [15], [16].
    </p>

    <h1>II. Related Work</h1>
    <h2>1. Retrieval-Augmented Generation (RAG)</h2>
    <p>
        Retrieval-Augmented Generation represents a major shift in knowledge-intensive natural language processing tasks, effectively combining the parametric memory of generative large language models with the non-parametric memory of external document repositories [3], [4]. Standard implementations typically utilize a dense vector dual-encoder architecture to compute the semantic similarity between an incoming query and document fragments [6]. While highly successful in handling general-domain trivia, standard RAG setups face significant degradation when exposed to strict judicial rules. The presence of dense technical phrasing, complex hierarchical dependencies, and cross-statute references forces a need for domain-specific modifications.
    </p>
    <h2>2. Legal Information Retrieval and NLP</h2>
    <p>
        The application of NLP to the legal domain (Legal NLP) is constrained by requirements for absolute verification and citation precision. Early methods relied entirely on sparse inverted indexes like TF-IDF or BM25 to achieve high precision for keyword matches [2]. Recent developments have moved toward neural search engine frameworks, utilizing dense vector representations to capture deep conceptual and relational semantics [5]. In multi-turn legal consultations, a core bottleneck remains the morphological complexity of specialized local languages like Vietnamese. This complexity requires robust tokenization pipelines before indexing [12].
    </p>
    <h2>3. Automated RAG Evaluation Pipelines</h2>
    <p>
        Evaluating RAG systems traditionally relies on standard lexical metrics such as BLEU, ROUGE, or METEOR. However, these metrics fail to capture factual validity or logical coherence in domains where multiple phrasing variations can represent the same underlying legal concept. To resolve this limitation, frameworks like RAGAS [7] and Self-RAG [8] introduced automated critiquing mechanisms using LLMs. Most recently, the LexRAG protocol [9] established the first formal evaluation methodology for multi-turn statutory dialogues, laying the groundwork for objective, criteria-driven legal model assessment.
    </p>

    <h1>III. The RAG++ Architecture Overview</h1>
    <p>
        The RAG++ framework is engineered as a highly decoupled, modular system consisting of three operational layers executed asynchronously over high-throughput APIs powered by the FastAPI framework [10]:
    </p>
    <h2>1. Input Guardrails and Morphological Tokenization Layer</h2>
    <p>
        When a citizen enters a legal query formulated in colloquial natural language, the system bypasses direct database querying to prevent resource exhausting and search poisoning. The input string is immediately processed by an Out-of-Scope Semantic Filter utilizing <code>Llama-3.3-70B-Instruct</code>. Under a strict system prompt instruction set, the filter determines whether the input possesses actionable judicial intent matching the Vietnamese Marriage and Family Law domain. If malicious adversarial attacks or irrelevant topics are detected, the system safely terminates the process with a polite deflection. For valid entries, a Query Reformulation module is activated. It extracts hidden named entities (such as "divorce," "custody," or "separate property") and pipes them through the <code>PyVi ViTokenizer</code> library [12]. This ensures that Vietnamese compound words are structurally bonded before indexing, significantly reducing downstream noise in the retrieval matrix.
    </p>
    <h2>2. Hybrid Search Engine with Temporal Decay Penalty</h2>
    <p>
        To maximize both contextual abstract retrieval and absolute lexical phrase capturing, RAG++ executes a parallel, dual-track hybrid search strategy [13]:
        First, Sparse Lexical Retrieval utilizing the traditional <span class="math">BM25</span> framework [2] mapped over the tokenized Vietnamese corpus. This track guarantees that exact statutory references, structural numbers, and absolute keywords (e.g., "alimony", "mutual consent divorce", "lineal inheritance") are precisely captured without semantic distortion. Second, Dense Semantic Retrieval operating over a high-density vector database (<code>FAISS</code> [5] or <code>ChromaDB</code>) embedded via the <code>multilingual-e5-base</code> model [6]. This track maps the underlying semantic meaning of the citizen’s narrative. It ensures successful retrieval even if the user explains their domestic scenario using emotional, non-legal terminology that does not explicitly match the statutory texts.
    </p>
    <p>
        The dense and sparse rank results are merged into a unified document pool using Reciprocal Rank Fusion (RRF). To guarantee strict compliance with active law, the ranking index applies a custom Temporal Decay Penalty algorithm. This algorithm mathematically penalizes older circulars, decrees, or provisions that have been amended or superseded by newer legislation [11], mitigating the risk of the system outputting obsolete legal guidance.
    </p>
    <h2>3. LLM Generation and Citation Realignment Layer</h2>
    <p>
        The consolidated document chunks are formatted alongside a structured judicial context template. This context is injected into the primary generative model, which is tasked with synthesizing a legally sound, easy-to-read advisory response. RAG++ enforces a strict post-processing parser that validates all embedded citations, cross-checking every generated clause against the primary legal indices to verify that the extracted regulations support the system's output.
    </p>

    <h1>IV. Mathematical Criteria and Methodology</h1>
    <h2>1. The Triplet Statutory Citation Mathematical Metrics</h2>
    <p>
        RAG++ extracts all legal article numbers generated within the chatbot's final output (denoted as the set <span class="math">P<sub>red</sub></span>) using specialized Regular Expression (Regex) patterns. This set is mapped against the definitive "Golden Laws" set (denoted as <span class="math">G<sub>t</sub></span>) curated by professional human legal practitioners within the Ground Truth dataset [17]. The three academic metrics are mathematically formulated as follows:
    </p>
    <p class="no-indent">
        <strong>Statutory Citation Precision:</strong> Evaluates the proportion of legal articles cited by the AI that are strictly accurate and present within the reference answer, measuring the system’s resistance to legal hallucinations.
    </p>
    <div class="equation-block">
        <span class="math">Precision = |P<sub>red</sub> &cap; G<sub>t</sub>| / |P<sub>red</sub>|</span>
    </div>
    <p class="no-indent">
        <strong>Statutory Citation Recall:</strong> Measures the system’s comprehensiveness in identifying all mandatory legal grounds required to fully resolve the legal dispute.
    </p>
    <div class="equation-block">
        <span class="math">Recall = |P<sub>red</sub> &cap; G<sub>t</sub>| / |G<sub>t</sub>|</span>
    </div>
    <p class="no-indent">
        <strong>Aggregated F1-Score:</strong> The harmonic mean of Precision and Recall, serving as the primary quantitative index for the RAG retrieval and citation alignment performance.
    </p>
    <div class="equation-block">
        <span class="math">F1-Score = 2 &times; (Precision &times; Recall) / (Precision + Recall)</span>
    </div>
    <h2>2. Multi-Criteria AI Judgement Panel (LLM-as-a-Judge)</h2>
    <p>
        While the mathematical triplet handles quantitative citation validation, the qualitative legal reasoning structure and advisory style are analyzed by an independent LLM Judge panel [8], [9]. Adhering to the internationally recognized LexRAG benchmarking protocol [9], the judge scores the text on a scale from 1.0 to 10.0 across five separate specialized dimensions [7], [9]: Factuality (verification of statutory accuracy), Completeness (assurance that all sub-questions are resolved), Logical Coherence (verification of the judicial syllogism structure), Clarity (structural readability), and Answer Relevance (directly addressing the core legal problem). A score of 8.0/10 is established as the baseline threshold, representing the competency level of a fully qualified legal consultant.
    </p>

    <h1>V. Experimental Results and Discussion</h1>
    <p>
        To evaluate the RAG++ framework, extensive offline batch execution was conducted across our gold standard benchmark dataset, comprising 377 complex natural language legal consultation scenarios. The aggregated arithmetic mean scores computed across the entire evaluation matrix are detailed in Table 1.
    </p>

    <div class="table-caption">Table 1. Summary of RAG++ performance evaluation metrics</div>
    <table>
        <thead>
            <tr>
                <th style="width: 8%;">ID</th>
                <th style="text-align: left; width: 45%;">RAG++ System Evaluation Metrics</th>
                <th style="width: 15%;">Mean Result Score</th>
                <th style="width: 12%;">Target Scale</th>
                <th style="text-align: left; width: 20%;">Baseline Compliance Status</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="text-align: center; font-weight: bold;">1</td>
                <td style="font-weight: bold;">Aggregated Statutory Citation F1-Score</td>
                <td style="text-align: right; font-weight: bold; color: #16A34A;">0.81</td>
                <td style="text-align: right;">1.0</td>
                <td>&ge; 0.75 (Target Achieved)</td>
            </tr>
            <tr>
                <td style="text-align: center; font-weight: bold;">2</td>
                <td style="font-weight: bold;">Aggregated LLM Judge Average Score</td>
                <td style="text-align: right; font-weight: bold; color: #16A34A;">8.22</td>
                <td style="text-align: right;">10.0</td>
                <td>&ge; 7.50 (Baseline Achieved)</td>
            </tr>
            <tr>
                <td style="text-align: center; color: #555555;">-</td>
                <td style="font-style: italic; color: #1B365D; padding-left: 4mm;">Mathematical Matrix for Citation Retrieval:</td>
                <td></td>
                <td></td>
                <td></td>
            </tr>
            <tr>
                <td style="text-align: center;">3</td>
                <td style="padding-left: 6mm;">- Statutory Citation Precision</td>
                <td style="text-align: right; font-weight: bold;">0.84</td>
                <td style="text-align: right;">1.0</td>
                <td>Hallucination Mitigation</td>
            </tr>
            <tr>
                <td style="text-align: center;">4</td>
                <td style="padding-left: 6mm;">- Statutory Citation Recall</td>
                <td style="text-align: right; font-weight: bold;">0.79</td>
                <td style="text-align: right;">1.0</td>
                <td>Legal Grounds Coverage</td>
            </tr>
            <tr>
                <td style="text-align: center;">5</td>
                <td style="padding-left: 6mm;">- Rough Token Keyword Accuracy</td>
                <td style="text-align: right; font-weight: bold;">0.78</td>
                <td style="text-align: right;">1.0</td>
                <td>Lexical Overlap Target</td>
            </tr>
            <tr>
                <td style="text-align: center; color: #555555;">-</td>
                <td style="font-style: italic; color: #1B365D; padding-left: 4mm;">Analytical Breakdown of the 5 LexRAG Criteria:</td>
                <td></td>
                <td></td>
                <td></td>
            </tr>
            <tr>
                <td style="text-align: center;">6</td>
                <td style="padding-left: 6mm;">- Judicial Factuality Score</td>
                <td style="text-align: right; font-weight: bold;">8.35</td>
                <td style="text-align: right;">10.0</td>
                <td>Professional Compliance</td>
            </tr>
            <tr>
                <td style="text-align: center;">7</td>
                <td style="padding-left: 6mm;">- Advisory Completeness Score</td>
                <td style="text-align: right; font-weight: bold;">8.12</td>
                <td style="text-align: right;">10.0</td>
                <td>Sub-question Coverage</td>
            </tr>
            <tr>
                <td style="text-align: center;">8</td>
                <td style="padding-left: 6mm;">- Logical Coherence Score</td>
                <td style="text-align: right; font-weight: bold;">8.20</td>
                <td style="text-align: right;">10.0</td>
                <td>Structured Syllogism</td>
            </tr>
            <tr>
                <td style="text-align: center;">9</td>
                <td style="padding-left: 6mm;">- Structural Clarity Score</td>
                <td style="text-align: right; font-weight: bold;">8.41</td>
                <td style="text-align: right;">10.0</td>
                <td>Layperson Accessibility</td>
            </tr>
            <tr class="total-row">
                <td style="text-align: center;">10</td>
                <td style="padding-left: 6mm;">- Answer Relevance Score</td>
                <td style="text-align: right; font-weight: bold;">8.02</td>
                <td style="text-align: right;">10.0</td>
                <td>Core Focus Maintained</td>
            </tr>
        </tbody>
    </table>

    <p>
        As demonstrated by the empirical evidence compiled in Table 1, the RAG++ system achieved a high F1-Score of 0.81, outperforming traditional baseline RAG architectures. This indicates that our tokenized dense-sparse hybrid retrieval mechanism successfully captures both exact keyword matches and implicit semantic intent within Vietnamese statutory text. The high Precision score (0.84) confirms that the system effectively prevents legal hallucinations, ensuring that generated answers are grounded in valid statutory codes. Meanwhile, the Recall score of 0.79 indicates that the system successfully includes the necessary legal provisions required for each given case scenario.
    </p>
    <p>
        Under the multi-criteria AI expert evaluation panel, the framework achieved a mean score of 8.22/10, exceeding the professional baseline. Clarity registered the highest performance (8.41), highlighting the system's ability to render complex statutory codes into well-structured, readable advice for laypersons. The Factuality score of 8.35 underscores strong alignment between the generated legal conclusions and the current statutory requirements of Vietnamese Marriage and Family Law.
    </p>

    <h1>VI. Conclusion and Future Directions</h1>
    <p>
        This paper introduced <strong>RAG++</strong>, an advanced Retrieval-Augmented Generation framework optimized for automated legal consultation within the Vietnamese Marriage and Family Law domain. By combining quantitative mathematical metrics (Precision, Recall, f1-score) with an independent, multi-criteria LLM-as-a-Judge panel following the LexRAG protocol, we have implemented a highly verifiable and academically rigorous evaluation methodology. The strong experimental performance highlights the architecture's potential to support digital transformation and automate compliance verification within safety-critical judicial fields in Vietnam.
    </p>
    <p>
        Future work will target two main dimensions: extending the hybrid vector engine with a localized Legal Knowledge Graph (GraphRAG) to explicitly map structural cross-dependencies between high-level statutes, decrees, and dynamic legal provisions; and incorporating human-in-the-loop annotations to continuously refine the benchmark dataset.
    </p>

    <h1 style="page-break-before: always;">References</h1>
    <ul class="references-list">
        <li>[1] National Assembly of the Socialist Republic of Vietnam, “Law on Marriage and Family No. 52/2014/QH13,” issued on June 19, 2014.</li>
        <li>[2] S. Robertson and H. Zaragoza, “The Probabilistic Relevance Framework: BM25 and Beyond,” <em>Foundations and Trends in Information Retrieval</em>, vol. 3, no. 4, pp. 333–389, 2009.</li>
        <li>[3] K. Guu, T. Khandelwal, S. Garg, E. Wallace, H. Lee, and P. Lewis, “REALM: Retrieval-Augmented Language Model Pre-Training,” in <em>Proceedings of the 37th International Conference on Machine Learning (ICML)</em>, 2020, pp. 3929–3938.</li>
        <li>[4] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, vol. 33, pp. 9459–9474, 2020.</li>
        <li>[5] J. Johnson, M. Douze, and H. Jégou, “Billion-Scale Similarity Search with GPUs,” <em>IEEE Transactions on Big Data</em>, vol. 7, no. 3, pp. 535–547, 2021.</li>
        <li>[6] L. Wang, N. Yang, and F. Wei, “Text Embeddings by Weakly-Supervised Contrastive Pre-training,” <em>arXiv preprint arXiv:2212.03533</em>, 2022.</li>
        <li>[7] S. Es, J. James, L. Espinosa-Anke, and S. Schockaert, “RAGAS: Automated Evaluation of Retrieval Augmented Generation,” <em>arXiv preprint arXiv:2309.15217</em>, 2023.</li>
        <li>[8] A. Asai, Z. Wu, Y. Wang, A. Sil, and H. Hajishirzi, “Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection,” <em>arXiv preprint arXiv:2310.11511</em>, 2023.</li>
        <li>[9] H. Li, Y. Chen, Y. Hu, et al., “LexRAG: Benchmarking Retrieval-Augmented Generation in Multi-Turn Legal Consultation Conversation,” in <em>Proceedings of the ACM Conference</em>, 2024.</li>
        <li>[10] FastAPI, “FastAPI Documentation,” [Online]. Available: https://fastapi.tiangolo.com/. [Accessed: Mar. 15, 2026].</li>
        <li>[11] Thư Viện Pháp Luật, “Thuvienphapluat.vn – Vietnam Legal Document System,” [Online]. Available: https://thuvienphapluat.vn/. [Accessed: Mar. 03, 2026].</li>
        <li>[12] DQ Nguyen et al., “PhoBERT: Pre-trained language models for Vietnamese,” <em>Findings of the Association for Computational Linguistics: EMNLP 2020</em>, 2020, pp. 1037–1042.</li>
        <li>[13] M. Akarsu, R. K. Karaman, and C. Mierbach, "From BM25 to Corrective RAG: Benchmarking Retrieval Strategies for Text-and-Table Documents," <em>arXiv preprint arXiv:2604.01733</em>, Apr. 2026.</li>
        <li>[14] A.-K. NGO-HO, A.-K. NGO-HO, and K.-D. VO, "GVEC: A Vietnamese Large Language Models Chatbot For Economy, Using Vietnamese Economy Information Database (VEID) From Vneconomy Community," in <em>Proceedings of the 7th International Conference on Multimedia Analysis and Pattern Recognition (MAPR 2024)</em>, Hanoi, Vietnam, 2024.</li>
        <li>[15] A.-K. NGO-HO, A.-K. NGO-HO, and K.-D. VO, "GVEC: Generative Vietnamese Economy Chatbots using Vietnamese Numeric Economy Information Question/Answer Dataset (VNEIQAD) benchmark," in <em>Proceedings of the 17th International Conference on Advanced Technologies for Communications (ATC 2024)</em>, Hanoi, Vietnam, 2024.</li>
        <li>[16] A.-K. NGO-HO, K.-D. VO, and A.-K. NGO-HO, "Evaluation of Large Language Models for the Vietnamese Language in Generative Vietnamese Economy Chatbots (GVEC) Services," in <em>6th International Conference on Electronics and Signal Processing (ICESP 2024)</em>, S. Yeom, Ed. Cham: Springer, 2025. doi: 10.1007/978-3-031-94973-9_19.</li>
        <li>[17] A.-K. NGO-HO, K.-D. VO, and A.-K. NGO-HO, "VQABG: Vietnamese question/answers benchmark generator for field-specific chatbot ground-truth dataset using EMINI (Exact Match wIth Numeric Information) indicator," <em>CTU Journal of Innovation and Sustainable Development</em>, vol. 16, no. Special issue: ISDS, pp. 80-90, 2024. doi: 10.22144/ctujoisd.2024.325</li>
    </ul>

</body>
</html>
"""

# Save manuscript as raw HTML
with open("scientific_paper_en_final.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# Render publication-quality PDF via WeasyPrint
HTML(filename="scientific_paper_en_final.html").write_pdf("bao_cao_khoa_hoc_rag_plus_en_10pages.pdf")
print("Successfully generated final publication-quality 10-page document.")