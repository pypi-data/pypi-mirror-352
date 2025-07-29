import numpy as np


def manhattan(sources: np.ndarray, destinations: np.ndarray) -> np.ndarray:
    """
    Compute the Manhattan distance matrix between source and destination points.

    Parameters
    ----------
    sources : np.ndarray
        Array of shape (n, d) containing the source points.
    destinations : np.ndarray
        Array of shape (m, d) containing the destination points.

    Returns
    -------
    np.ndarray
        Manhattan distance matrix of shape (n, m).
    """
    # Expand dimensions to enable broadcasting
    sources_expanded = sources[:, np.newaxis, :]
    destinations_expanded = destinations[np.newaxis, :, :]

    # Compute absolute differences along the last dimension
    differences = np.abs(sources_expanded - destinations_expanded)

    # Sum absolute differences along the last dimension to get
    # Manhattan distance
    return np.sum(differences, axis=2)
