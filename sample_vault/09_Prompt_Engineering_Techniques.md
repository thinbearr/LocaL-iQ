---
title: Prompt Engineering Techniques
tags: [prompt-engineering, llm, system-prompts]
status: active
date: 2026-08-23
author: Prompt Engineer
---

# Prompt Engineering Techniques

Prompt Engineering is the practice of structuring text inputs to optimize the output of [[05_Large_Language_Models|Large Language Models]].

## Key Methods

### Few-Shot Prompting
Providing clear input-output demonstrations within the prompt context before requesting generation on a target task.

### Chain-of-Thought (CoT)
Encouraging the LLM to generate step-by-step reasoning steps before rendering its final answer.

### Citation Grounding (RAG Prompts)
Instructing the model to answer strictly based on retrieved context chunks and explicitly cite source notes using `[Note Title#Section]` markup.

```text
System Prompt Pattern:
You are an intelligent knowledge assistant. Answer the user question using ONLY the provided vault context chunks.
If the context does not contain sufficient information, state "No relevant information found."
Do NOT fabricate claims.
```

Prompt engineering is crucial for building robust [[15_Evaluation_and_Hallucination_Guardrails|Hallucination Guardrails]].

#prompt-engineering #cot #grounding #system-prompts
