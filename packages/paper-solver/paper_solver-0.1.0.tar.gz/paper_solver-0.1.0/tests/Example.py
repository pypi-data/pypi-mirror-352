from __future__ import division
import numpy as np
from paper_solver._constraints import NonlinearConstraint, BoxConstraint, LinearConstraint
from paper_solver._minimize_constrained import minimize_constrained
# from paper_solver import minimize_constrained, NonlinearConstraint, BoxConstraint, LinearConstraint

# 定义目标函数
fun = lambda x: 100 * (x[1] - x[0]**2)**2 + (1 - x[0])**2

# 定义梯度函数
grad = lambda x: np.array([
    -400 * x[0] * (x[1] - x[0]**2) - 2 * (1 - x[0]),   # 对 x0 求偏导
    200 * (x[1] - x[0]**2)                            # 对 x1 求偏导
])

# 定义约束函数
def constraint_function(x):
    return np.array([
        x[0]**2 + x[1] - 1,  # 第一个约束
        x[0]**2 - x[1] - 1   # 第二个约束
    ])

# 定义雅可比矩阵函数
def jac_constraint_function(x):
    return np.array([
        [2*x[0], 1],   # 第一个约束的雅可比矩阵
        [2*x[0], -1]   # 第二个约束的雅可比矩阵
    ])

def hess_constraint_function(x, v):
    return v[0]*np.array([[2, 0], [0, 0]]) + v[1]*np.array([[2, 0], [0, 0]])

# 定义约束类型

# 创建非线性约束对象
nonlinear_constraint = NonlinearConstraint(constraint_function, ('less', 0), jac=jac_constraint_function, hess=hess_constraint_function)

# 定义线性约束
linear_constraint = LinearConstraint([[2,1]], ('less', 1))

# 定义边界约束
box = BoxConstraint(("interval", (0,-0.5),(1,2)))

x0 = [0,1]

# 应用求解器
result = minimize_constrained(fun, x0, grad, constraints=(nonlinear_constraint, box, linear_constraint))


print(result.x)



import numpy as np
from _constraints import NonlinearConstraint, BoxConstraint, LinearConstraint
from _minimize_constrained import minimize_constrained
fun = lambda x: ...
grad = lambda x: np.array([...])
def constraint_function(x):
    return np.array([...])
def jac_constraint_function(x):
    return np.array([...])
def hess_constraint_function(x, v):
    return v[0]*np.array([...])
nonlinear_constraint = NonlinearConstraint(...)
linear_constraint = LinearConstraint(...)
box = BoxConstraint((...))
x0 = [...]
result = minimize_constrained(fun, x0, grad, constraints=(nonlinear_constraint, box, linear_constraint))
