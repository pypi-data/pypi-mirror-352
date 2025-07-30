# nm
SOM utils

To install:	```pip install nm```

## Overview
The `nm` package provides a Python implementation of Self-Organizing Maps (SOMs), a type of unsupervised learning neural network that is used to produce a low-dimensional (typically two-dimensional), discretized representation of the input space of the training samples. This implementation includes various functionalities such as data normalization, initialization methods, training processes, and visualization tools.

## Main Features
- **Normalization**: Support for data normalization which is crucial for effective SOM training.
- **Initialization Methods**: Includes PCA-based and random initialization to start the SOM training.
- **Training**: Supports both batch and sequential training methods.
- **Visualization**: Functions to visualize the SOM's codebooks and the mapping from data space to SOM space.
- **Projection**: Ability to project new data onto the trained SOM.
- **Clustering**: Utilize the trained SOM for clustering data.
- **Utility Functions**: Additional functions for data denormalization, finding k-nearest nodes, etc.

## Usage

### Initialization
To create a SOM instance:
```python
from nm import SOM
som = SOM(name="My_SOM", Data=my_data, mapsize=[20, 30], norm_method='var', initmethod='pca', neigh='Gaussian')
```

### Training
To train the SOM:
```python
som.train(n_job=1, shared_memory='no', verbose='on')
```

### Visualization
To visualize the trained SOM:
```python
som.view_map(what='codebook', which_dim='all', pack='Yes', text_size=10, save='No', grid='Yes', text='Yes')
```

### Project Data
To project new data onto the trained SOM and find the best matching units (BMUs):
```python
new_data_projection = som.project_data(new_data)
```

### Clustering
To perform clustering on the map nodes:
```python
cluster_labels = som.cluster(method='Kmeans', n_clusters=8)
```

### Prediction
To predict using the trained SOM:
```python
predicted_values = som.predict(X_test)
```

## Documentation
Each function in the SOM class is well documented with docstrings, providing details on the parameters, the expected inputs, and outputs. Users are encouraged to refer to these docstrings for more detailed usage instructions.

## Installation
This package can be installed using pip:
```bash
pip install nm
```

## Requirements
This package depends on several external libraries including:
- NumPy
- Matplotlib
- Scikit-learn
- Joblib
- NumExpr
- SciPy

Ensure these are installed in your Python environment to use `nm` package effectively.