# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/fire-institute/fire/blob/master/NOTICE.txt

import typing

import pandas as pd

from ...core.plot import plots
from ..eva_utils import ForwardReturns, IC, QuantileReturns, compute_ic, compute_quantile_returns

__all__ = ["Evaluator"]


def to_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy(deep=False)
    if not isinstance(out.index, pd.DatetimeIndex):
        out.index = pd.to_datetime(out.index)
    return out


class Evaluator:
    def __init__(self, factor: pd.DataFrame, forward_returns: ForwardReturns):
        self.factor = factor
        self.forward_returns = forward_returns
        self._to_datetime_index()
        self._reindex_forward_returns()
        self._result = {}

    def _to_datetime_index(self):
        self.factor = to_datetime_index(self.factor)
        self.forward_returns = {k: to_datetime_index(v) for k, v in self.forward_returns.items()}

    def _reindex_forward_returns(self):
        self.forward_returns = {k: v.reindex_like(self.factor, copy=False) for k, v in self.forward_returns.items()}

    def get_ic(self, method: typing.Literal["pearson", "kendall", "spearman"], plot=True) -> IC:
        cache_key = ("ic", (method,))
        if cache_key not in self._result:
            self._result[cache_key] = compute_ic(self.factor, self.forward_returns, method)
        ic = self._result[cache_key]
        if plot:
            plots.plt_ic(ic)
        return ic

    def get_quantile_returns(self, quantiles: int = 5, plot=True) -> QuantileReturns:
        cache_key = ("quantile_returns", (quantiles,))
        if cache_key not in self._result:
            self._result[cache_key] = compute_quantile_returns(self.factor, self.forward_returns, quantiles)
        qt = self._result[cache_key]
        if plot:
            plots.plt_quantile_cumulative_returns(qt)
            plots.plt_quantile_cumulated_end_returns(qt)
        return qt
