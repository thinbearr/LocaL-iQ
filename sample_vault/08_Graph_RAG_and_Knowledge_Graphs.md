---
title: Graph RAG and Knowledge Graphs
tags: [graph-rag, knowledge-graph, networkx, retrieval]
status: active
date: 2026-08-22
author: Graph AI Researcher
---

# Graph RAG and Knowledge Graphs

Graph RAG combines vector-based similarity search with explicit knowledge graph relationships. In an [[11_Obsidian_Knowledge_Management|Obsidian Vault]], notes represent graph nodes, while `[[wikilinks]]` and backlinks represent directed edges.

## Graph-Guided Candidate Expansion

Unlike flat vector retrieval (which queries only global [[07_Vector_Databases|Vector DBs]]), Graph RAG uses a two-phase retrieval process:

1. **Seed Retrieval**: Vector search identifies initial top-k matching seed chunks.
2. **Graph Expansion**: The system extracts 1-hop outgoing links and backlinks connected to the seed notes.
3. **Restricted Semantic Search**: A second vector search is executed specifically over chunks belonging to those candidate neighbor notes.
4. **Relevance Rescoring**: Only neighbor chunks clearing relevance score thresholds are admitted into context.

## Hub Note Capping Strategy

Notes like Maps of Content (MOCs)—such as [[13_MOC_Artificial_Intelligence]] or [[14_MOC_RAG_Architectures]]—contain high link degrees ($>10$ links). Indiscriminate expansion from hub notes floods the context with loosely related topics.

To mitigate this, Graph RAG applies:
- **Neighbor caps**: Restricting neighbor expansion to a maximum limit (e.g., 5-8 notes per seed).
- **Hub guards**: Excluding notes exceeding a maximum degree threshold from automatic full candidate expansion.

Graph-guided search significantly improves context recall while maintaining strict precision.

#graph-rag #knowledge-graph #wikilinks #backlinks #networkx
