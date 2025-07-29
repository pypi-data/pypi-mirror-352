"""
Initialization utilities for LMGEC clustering.

This module provides functions to initialize cluster assignments,
centroids, and view-specific projection matrices required by the
LMGEC algorithm.

Functions:
- init_G_F: initialize cluster labels and centroids using KMeans.
- init_W: initialize projection matrix via truncated SVD.
"""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD


def init_G_F(
    XW: np.ndarray,
    k: int,
) -> tuple:
    """
    Initialize cluster assignments G and centroids F using KMeans.

    :param XW: Array [n_samples, embedding_dim], data to cluster.
    :param k: Number of clusters.
    :returns: Tuple (G, F) where:
        - G: 1D array of length n_samples, initial cluster labels.
        - F: 2D array [k, embedding_dim], initial cluster centroids.
    :rtype: (np.ndarray, np.ndarray)
    """
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(XW)
    return kmeans.labels_, kmeans.cluster_centers_


def init_W(
    X: np.ndarray,
    f: int,
) -> np.ndarray:
    """
    Initialize projection matrix W using truncated SVD.

    :param X: Array [n_samples, n_features], input data matrix.
    :param f: Target embedding dimension.
    :returns: Projection matrix [n_features, f].
    :rtype: np.ndarray
    """
    svd = TruncatedSVD(n_components=f)
    svd.fit(X)
    # TruncatedSVD.components_ has shape [f, n_features]
    # Transpose to [n_features, f]
    return svd.components_.T
