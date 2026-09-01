---
title: Transformer Architecture
tags: [transformers, attention, nlp, architecture]
status: active
date: 2026-08-18
author: NLP Researcher
---

# Transformer Architecture

Introduced in the landmark 2017 paper *"Attention Is All You Need"* by Vaswani et al., the Transformer architecture discarded recurrent sequential processing in favor of parallelizable self-attention mechanisms.

## Core Components

### Scaled Dot-Product Self-Attention
Self-attention allows the model to weigh the relative importance of every token against every other token in a sequence, computed as:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

Where:
- $Q$: Query matrix
- $K$: Key matrix
- $V$: Value matrix
- $d_k$: Scaling dimension factor

### Multi-Head Attention (MHA)
Instead of computing single attention once, Multi-Head Attention projects Queries, Keys, and Values into multiple lower-dimensional subspaces, enabling the network to jointly attend to information from different representation subspaces.

### Positional Encoding
Because self-attention is permutation-invariant, explicit positional encodings (sinusoidal or rotary embeddings RoPE) are added to input token embeddings to communicate sequence order.

## Impact on Foundation Models

Transformers revolutionized natural language processing, serving as the foundational architectural blueprint for decoder-only [[05_Large_Language_Models|Large Language Models]] (such as GPT-4 and Llama 3) and encoder-based embedding models used in [[12_Semantic_Search_and_Embeddings|Semantic Search]].

For architecture maps, see [[14_MOC_RAG_Architectures|RAG & Architecture Map of Content]].

#transformers #attention #nlp #deep-learning
