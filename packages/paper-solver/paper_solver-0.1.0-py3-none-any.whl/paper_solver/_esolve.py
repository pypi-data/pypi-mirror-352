
# 用于求解非线性等式方程的牛顿法
def esolve(f, x0, epsilon=1e-11, max_iterations=1000):
    h = 1e-8  # 初始步长
    h_min = 1e-11  # 最小步长，防止无限减小
    max_h_reduction = 10  # 步长最大减小次数

    def derivative(f, x, h):
        # 使用中心差分法计算导数
        return (f(x + h) - f(x - h)) / (2 * h)

    while True:
        x = x0
        iteration = 0
        h_reduction_count = 0

        while iteration < max_iterations:
            fx = f(x)
            fpx = derivative(f, x, h)

            # 检查导数是否为零，如果为零则增加步长
            if abs(fpx) < epsilon:
                if h_reduction_count < max_h_reduction:
                    h /= 10  # 减小步长
                    h_reduction_count += 1
                    if h < h_min:
                        break  # 如果步长已经很小，则停止迭代
                else:
                    break  # 如果多次减小步长后导数仍然很小，则停止迭代
            elif abs(fx) < 1e-4:  # 检查 f(x) 是否小于 1e-4
                break
            else:
                # 计算新的x值
                x_new = x - fx / fpx

                # 检查收敛性：如果x的变化很小，则认为收敛
                if abs(x_new - x) < epsilon:
                    x = x_new
                    break

                # 根据导数值的大小动态调整步长
                h = min(h, abs(fx / fpx) * 0.1)

                x = x_new
                iteration += 1

        if abs(f(x)) < 1e-4:
            break
        else:
            x0 /= 10  # 缩小初始点十倍重新运行

    return x
