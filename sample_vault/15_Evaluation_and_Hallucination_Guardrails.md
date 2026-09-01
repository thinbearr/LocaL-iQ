---
title: Evaluation and Hallucination Guardrails
tags: [evaluation, guardrails, anti-hallucination, metrics]
status: active
date: 2026-08-29
author: AI Safety Lead
---

# Evaluation and Hallucination Guardrails

Production RAG systems require continuous quality assurance to prevent hallucinated statements and enforce grounding against source documents.

## Hallucination Prevention Strategies

### Minimum Similarity Threshold Guardrail
Before invoking an LLM, the retrieval engine calculates the maximum similarity score among retrieved context chunks. If no chunk clears the threshold (e.g., score $< 0.30$), the system immediately short-circuits with a rule-based response:

> *"No relevant information found in the vault."*

This completely prevents calling the LLM when no relevant knowledge exists, eliminating hallucination opportunities.

### Strict Citation Verification
Generative answers must link every factual assertion to a specific cited source note (`[[Note Title]]`). Any ungrounded claim is flagged as unverified context.

## Benchmarking RAG Quality

Standard metrics used to evaluate RAG systems:
- **Context Precision**: Ratio of retrieved chunks that are actually relevant.
- **Context Recall**: Percentage of relevant source information retrieved.
- **Faithfulness**: Absence of fabricated claims unbacked by context chunks.

Evaluating RAG performance against [[08_Graph_RAG_and_Knowledge_Graphs|Graph RAG]] vs [[06_Retrieval_Augmented_Generation|Flat Vector RAG]] demonstrates significant precision improvements when using graph candidate expansion.

#evaluation #guardrails #anti-hallucination #metrics
