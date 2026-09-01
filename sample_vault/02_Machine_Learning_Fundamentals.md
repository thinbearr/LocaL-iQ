---
title: Machine Learning Fundamentals
tags: [ml, machine-learning, algorithms]
status: active
date: 2026-08-16
author: Data Scientist
---

# Machine Learning Fundamentals

Machine Learning (ML) is the subfield of [[01_Artificial_Intelligence_Overview|Artificial Intelligence]] that focuses on developing algorithms that improve automatically through experience and data analysis.

## Learning Paradigms

ML is traditionally divided into three primary paradigms:

### Supervised Learning
Models are trained on labeled datasets containing input-output pairs $(X, y)$. Common tasks include:
- **Classification**: Predicting categorical labels (e.g., spam detection).
- **Regression**: Predicting continuous values (e.g., house price forecasting).

### Unsupervised Learning
Models extract hidden patterns or structures from unlabeled data $X$. Key applications include:
- **Clustering**: Grouping similar instances (e.g., K-Means).
- **Dimensionality Reduction**: Compressing feature spaces while preserving variance (e.g., PCA, UMAP).

### Reinforcement Learning
Agents learn optimal decision-making policies by interacting with an environment to maximize cumulative reward signals.

## Mathematical Foundations

ML models heavily rely on mathematical concepts:
- **Linear Algebra**: Matrix operations and vector representations.
- **Optimization**: Gradient Descent and Stochastic Gradient Descent (SGD) for parameter tuning.
- **Representation**: Converting high-dimensional data into dense vector representations. See [[12_Semantic_Search_and_Embeddings#Vector Embeddings|Vector Embeddings Section]].

## Transition to Deep Learning

When dataset scale and model complexity grow significantly, traditional ML algorithms (such as Decision Trees or SVMs) often hit a performance plateau. This prompted the development of [[03_Deep_Learning_and_Neural_Networks|Deep Learning architectures]].

#ml #algorithms #supervised #unsupervised
