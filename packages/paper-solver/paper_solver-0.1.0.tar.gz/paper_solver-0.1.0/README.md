# Paper Solver

QC Lab发布的首款开源求解器项目

Paper Solver是一个专门面向造纸行业的高性能约束优化求解器，提供了强大的信赖域算法来解决各类约束优化问题。

## 特性

- 支持多种约束类型：
  - 边界约束 (BoxConstraint)
  - 线性约束 (LinearConstraint)
  - 非线性约束 (NonlinearConstraint)
- 提供两种主要的优化算法：
  - 等式约束SQP算法
  - 信赖域内点法
- 适用于大规模优化问题
- 支持自动微分和数值微分
- 提供灵活的约束定义方式

## 安装

```bash
pip install paper-solver
```

## 快速开始

以下是一个简单的约束优化问题示例：

```python
from paper_solver import minimize_constrained, NonlinearConstraint
import numpy as np

# 定义目标函数
def objective(x):
    return 100 * (x[1] - x[0]**2)**2 + (1 - x[0])**2

# 定义目标函数的梯度
def gradient(x):
    return np.array([
        -400 * x[0] * (x[1] - x[0]**2) - 2 * (1 - x[0]),
        200 * (x[1] - x[0]**2)
    ])

# 定义约束函数
def constraints(x):
    return np.array([
        x[0]**2 + x[1] - 1,  # 第一个约束
        x[0]**2 - x[1] - 1   # 第二个约束
    ])

# 定义约束的雅可比矩阵
def jacobian(x):
    return np.array([
        [2*x[0], 1],
        [2*x[0], -1]
    ])

# 创建非线性约束
constraint = NonlinearConstraint(
    constraints, 
    ('less', 0),
    jac=jacobian
)

# 求解优化问题
result = minimize_constrained(
    objective,
    x0=np.array([0.0, 1.0]),
    grad=gradient,
    constraints=constraint
)
```

## 主要组件

- `minimize_constrained`: 核心优化函数
- `BoxConstraint`: 用于定义边界约束
- `LinearConstraint`: 用于定义线性约束
- `NonlinearConstraint`: 用于定义非线性约束

## 约束类型支持

支持多种约束定义方式：
- 区间约束：`lb <= x <= ub`
- 大于等于约束：`x >= lb`
- 小于等于约束：`x <= ub`
- 等式约束：`x == c`

## 参考文献

- Byrd, Richard H., Mary E. Hribar, and Jorge Nocedal. "An interior point algorithm for large-scale nonlinear programming." SIAM Journal on Optimization 9.4 (1999): 877-900.
- Lalee, Marucha, Jorge Nocedal, and Todd Plantega. "On the implementation of an algorithm for large-scale equality constrained optimization." SIAM Journal on Optimization 8.3 (1998): 682-706.

## 许可证

本项目采用 Apache License 2.0 许可证。详细信息请查看 [LICENSE](LICENSE) 文件。

Copyright 2024 QC Lab