import numpy as np

EARTH_RADIUS_METERS = 6371000


def spherical(sources: np.ndarray, destinations: np.ndarray) -> np.ndarray:
    """
    Compute the distance matrix using the Spherical distance]

    Parameters
    ----------
    sources : np.ndarray
        Array of shape (n, d) containing the source points.
    destinations : np.ndarray
        Array of shape (m, d) containing the destination points.

    Returns
    -------
    np.ndarray
        Spherical distance matrix of shape (n, m).
    """

    sources_rad = np.radians(sources)
    destinations_rad = np.radians(destinations)

    delta_lambda = sources_rad[:, [1]] - destinations_rad[:, 1]  # (N x M) lng
    phi1 = sources_rad[:, [0]]  # (N x 1) array of source latitudes
    phi2 = destinations_rad[:, 0]  # (1 x M) array of destination latitudes

    delta_sigma = np.arctan2(
        np.sqrt(
            (np.cos(phi2) * np.sin(delta_lambda)) ** 2
            + (
                np.cos(phi1) * np.sin(phi2)
                - np.sin(phi1) * np.cos(phi2) * np.cos(delta_lambda)
            )
            ** 2
        ),
        (
            np.sin(phi1) * np.sin(phi2)
            + np.cos(phi1) * np.cos(phi2) * np.cos(delta_lambda)
        ),
    )

    return EARTH_RADIUS_METERS * delta_sigma
