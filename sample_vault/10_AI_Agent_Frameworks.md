---
title: AI Agent Frameworks
tags: [agents, tool-use, autonomous-systems]
status: active
date: 2026-08-24
author: Autonomous Systems Lead
---

# AI Agent Frameworks

AI Agents extend [[05_Large_Language_Models|Large Language Models]] beyond static text generation by equipping them with tools, execution loops, and external memory.

## Core Agentic Loop

1. **Plan**: Decompose user goals into sequential actions.
2. **Act**: Invoke tools (e.g., code execution, web search, vector retrieval).
3. **Observe**: Evaluate tool execution feedback.
4. **Reflect**: Adjust execution trajectory dynamically.

Agentic systems leverage [[06_Retrieval_Augmented_Generation|RAG pipelines]] as long-term memory sources to preserve contextual factual state across tasks.

#agents #tools #autonomy #ai
