# ge
Utils for training models

To install:	```pip install ge```

## Overview
The `ge` package provides utility functions for evaluating and constructing formulas for fitted models, particularly useful in the context of machine learning and data analysis. The main functionalities include calculating normalized root mean square error (NRMSE), cross-validated root mean square error (CV RMSE), and generating a string representation of a model's formula with fitted parameters.

## Functions

### nrmse
Calculates the normalized root mean square error between predicted and actual data. This is used to measure the accuracy of a model, normalized by the range of the data.

**Usage:**
```python
from ge import nrmse
actual_data = [1, 2, 3, 4, 5]
predicted_data = [1.1, 1.9, 3.0, 3.9, 5.1]
error = nrmse(actual_data, predicted_data)
print("NRMSE:", error)
```

### cv_rmse
Calculates the cross-validated root mean square error between predicted and actual data, normalized by the mean of the actual data. This provides a scale-independent measure of prediction error, useful for comparing models across different datasets.

**Usage:**
```python
from ge import cv_rmse
actual_data = [1, 2, 3, 4, 5]
predicted_data = [1.1, 1.9, 3.0, 3.9, 5.1]
error = cv_rmse(actual_data, predicted_data)
print("CV RMSE:", error)
```

### formula_str
Generates a string representation of a fit function's formula with parameters injected. This is particularly useful for documenting and sharing the exact mathematical formula used in model fitting.

**Usage:**
```python
from ge import formula_str
from scipy.optimize import curve_fit

# Define a model function
def model_func(x, a, b):
    return a + b * x

# Example data
xdata = [0, 1, 2, 3, 4]
ydata = [0, 2, 4, 6, 8]

# Fit the model to the data
params, _ = curve_fit(model_func, xdata, ydata)

# Generate formula string
formula = formula_str(model_func, params)
print("Fitted formula:", formula)
```

## Installation
To install the `ge` package, use the following pip command:
```bash
pip install ge
```

This package is designed to be lightweight and easy to integrate into existing Python projects, particularly those involving data analysis and machine learning.