import numpy as np


def euclidean(sources, destinations):
    """
    Calculate the Euclidean distance matrix between source and destination points.

    Parameters
    ----------
    sources : np.ndarray
        Array of shape (n, d) containing the source points.
    destinations : np.ndarray
        Array of shape (m, d) containing the destination points.

    Returns
    -------
    np.ndarray
        Euclidean distance matrix of shape (n, m).
    """
    # Expand dimensions to enable broadcasting
    sources_expanded = sources[:, np.newaxis, :]
    destinations_expanded = destinations[np.newaxis, :, :]

    # Compute differences along the last dimension
    differences = sources_expanded - destinations_expanded

    # Compute Euclidean distances using norm along the last dimension
    return np.linalg.norm(differences, axis=2)
