import torch
from torchmetrics import Metric
from torchmetrics.utilities import dim_zero_cat

from torchmetrics.regression import MeanSquaredError

__all__ = ["ExpectedLevelofError", "MeanSquaredError"]


class ExpectedLevelofError(Metric):
    """Calculates the expected level of error based on absolute and relative error thresholds.

    This metric evaluates predictions by comparing them against target values using both
    absolute and relative error thresholds. It calculates the proportion of predictions
    that fall within, above, or below an error envelope.

    The error envelope is defined as:
        upper_bound = target + (relative * target + absolute)
        lower_bound = target - (relative * target + absolute)

    Args:
        absolute (float): Absolute error threshold (default: 0.05)
        relative (float): Relative error threshold (default: 0.15)
        mode (str, optional): Evaluation mode, one of ['inside', 'above', 'below', 'all', None]
            - 'inside': Return proportion of predictions within envelope
            - 'above': Return proportion of predictions above envelope
            - 'below': Return proportion of predictions below envelope
            - 'all' or None: Return all three proportions
        **kwargs: Additional arguments passed to Metric base class

    Example:
        >>> metric = ExpectedLevelofError(absolute=0.1, relative=0.2)
        >>> preds = torch.tensor([1.1, 2.2, 3.3])
        >>> target = torch.tensor([1.0, 2.0, 3.0])
        >>> metric.update(preds, target)
        >>> above, below, inside = metric.compute()
    """

    def __init__(self, absolute=0.05, relative=0.15, mode=None, **kwargs):
        super().__init__(**kwargs)
        self.absolute = absolute
        self.relative = relative
        self.mode = mode
        self.add_state("preds", default=[], dist_reduce_fx="cat")
        self.add_state("target", default=[], dist_reduce_fx="cat")
        self.add_state("count", default=torch.tensor(0), dist_reduce_fx="sum")

    def update(self, preds, target):
        """Update metric states with new predictions and targets.

        Args:
            preds (torch.Tensor): Predicted values
            target (torch.Tensor): Ground truth values
        """
        self.preds.append(preds)
        self.target.append(target)

    def compute(self):
        """Compute the expected level of error metrics.

        Returns:
            If mode is None or 'all':
                tuple: (proportion_above, proportion_below, proportion_inside)
            If mode is 'inside', 'above', or 'below':
                torch.Tensor: Single proportion value

        Raises:
            ValueError: If mode is not one of ['inside', 'above', 'below', 'all', None]
        """
        # Concatenate all predictions and targets
        preds = dim_zero_cat(self.preds)
        target = dim_zero_cat(self.target)

        # Handle empty predictions
        count = len(preds)
        if count == 0:
            return torch.tensor(0), torch.tensor(0), torch.tensor(0)

        # Calculate error envelope bounds
        target_above_envelope = target + (self.relative * target + self.absolute)
        target_below_envelope = target - (self.relative * target + self.absolute)

        # Calculate proportions
        aboves = preds > target_above_envelope
        belows = preds < target_below_envelope
        insides = (preds >= target_below_envelope) & (preds <= target_above_envelope)

        ee_above = aboves.sum() / count
        ee_below = belows.sum() / count
        ee_inside = insides.sum() / count

        # Return based on mode
        if self.mode is None or self.mode == "all":
            return ee_above, ee_below, ee_inside
        if self.mode == "inside":
            return ee_inside
        if self.mode == "above":
            return ee_above
        if self.mode == "below":
            return ee_below
        raise ValueError(f"Invalid mode {self.mode} not in {['inside', 'above', 'below', 'all']}")


if __name__ == "__main__":
    # Example usage
    metric = ExpectedLevelofError()
    preds = [1.5, 2.2, 3.3, 4.4, 4.9]
    target = [1, 2, 3, 4, 5]
    metric.update(torch.tensor([preds]), torch.tensor([target]))
    aboves, belows, insides = metric.compute()
    print(aboves, belows, insides)
