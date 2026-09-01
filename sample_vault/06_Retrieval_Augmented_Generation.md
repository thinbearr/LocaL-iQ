---
title: Retrieval Augmented Generation
tags: [rag, retrieval, llm, architecture]
status: active
date: 2026-08-20
author: RAG Architect
---

# Retrieval Augmented Generation

Retrieval-Augmented Generation (RAG) is an architectural framework that enhances [[05_Large_Language_Models|Large Language Models]] by retrieving relevant factual passages from external reference databases before generating responses.

## Standard Vector RAG Pipeline

A standard naive RAG system operates in three distinct phases:

1. **Ingestion & Indexing**: Documents are split into chunks, converted into dense vectors using [[12_Semantic_Search_and_Embeddings|Embedding Models]], and stored in [[07_Vector_Databases|Vector Databases]].
2. **Retrieval**: At query time, the user's question is embedded, and a top-k cosine similarity search pulls the most semantically similar passages.
3. **Generation**: The retrieved passages are formatted into a prompt context, guiding the LLM to generate a grounded answer with citations.

## Limitations of Naive Flat RAG

Flat vector search treats document corpora as isolated, unstructured fragments of text. In structured environments—such as an [[11_Obsidian_Knowledge_Management|Obsidian Vault]] with rich wikilinks—flat vector search completely misses document relationships, backlinks, and navigational context.

## Next-Generation Graph RAG

To overcome flat vector RAG limitations, [[08_Graph_RAG_and_Knowledge_Graphs|Graph RAG]] incorporates explicit graph topology. By utilizing note wikilinks and backlinks, retrieval algorithms can expand candidate search space across linked neighbor notes.

For complete RAG system design patterns, see [[14_MOC_RAG_Architectures|RAG Architectures Map of Content]].

#rag #retrieval #search #ai-architecture
