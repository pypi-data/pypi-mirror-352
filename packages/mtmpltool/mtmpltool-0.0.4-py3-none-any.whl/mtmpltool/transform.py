import numpy as np
import torch
import torch.nn.functional as F
from typing import TypeVar

__all__ = ["ScalarToOnehot", "Random_0_or_1"]

# 定义类型变量，支持 numpy 数组和 PyTorch 张量
Array = TypeVar("Array", np.ndarray, torch.Tensor)


class ScalarToOnehot:
    """将连续标量值转换为等间隔的 one-hot 编码。

    该类将连续的标量值离散化为等间隔的区间，并转换为 one-hot 编码形式。
    例如，对于输入值 0.555，如果 scale=10，会被映射到 [0.5, 0.6) 区间，
    对应的 one-hot 向量中该位置为 1，其他位置为 0。

    参数:
        vmin (float): 标量值的最小值（原始尺度）
        vmax (float): 标量值的最大值（原始尺度）
        scale (float): 缩放因子，用于控制离散化精度。例如 scale=10 表示将 0.1 的间隔转换为 1 的整数间隔
        bounded (bool): 区间类型。True 表示 [vmin, vmax]（闭区间），False 表示 [vmin, vmax)（左闭右开区间）

    示例:
        >>> values = np.array([-0.19, 0.555, 0.8])
        >>> scale, bounded = 10, True
        >>> vmin, vmax = ScalarToOnehot.calculate_value_min_max(values, scale)
        >>> _, onehot = ScalarToOnehot(vmin, vmax, scale, bounded)(None, values)
        >>> print(onehot)  # 输出对应的 one-hot 编码
    """

    def __init__(self, vmin: float, vmax: float, scale: float = 1.0, bounded: bool = False):
        """初始化转换器。

        参数校验:
            - scale 必须大于 0，否则无法进行有效的离散化
        """
        self.vmin = vmin
        self.vmax = vmax
        self.scale = scale
        self.bounded = bounded

        if scale <= 0:
            raise ValueError("缩放因子 scale 必须大于 0")

    @staticmethod
    def calculate_value_min_max(scalars, scale) -> tuple[float, float]:
        """计算输入数据的最小值和最大值，并进行缩放对齐。

        步骤:
        1. 将输入转换为 PyTorch 张量
        2. 应用缩放因子
        3. 计算缩放后的最小值和最大值
        4. 将结果转换回原始尺度

        参数:
            scalars: 输入的标量值数组（numpy 数组或 PyTorch 张量）
            scale: 缩放因子

        返回:
            tuple[float, float]: (最小值, 最大值)，已对齐到 scale 的整数倍
        """
        # 统一转换为 PyTorch 张量
        if isinstance(scalars, np.ndarray):
            input_tensor = torch.from_numpy(scalars).float()
        else:
            input_tensor = scalars.float()

        # 应用缩放并计算边界值
        scaled_values = input_tensor * scale
        vmin_scaled = int(torch.floor(scaled_values.min()))  # 向下取整
        vmax_scaled = int(torch.ceil(scaled_values.max()))  # 向上取整

        # 转换回原始尺度
        return vmin_scaled / scale, vmax_scaled / scale

    def to_onehot(self, scalars: Array) -> torch.Tensor:
        """将标量值转换为 one-hot 编码。

        转换步骤:
        1. 将输入值缩放到整数区间
        2. 计算每个值对应的区间索引
        3. 生成对应的 one-hot 编码

        参数:
            scalars: 输入的标量值数组

        返回:
            torch.Tensor: one-hot 编码后的张量，形状为 (n, num_classes)

        异常:
            ValueError: 当输入值超出 [vmin, vmax] 范围时抛出
        """
        vmin, vmax, scale, bounded = self.vmin, self.vmax, self.scale, self.bounded

        # 统一转换为 PyTorch 张量并应用缩放
        if isinstance(scalars, np.ndarray):
            input_tensor = torch.from_numpy(scalars).float()
        else:
            input_tensor = scalars.float()
        scaled_values = input_tensor * scale

        # 计算缩放后的边界值
        if vmin is None:
            vmin_scaled = int(torch.floor(scaled_values.min()))
        else:
            vmin_scaled = int(vmin * scale)

        if vmax is None:
            vmax_scaled = int(torch.ceil(scaled_values.max()))
        else:
            vmax_scaled = int(vmax * scale)

        # 检查输入值是否在有效范围内
        if (scaled_values < vmin_scaled).any() or (scaled_values > vmax_scaled).any():
            raise ValueError("输入值超出 [vmin, vmax] 范围，请检查参数或输入数据")

        # 根据区间类型调整类别数量
        add_one = 0 if bounded else 1  # 闭区间不需要额外加1，开区间需要
        num_classes: int = int(vmax_scaled - vmin_scaled + add_one)

        # 计算每个值对应的区间索引
        discrete_indices = torch.round(scaled_values - vmin_scaled).long()

        # 处理右边界值
        if bounded:
            discrete_indices[discrete_indices == num_classes] -= 1

        # 生成 one-hot 编码
        one_hot = F.one_hot(discrete_indices, num_classes=num_classes)
        return one_hot.float()

    def to_range(self):
        """获取每个区间的左右边界值。

        计算步骤:
        1. 将边界值缩放到整数区间
        2. 生成等间隔的边界值数组
        3. 转换回原始尺度

        返回:
            tuple[torch.Tensor, torch.Tensor]: (左边界值数组, 右边界值数组)
        """
        vmin, vmax, scale, bounded = self.vmin, self.vmax, self.scale, self.bounded
        vmin_scaled, vmax_scaled = int(vmin * scale), int(vmax * scale)
        add_one = 0 if bounded else 1

        # 生成等间隔的边界值
        class_left_edges_scaled = torch.arange(start=vmin_scaled, end=vmax_scaled + add_one, step=1)
        class_right_edges_scaled = class_left_edges_scaled + 1

        # 转换回原始尺度
        class_left_edges = class_left_edges_scaled / scale
        class_right_edges = class_right_edges_scaled / scale

        return class_left_edges, class_right_edges

    def __call__(self, inputs: Array, targets: Array) -> tuple[torch.Tensor, torch.Tensor]:
        """执行转换操作。

        参数:
            inputs: 输入数据（本方法中未使用）
            targets: 需要转换的目标数据

        返回:
            tuple[torch.Tensor, torch.Tensor]: (原始输入, one-hot编码后的目标)
        """
        return torch.Tensor(inputs), self.to_onehot(targets)


class Random_0_or_1:
    """随机将输入数据中的部分值替换为 0 或 1。

    该类用于数据增强，通过随机替换输入数据中的值来生成新的训练样本。
    替换操作受 mask 控制，只有 mask 中为 0 的位置才会被替换。

    工作原理:
    1. 根据概率 p 决定是否执行替换
    2. 使用 mask 控制哪些位置可以被替换
    3. 被替换的位置随机填充 0 或 1
    4. 在目标数据中标记被替换的样本

    参数:
        p (float): 触发替换的概率，范围 [0, 1]
        value (int): 替换后的目标值，用于标记被替换的样本
        mask (torch.Tensor, optional): 控制哪些位置可以被替换的掩码。None 表示所有位置都可替换

    示例:
        >>> mask = torch.zeros(10)
        >>> mask[5:] = 1  # 只替换前5个位置
        >>> transform = Random_0_or_1(p=0.1, value=1)
        >>> inputs = torch.ones(10)
        >>> new_inputs, new_targets = transform(inputs, torch.zeros(10), mask)
        >>> print(new_inputs)
        >>> print(new_targets)
    """

    def __init__(self, p=0.1, value=1, mask=None):
        """初始化转换器。

        参数:
            p: 替换概率
            value: 目标标记值
            mask: 替换掩码，None 表示全1掩码（所有位置都可替换）
        """
        self.p = p
        self.value = value
        self.mask = mask

    def __call__(self, inputs, targets):
        """执行随机替换操作。

        步骤:
        1. 检查或创建掩码
        2. 根据概率决定是否执行替换
        3. 生成随机替换值
        4. 应用掩码进行替换
        5. 更新目标标记

        参数:
            inputs: 输入数据
            targets: 目标数据

        返回:
            tuple[torch.Tensor, torch.Tensor]: (处理后的输入数据, 处理后的目标数据)
        """
        # 创建或使用现有掩码
        if self.mask is not None:
            mask = self.mask
            # 判断mask和inputs的形状是否相同:
            if mask.shape != inputs.shape:
                raise ValueError(f"mask和inputs的形状不相同: {mask.shape} != {inputs.shape}")
        else:
            mask = torch.ones_like(inputs, dtype=torch.bool)
            self.mask = mask

        # 根据概率决定是否执行替换
        if np.random.rand() < self.p:
            # 生成随机替换值（0或1）
            random_01 = torch.randint(low=0, high=2, size=inputs.shape, dtype=inputs.dtype)
            # 应用掩码：mask为True的位置保持原值，False的位置使用随机值
            false_inputs = torch.where(mask, inputs, random_01)
            # 创建目标标记：所有位置为0，最后一维为目标值
            false_targets = torch.full_like(targets, 0)
            false_targets[..., -1] = self.value
            return false_inputs, false_targets
        else:
            return inputs, targets
