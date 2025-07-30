"""
基本优化示例

这个示例展示了如何使用paper_solver解决一个简单的约束优化问题。
问题形式为：
    minimize: f(x) = 100(x₁ - x₀²)² + (1 - x₀)²
    subject to: x₀² + x₁ ≤ 1
                x₀² - x₁ ≤ 1
"""

from paper_solver import minimize_constrained, NonlinearConstraint
import numpy as np

def main():
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
            [2*x[0], 1],   # 第一个约束的雅可比矩阵
            [2*x[0], -1]   # 第二个约束的雅可比矩阵
        ])

    # 创建非线性约束
    constraint = NonlinearConstraint(
        constraints, 
        ('less', 0),  # 约束条件：小于等于0
        jac=jacobian
    )

    # 设置初始点
    x0 = np.array([0.0, 1.0])

    # 求解优化问题
    result = minimize_constrained(
        objective,
        x0,
        gradient,
        constraints=constraint,
        options={
            'initial_trust_radius': 1.0,
            'factorization_method': 'QRFactorization',
            'return_all': True
        }
    )

    # 打印结果
    print("优化结果:")
    print(f"x = {result.x}")
    print(f"目标函数值 = {result.fun}")
    print(f"是否成功 = {result.success}")
    print(f"迭代次数 = {result.nit}")
    print(f"状态信息 = {result.message}")

if __name__ == "__main__":
    main()
