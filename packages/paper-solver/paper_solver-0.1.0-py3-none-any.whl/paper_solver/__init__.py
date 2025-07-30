"""
Paper Solver
===========

一个专门面向造纸行业的高性能约束优化求解器。

主要组件:
---------
- minimize_constrained : 核心优化函数
- NonlinearConstraint : 处理非线性约束
"""

from ._minimize_constrained import minimize_constrained
from ._constraints import NonlinearConstraint, LinearConstraint, BoxConstraint


__version__ = "0.1.0"

__all__ = [
    'minimize_constrained',
    'NonlinearConstraint',
    'LinearConstraint',
    'BoxConstraint',
]