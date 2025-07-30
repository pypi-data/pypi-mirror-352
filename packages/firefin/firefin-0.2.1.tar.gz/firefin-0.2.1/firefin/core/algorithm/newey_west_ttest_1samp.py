"""
Calculate Newey-West Adjusted Standard Error in t-test for Academic Research
---------------------------------------------------
This module provides a class for performing a one-sample t-test with Newey-West adjusted standard errors.
The implementation focuses on clarity, comprehensive documentation, and best practices for financial research.
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple
import statsmodels.api as sm 

class NeweyWestTTest:
    """
    A class for performing a one-sample t-test using Newey-West adjusted standard errors.
    """

    @staticmethod
    def newey_west_ttest_1samp(data: Union[np.ndarray, pd.Series, list],
                               popmean: float = 0.0,
                               lags: int = 4,
                               nan_policy: str = 'omit') -> Tuple[float, float, float]:
        """
        Perform a one-sample t-test using Newey-West adjusted standard errors.

        Parameters
        ----------
        data : array-like
            The sample data.
        popmean : float, optional
            The hypothesized population mean (default is 0.0).
        lags : int, optional
            The number of lags for Newey-West adjustment (default is 4).
        nan_policy : {'propagate', 'omit', 'raise'}, optional
            Defines how to handle input NaNs:
                'propagate' : if a NaN is present in the input, return NaN for all outputs.
                'omit'      : omit NaNs when performing the calculation. If insufficient data remains, return NaN.
                'raise'     : if a NaN is present, raise a ValueError.
            (default is 'omit').

        Returns
        -------
        t_value : float
            The t-statistic.
        p_value : float
            The p-value for the t-test.
        se : float
            The Newey-West adjusted standard error.

        Raises
        ------
        ValueError
            If the input data is not one-dimensional or if nan_policy is set to 'raise' and data contains NaNs.
        """
        # Convert input data to a NumPy array
        data_arr = np.asarray(data)
        # Ensure the data is one-dimensional
        if data_arr.ndim != 1:
            raise ValueError("Input data must be a one-dimensional array or series. Only a single variable is allowed.")

        # Validate nan_policy argument
        if nan_policy not in ['propagate', 'omit', 'raise']:
            raise ValueError("nan_policy must be one of 'propagate', 'omit', or 'raise'.")

        # Handle NaN values according to nan_policy
        if nan_policy == 'propagate':
            if np.isnan(data_arr).any():
                return np.nan, np.nan, np.nan
        elif nan_policy == 'raise':
            if np.isnan(data_arr).any():
                raise ValueError("Input data contains NaN values.")
        elif nan_policy == 'omit':
            data_arr = data_arr[~np.isnan(data_arr)]
            # If no sufficient data remains after omitting NaNs, return NaN values
            if data_arr.size < 2:
                raise ValueError("No sufficient data (length < 2) remains after omitting NaNs.")

        # If the data length is insufficient, return NaNs
        if data_arr.size < 2:
            raise ValueError("No sufficient data (length < 2).")

        # Adjust the data by subtracting the hypothesized population mean
        adjusted_data = data_arr - popmean
        # Create an intercept term (a column of ones)
        X = np.ones(len(adjusted_data))
        # Fit an OLS model with Newey-West (HAC) standard errors
        model = sm.OLS(adjusted_data, X).fit(cov_type='HAC', cov_kwds={'maxlags': lags})
        # Extract the t-statistic, p-value, and standard error
        t_value = model.tvalues[0]
        p_value = model.pvalues[0]
        se = model.bse[0]

        return t_value, p_value, se
