import torch

__all__ = ["LinearLRWarmupAndCosineAnnealingWarmRestarts"]


class LinearLRWarmupAndCosineAnnealingWarmRestarts(torch.optim.lr_scheduler.SequentialLR):
    """Combines linear warmup and cosine annealing with warm restarts for learning rate scheduling.

    This scheduler implements a two-phase learning rate schedule:
    1. Linear warmup phase: Gradually increases learning rate from a small value
    2. Cosine annealing phase: Decreases learning rate following a cosine curve with periodic restarts

    Args:
        optimizer (torch.optim.Optimizer): The optimizer whose learning rate will be scheduled
        warmup_epochs (int): Number of epochs for linear warmup phase
        linear_params (dict): Parameters for LinearLR scheduler, excluding total_iters
        cosine_params (dict): Parameters for CosineAnnealingWarmRestarts scheduler, must include T_0
        **kwargs: Additional arguments passed to SequentialLR

    Example:
        >>> optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
        >>> scheduler = LinearLRWarmupAndCosineAnnealingWarmRestarts(
        ...     optimizer,
        ...     warmup_epochs=5,
        ...     linear_params={"start_factor": 0.1},
        ...     cosine_params={"T_0": 10, "eta_min": 1e-6}
        ... )
    """

    def __init__(self, optimizer, warmup_epochs: int, linear_params: dict, cosine_params: dict, **kwargs):
        # Linear warmup phase
        _linear_params = linear_params.copy()
        _linear_params["total_iters"] = warmup_epochs
        scheduler_linear_warmup = torch.optim.lr_scheduler.LinearLR(optimizer, **_linear_params)

        # Cosine annealing phase with warm restarts
        _cosine_params = cosine_params.copy()
        T_0 = _cosine_params.pop("T_0")  # Required parameter for restart period
        scheduler_cosine_annealing = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=T_0, **_cosine_params
        )

        # Combine schedulers with warmup_epochs as the transition point
        schedulers = [scheduler_linear_warmup, scheduler_cosine_annealing]
        milestones = [warmup_epochs]
        super().__init__(optimizer, schedulers, milestones, **kwargs)
