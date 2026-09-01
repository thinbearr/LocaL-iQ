---
title: Semantic Search and Embeddings
tags: [embeddings, semantic-search, sentence-transformers, cosine-similarity]
status: active
date: 2026-08-26
author: AI Research Engineer
---

# Semantic Search and Embeddings

Semantic search matches query intent and context rather than relying on exact keyword matching.

## Vector Embeddings

Dense vector embeddings map text fragments into a continuous high-dimensional vector space where semantically related concepts reside close together.

### Local CPU Embedding Models
In zero-cost architectures, lightweight models such as `all-MiniLM-L6-v2` or `bge-small-en` run locally on CPU using `sentence-transformers`:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(["Retrieval Augmented Generation", "Obsidian Vault RAG"])
```

## Distance Metrics

Semantic similarity is evaluated using metric distances:
- **Cosine Similarity**: Measures the cosine of the angle between two vectors ($\cos(\theta) = \frac{A \cdot B}{\|A\| \|B\|}$).
- **Euclidean Distance (L2)**: Measures straight-line distance between vector points.

Semantic embeddings are indexed inside [[07_Vector_Databases|Vector Databases]] to power global retrieval in [[06_Retrieval_Augmented_Generation|RAG Pipelines]].

#embeddings #semantic-search #vector-space #cosine-similarity
