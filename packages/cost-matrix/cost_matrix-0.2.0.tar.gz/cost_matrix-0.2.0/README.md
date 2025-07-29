# cost-matrix

`cost-matrix` is a Python package designed to simplify the creation of cost matrices for optimization problems. Whether you're dealing with distance calculations or travel durations, `cost-matrix` provides a robust set of tools to meet your needs.

This package is invaluable for anyone working on optimization problems, data analysis, or transportation planning. With its diverse range of distance calculation methods and integration with OSRM, it provides a comprehensive solution for generating cost matrices efficiently.

## Key Features:
- **Manhattan**: Compute distances based on orthogonal paths.
- **Euclidean**: Calculate straight-line distances in a Cartesian plane.
- **Spherical**: Calculate distances between geographical points considering the Earth's curvature.
- **OSRM**: Integrate with the Open Source Routing Machine (OSRM) to obtain travel duration or distance matrices.

## Installation

To install the `cost-matrix` package, you can use pip:

```sh
pip install cost-matrix
```


## Example Usage:
```python
import numpy as np
import cost_matrix

# Define source and destination coordinates (latitude, longitude)
sources = np.array([[37.7749, -122.4194], [34.0522, -118.2437]])  # San Francisco, Los Angeles
destinations = np.array([[40.7128, -74.0060], [51.5074, -0.1278]])  # New York, London

# Calculate Manhattan distance matrix
manhattan_matrix = cost_matrix.manhattan(sources, destinations)
print(manhattan_matrix)

# Calculate Euclidean distance matrix
euclidean_matrix = cost_matrix.euclidean(sources, destinations)
print(euclidean_matrix)

# Calculate Spherical distance matrix
spherical_matrix = cost_matrix.spherical(sources, destinations)
print(spherical_matrix)

# Calculate OSRM travel distances matrix
osrm_distance_matrix = cost_matrix.osrm(sources, destinations)
print(osrm_distance_matrix)

# Calculate OSRM travel durations matrix
osrm_duration_matrix = cost_matrix.osrm(
    sources, 
    destinations, 
    cost_type="durations", 
    server_address="http://localhost:5000",
    batch_size=250
)
print(osrm_duration_matrix)
```

## GitHub
* [Repository](https://github.com/luanleonardo/cost-matrix)
