"""
LMGEC clustering model implementation.

This module provides the LMGEC class, which implements the Localized
Multi-Graph Embedding Clustering (LMGEC) algorithm. It extends
scikit-learn's BaseEstimator and ClusterMixin interfaces, offering
fit, predict, and transform methods for clustering across multiple views.
"""

import numpy as np
from sklearn.base import BaseEstimator, ClusterMixin

from ..utils.init_utils import init_G_F, init_W  # type: ignore
from ..models.lmgec_core import train_loop      # type: ignore


class LMGEC(BaseEstimator, ClusterMixin):
    """
    Localized Multi-Graph Embedding Clustering (LMGEC) model.

    :param int n_clusters: Number of clusters to form.
    :param int embedding_dim: Dimension of embedding space.
    :param float temperature: Temperature for view weighting.
    :param int max_iter: Max training iterations.
    :param float tolerance: Convergence threshold.
    """

    def __init__(
        self,
        n_clusters: int = 3,
        embedding_dim: int = 10,
        temperature: float = 0.5,
        max_iter: int = 30,
        tolerance: float = 1e-6,
    ):
        self.n_clusters = n_clusters
        self.embedding_dim = embedding_dim
        self.temperature = temperature
        self.max_iter = max_iter
        self.tolerance = tolerance

    def fit(self, X_views, y=None):  # noqa: D102
        """
        Fit the LMGEC model to multiple data views.

        :param list X_views: List of feature matrices per view.
        :param y: Ignored, for API consistency.
        :returns: Fitted estimator.
        :rtype: self
        """
        n_views = len(X_views)
        alphas = np.zeros(n_views)
        XW_consensus = 0

        for v, Xv in enumerate(X_views):
            Wv = init_W(Xv, self.embedding_dim)
            XWv = Xv @ Wv
            Gv, Fv = init_G_F(XWv, self.n_clusters)
            inertia = np.linalg.norm(XWv - Fv[Gv])
            alphas[v] = np.exp(-inertia / self.temperature)
            XW_consensus += alphas[v] * XWv

        XW_consensus /= alphas.sum()
        G, F = init_G_F(XW_consensus, self.n_clusters)

        G, F, XW_final, losses = train_loop(
            X_views,
            F,  # type: ignore
            G,  # type: ignore
            alphas,  # type: ignore
            self.n_clusters,
            self.max_iter,
            self.tolerance,
        )

        self.labels_ = G.numpy() if hasattr(G, "numpy") else G
        self.F_ = F
        self.XW_ = XW_final
        self.loss_history_ = losses

        return self

    def predict(self, X_views):  # noqa: D102
        """
        Predict cluster labels for input views after fitting.

        :param list X_views: List of feature matrices (ignored).
        :returns: Cluster labels from fit.
        :rtype: array-like
        """
        return self.labels_

    def transform(self, X_views):  # noqa: D102
        """
        Transform input views into the final embedding space.

        :param list X_views: List of feature matrices (ignored).
        :returns: Consensus embedding from fit.
        :rtype: array-like
        """
        return self.XW_
