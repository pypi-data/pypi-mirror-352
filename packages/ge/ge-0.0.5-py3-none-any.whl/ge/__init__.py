"""Utils for training models"""
__author__ = 'tcw'

from numpy import *
import re
import inspect


def nrmse(ydata, ypred):
    return sqrt(mean((ypred - ydata) ** 2)) / (max(ydata) - min(ydata))


def cv_rmse(ydata, ypred):
    return sqrt(mean((ypred - ydata) ** 2)) / mean(ydata)


def formula_str(fit_func, params, num_format_or_precision=2):
    """
    Returns a string showing what a fit functions' formula is, with params injected.
    The normal use is when you have a fit function, say:
        def func(x, a, b):
            return a + b * x)
    which you then fit to data
        params, pcov = curve_fit(func, xdata, ydata, p0=(1.0, 1.0))
    to get some numerical params, say:
        params == [1.07815647e-06,  1.28497311e+00]

    Then if you call
        formula_str(func, params)
    you'll get
        1.07e-06 + 1.28e+00 * x

    You can control the appearance of the numerical params in the formula using the num_format_or_precision argument.

    Note that to work, the formula of the fit function has to fit completely in the return line of the function.
    """
    if not isinstance(num_format_or_precision, str):
        num_format_or_precision = '{:.' + str(num_format_or_precision) + 'e}'

    # get the param names from the code of the function
    param_names = (
        re.compile('def [^(]+\(([^)]+)\)')
        .findall(inspect.getsource(fit_func))[0]
        .split(', ')[1:]
    )

    # get the formula string from the code of the function
    formula_str = re.compile('return ([^\n]*)').findall(inspect.getsource(fit_func))[0]

    # replace the param values in the formula string to get the result
    rep = dict(
        (re.escape(k), num_format_or_precision.format(v))
        for k, v in zip(param_names, params)
    )
    pattern = re.compile('|'.join(list(rep.keys())))
    formula_str_with_nums = pattern.sub(
        lambda m: rep[re.escape(m.group(0))], formula_str
    )

    return formula_str_with_nums




def weighted_rmse(ydata, ypred, weights):
    """
    Calculates the root mean square error between predicted and actual data, weighted by a given array of weights.
    This is useful when different data points have different levels of importance or reliability.

    Parameters:
        ydata (array-like): The actual data.
        ypred (array-like): The predicted data.
        weights (array-like): The weights for each data point. Must be the same length as ydata and ypred.

    Returns:
        float: The weighted root mean square error.

    Example:
        >>> actual_data = [1, 2, 3, 4, 5]
        >>> predicted_data = [1.1, 1.9, 3.0, 3.9, 5.1]
        >>> weights = [0.5, 2.0, 1.5, 1.0, 0.5]
        >>> error = weighted_rmse(actual_data, predicted_data, weights)
        >>> print("Weighted RMSE:", error)
    """
    if len(ydata) != len(ypred) or len(ydata) != len(weights):
        raise ValueError("All input arrays must have the same length.")
    
    import numpy as np
    weighted_squared_errors = weights * (np.array(ypred) - np.array(ydata)) ** 2
    mean_weighted_squared_error = np.sum(weighted_squared_errors) / np.sum(weights)
    return np.sqrt(mean_weighted_squared_error)

def model_summary(fit_func, params, xdata, ydata):
    """
    Provides a summary for a fitted model including the formula string and performance metrics like RMSE and NRMSE.

    Parameters:
        fit_func (function): The fit function used to model the data.
        params (list or array-like): The parameters obtained from fitting the model.
        xdata (array-like): The x-values of the data.
        ydata (array-like): The y-values of the data.

    Returns:
        dict: A dictionary containing the formula, RMSE, and NRMSE.

    Example:
        >>> from scipy.optimize import curve_fit
        >>> def model_func(x, a, b):
        ...     return a + b * x
        >>> xdata = [0, 1, 2, 3, 4]
        >>> ydata = [0, 2, 4, 6, 8]
        >>> params, _ = curve_fit(model_func, xdata, ydata)
        >>> summary = model_summary(model_func, params, xdata, ydata)
        >>> print(summary)
    """
    predicted_ydata = [fit_func(x, *params) for x in xdata]
    rmse_value = sqrt(mean((np.array(predicted_ydata) - np.array(ydata)) ** 2))
    nrmse_value = nrmse(ydata, predicted_ydata)
    formula = formula_str(fit_func, params)
    
    return {
        'formula': formula,
        'RMSE': rmse_value,
        'NRMSE': nrmse_value
    }
