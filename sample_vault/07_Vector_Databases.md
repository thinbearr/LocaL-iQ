---
title: Vector Databases
tags: [vector-db, chromadb, embeddings, search]
status: active
date: 2026-08-21
author: Infrastructure Engineer
---

# Vector Databases

Vector Databases are specialized data stores engineered to store, index, and query high-dimensional vector embeddings efficiently at scale.

## Indexing Algorithms

Traditional relational databases query data using B-Trees or Hash Indexes. Vector databases utilize Approximate Nearest Neighbor (ANN) search algorithms to handle vector spaces with hundreds or thousands of dimensions:

- **HNSW (Hierarchical Navigable Small World)**: Graph-based index structure offering fast query throughput.
- **IVF (Inverted File Index)**: Partitions vector space into Voronoi cells to accelerate search speed.

## ChromaDB in Zero-Cost Stacks

For local, zero-cost developer environments, **ChromaDB** is a lightweight, open-source vector store. It integrates directly with local Python embedding models (like `all-MiniLM-L6-v2`) and provides metadata filtering.

```python
import chromadb

# Initialize local persistent client
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("obsidian_vault")
```

Vector databases form the indexing backbone of [[06_Retrieval_Augmented_Generation|Retrieval-Augmented Generation]], working alongside [[12_Semantic_Search_and_Embeddings|Semantic Search algorithms]].

#vector-db #chromadb #indexing #hnsw #embeddings
