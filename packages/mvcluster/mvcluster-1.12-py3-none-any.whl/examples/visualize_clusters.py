"""
Example script to run clustering using the LMGEC model on a built-in dataset,
and to visualize the predicted and ground truth clusters.

This example uses one of the available datasets, preprocesses the data,
computes the LMGEC clustering, and visualizes the results
in 2D using PCA projection.

To run this script:

    python visualize_clusters.py

Note:
    This script must be located in the `examples/` directory.
"""

import os
import sys
import numpy as np
from sklearn.preprocessing import StandardScaler

# Add the parent directory to the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mvcluster.cluster import LMGEC  # noqa: E402
from mvcluster.utils.plot import visualize_clusters  # noqa: E402
from mvcluster.utils.datagen import datagen  # noqa: E402
from mvcluster.utils.preprocess import preprocess_dataset  # noqa: E402


def main():
    """
    Main function to execute the clustering and visualization pipeline.

    Steps:
        1. Load dataset using `datagen`.
        2. Preprocess each view with adjacency normalization and TF-IDF.
        3. Construct embeddings.
        4. Apply LMGEC clustering.
        5. Visualize predicted vs. ground truth clusters.
    """
    # Configuration parameters
    dataset_name = "acm"  # Choose from: "acm", "dblp", "imdb", "photos"
    temperature = 1.0
    beta = 1.0
    max_iter = 10
    tolerance = 1e-7

    # Load and preprocess the dataset
    As, Xs, labels = datagen(dataset_name)
    k = len(np.unique(labels))
    views = list(zip(As, Xs))

    processed_views = []
    for A, X in views:
        use_tfidf = dataset_name in ["acm", "dblp", "imdb", "photos"]
        norm_adj, feats = preprocess_dataset(
            A, X, tf_idf=use_tfidf, beta=int(beta)
        )
        if hasattr(feats, "toarray"):
            feats = feats.toarray()
        processed_views.append((np.asarray(norm_adj), feats))

    # Compute embeddings for each view
    Hs = [
        StandardScaler(with_std=False).fit_transform(S @ X)
        for S, X in processed_views
    ]

    # Run clustering
    model = LMGEC(
        n_clusters=k,
        embedding_dim=k + 1,
        temperature=temperature,
        max_iter=max_iter,
        tolerance=tolerance,
    )
    pred_labels = model.fit_predict(Hs)  # type: ignore

    # Visualize results
    X_concat = np.hstack([X for _, X in processed_views])
    visualize_clusters(
        X_concat, pred_labels, method='pca', title='Clusters prédits (LMGEC)'
    )
    visualize_clusters(
        X_concat, labels, method='pca', title='Clusters réels (Ground Truth)'
    )


if __name__ == "__main__":
    main()
