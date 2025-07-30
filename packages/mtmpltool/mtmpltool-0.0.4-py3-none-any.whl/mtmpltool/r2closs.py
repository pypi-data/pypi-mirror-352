import torch
import torch.nn as nn
from torch.nn import functional as F
from typing import Optional

from mtmpltool.transform import ScalarToOnehot
from pytorch_forecasting.metrics import QuantileLoss

__all__ = ["RegressionR2CLoss", "ClassificationR2CLoss", "QuantileR2CLoss", "AttentionPoolingR2CLoss"]


class BaseR2CLoss(nn.Module):
    """Base class for all loss functions in the module.

    This abstract class defines the interface for loss functions with methods for
    converting inputs to probabilities and values, and computing the loss.

    Methods:
        to_p: Convert inputs to probability distribution
        to_value: Convert inputs to scalar values
        forward: Compute the loss between inputs and targets
    """

    def __init__(self):
        super().__init__()

    def to_probability(self, inputs):
        """Convert inputs to probability distribution.

        Args:
            inputs (torch.Tensor): Input tensor

        Returns:
            torch.Tensor: Probability distribution
        """
        raise NotImplementedError("to_p method must be implemented in subclass")

    def to_prediction(self, inputs):
        """Convert inputs to scalar values.

        Args:
            inputs (torch.Tensor): Input tensor

        Returns:
            torch.Tensor: Scalar values
        """
        raise NotImplementedError("to_value method must be implemented in subclass")

    def forward(self, inputs, target):
        """Compute the loss between inputs and targets.

        Args:
            inputs (torch.Tensor): Predicted values
            target (torch.Tensor): Ground truth values

        Returns:
            torch.Tensor: Loss value
        """
        raise NotImplementedError("forward method must be implemented in subclass")


class RegressionR2CLoss(BaseR2CLoss):
    """Regression loss function with R2C transformation.

    Computes the loss between predicted and target values using R2C transformation.
    """

    def __init__(self, loss_fn_name: str, loss_fn_kwargs: Optional[dict] = None, **kwargs):
        try:
            loss_fn_kwargs = {} if loss_fn_kwargs is None else loss_fn_kwargs
            self.loss_fn = getattr(torch.nn, loss_fn_name)(**loss_fn_kwargs)
        except AttributeError:
            raise ValueError(f"Loss function {loss_fn_name} not found in torch.nn")

    def to_probability(self, inputs):
        return torch.ones_like(inputs)

    def to_prediction(self, inputs):
        return torch.Tensor(inputs)

    def forward(self, inputs, target):
        return self.loss(self.to_prediction(inputs), target)


class ClassificationR2CLoss(BaseR2CLoss, nn.CrossEntropyLoss):
    """Cross entropy loss with optional class weights.

    Args:
        weight (torch.Tensor, optional): Class weights for weighted loss
        weight_gen_params (dict, optional): Parameters for generating class weights
    """

    def __init__(self, weight: Optional[torch.Tensor] = None, weight_gen_params: Optional[dict] = None, **kwargs):
        if weight is None:
            self.weight: torch.Tensor = self.generate_weight(**weight_gen_params)
        else:
            self.weight = weight
        self.register_buffer("weight", weight)
        super(nn.CrossEntropyLoss, self).__init__(**kwargs)

    def generate_weight(self, **weight_gen_params):
        trans = ScalarToOnehot(**weight_gen_params)
        edges_left, edges_right = trans.to_range()
        return (edges_left + edges_right) / 2

    def to_probability(self, inputs):
        return F.softmax(inputs, dim=1)

    def to_prediction(self, inputs):
        return self.weight[self.to_probability(inputs).max(dim=1).indices]


class QuantileR2CLoss(BaseR2CLoss, QuantileLoss):
    """Quantile regression loss for multiple quantiles.

    Computes the pinball loss for multiple quantiles simultaneously.

    Args:
        quantiles (list): List of quantile levels (e.g., [0.1, 0.5, 0.9])
    """

    def __init__(self, quantiles):
        super(QuantileLoss, self).__init__(quantiles=quantiles)

    def to_probability(self, inputs):
        shape = list(inputs.shape)
        shape[-1] = 1
        return torch.ones(shape).type_as(inputs)

    def to_prediction(self, inputs):
        return super(QuantileLoss, self).to_prediction(inputs)


class AttentionPoolingR2CLoss(BaseR2CLoss):
    """Base class for attention-based loss functions.

    Implements common functionality for attention-based losses with temperature scaling.

    Args:
        loss_fn (nn.Module): Base loss function to use
        weight (torch.Tensor): Attention weights
        t (float, optional): Temperature scaling factor. If None, uses sqrt(len(weight))
    """

    def __init__(
        self,
        loss_fn_name: str,
        loss_fn_kwargs: Optional[dict] = None,
        weight: Optional[torch.Tensor] = None,
        weight_gen_params: Optional[dict] = None,
        t=None,
        **kwargs,
    ):
        super().__init__()
        try:
            self.loss_fn = getattr(torch.nn, loss_fn_name)(**loss_fn_kwargs)
        except AttributeError:
            raise ValueError(f"Loss function {loss_fn_name} not found in torch.nn")
        if weight is None:
            weight: torch.Tensor = self.generate_weight(**weight_gen_params)
        self.register_buffer("weight", weight)
        self.weight: torch.Tensor

        if t is None:
            t = torch.sqrt(torch.tensor(len(weight)))
        else:
            t = torch.tensor(t)
        self.register_buffer("t", t)
        self.t: torch.Tensor

    def generate_weight(self, **weight_gen_params):
        trans = ScalarToOnehot(**weight_gen_params)
        edges_left, edges_right = trans.to_range()
        return edges_left

    def to_probability(self, inputs: torch.Tensor):
        return F.softmax(inputs / self.t, dim=1)

    def to_prediction(self, inputs: torch.Tensor):
        return self.to_probability(inputs) @ self.weight

    def forward(self, inputs: torch.Tensor, target: torch.Tensor):
        return self.loss_fn(self.to_prediction(inputs).view(-1), target.view(-1))
