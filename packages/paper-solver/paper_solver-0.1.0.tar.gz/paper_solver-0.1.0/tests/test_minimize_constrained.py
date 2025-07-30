"""
测试minimize_constrained函数的基本功能
"""

import numpy as np
import pytest
from paper_solver import minimize_constrained, NonlinearConstraint

def test_rosenbrock_with_constraints():
    """
    测试带约束的Rosenbrock函数优化
    """
    # 定义Rosenbrock函数
    def fun(x):
        return 100 * (x[1] - x[0]**2)**2 + (1 - x[0])**2

    def grad(x):
        return np.array([
            -400 * x[0] * (x[1] - x[0]**2) - 2 * (1 - x[0]),
            200 * (x[1] - x[0]**2)
        ])

    # 定义约束
    def constraint_fun(x):
        return np.array([
            x[0]**2 + x[1] - 1,
            x[0]**2 - x[1] - 1
        ])

    def constraint_jac(x):
        return np.array([
            [2*x[0], 1],
            [2*x[0], -1]
        ])

    constraint = NonlinearConstraint(
        constraint_fun, 
        ('less', 0),
        jac=constraint_jac
    )

    # 初始点
    x0 = np.array([0.0, 1.0])

    # 优化
    result = minimize_constrained(
        fun,
        x0,
        grad,
        constraints=constraint,
        options={'initial_trust_radius': 1.0}
    )

    # 验证结果
    assert result.success
    assert result.fun < 1.0  # 目标函数值应该很小
    assert np.all(constraint_fun(result.x) <= 1e-6)  # 约束应该满足

def test_quadratic_with_box_constraints():
    """
    测试带边界约束的二次函数优化
    """
    # 简单的二次函数
    def fun(x):
        return (x[0] - 2)**2 + (x[1] - 3)**2

    def grad(x):
        return np.array([
            2 * (x[0] - 2),
            2 * (x[1] - 3)
        ])

    # 边界约束
    bounds = [(-1, 4), (-1, 4)]

    # 初始点
    x0 = np.array([0.0, 0.0])

    # 优化
    result = minimize_constrained(
        fun,
        x0,
        grad,
        bounds=bounds
    )

    # 验证结果
    assert result.success
    assert np.all(result.x >= -1)  # 检查下界
    assert np.all(result.x <= 4)   # 检查上界
    assert np.allclose(result.x, [2, 3], atol=1e-5)  # 检查是否达到预期最优解

def test_linear_constraints():
    """
    测试带线性约束的优化问题
    """
    # 简单的二次函数
    def fun(x):
        return (x[0] - 1)**2 + (x[1] - 2)**2

    def grad(x):
        return np.array([
            2 * (x[0] - 1),
            2 * (x[1] - 2)
        ])

    # 线性约束 x + y <= 2
    A = np.array([[1, 1]])
    b = np.array([2])

    # 初始点
    x0 = np.array([0.0, 0.0])

    # 优化
    result = minimize_constrained(
        fun,
        x0,
        grad,
        A=A,
        b=b
    )

    # 验证结果
    assert result.success
    assert np.dot(A, result.x) <= b + 1e-6  # 检查约束是否满足
    assert result.fun < 1.0  # 目标函数值应该合理

def test_invalid_inputs():
    """
    测试无效输入的处理
    """
    def fun(x):
        return x[0]**2 + x[1]**2

    def grad(x):
        return np.array([2*x[0], 2*x[1]])

    # 测试维度不匹配的初始点
    with pytest.raises(ValueError):
        minimize_constrained(fun, np.array([0.0]), grad)

    # 测试无效的约束
    with pytest.raises(ValueError):
        minimize_constrained(fun, np.array([0.0, 0.0]), grad, A=np.array([[1]]), b=np.array([1, 1]))

if __name__ == '__main__':
    pytest.main([__file__])