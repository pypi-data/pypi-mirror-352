import logging
from typing import Any, Callable, Optional

import torch
from torch import Tensor
from typing_extensions import override

import lightning.pytorch as pl
from lightning.pytorch.callbacks.callback import Callback
from lightning.fabric.utilities.exceptions import MisconfigurationException
from lightning_utilities.core.rank_zero import rank_prefixed_message, rank_zero_warn
from lightning.pytorch.callbacks import EarlyStopping


log = logging.getLogger(__name__)


class RateEarlyStopping(EarlyStopping):
    r"""Monitor two metrics and stop training when the rate of the main metric and the auxiliary metric is less or greater than beta.

    Args:
        monitor_main: quantity to be monitored.
        monitor_aux: quantity to be monitored.
        beta: the threshold for the rate of the main metric and the auxiliary metric.
        min_delta: minimum change in the monitored quantity to qualify as an improvement, i.e. an absolute
            change of less than or equal to `min_delta`, will count as no improvement.
        patience: number of checks with no improvement
            after which training will be stopped. Under the default configuration, one check happens after
            every training epoch. However, the frequency of validation can be modified by setting various parameters on
            the ``Trainer``, for example ``check_val_every_n_epoch`` and ``val_check_interval``.

            .. note::

                It must be noted that the patience parameter counts the number of validation checks with
                no improvement, and not the number of training epochs. Therefore, with parameters
                ``check_val_every_n_epoch=10`` and ``patience=3``, the trainer will perform at least 40 training
                epochs before being stopped.

        verbose: verbosity mode.
        mode: one of ``'min'``, ``'max'``. In ``'min'`` mode, training will stop when the quantity
            monitored has stopped decreasing and in ``'max'`` mode it will stop when the quantity
            monitored has stopped increasing.
        strict: whether to crash the training if `monitor` is not found in the validation metrics.
        check_finite: When set ``True``, stops training when the monitor becomes NaN or infinite.
        stopping_threshold: Stop training immediately once the monitored quantity reaches this threshold.
        divergence_threshold: Stop training as soon as the monitored quantity becomes worse than this threshold.
        check_on_train_epoch_end: whether to run early stopping at the end of the training epoch.
            If this is ``False``, then the check runs at the end of the validation.
        log_rank_zero_only: When set ``True``, logs the status of the early stopping callback only for rank 0 process.

    Raises:
        MisconfigurationException:
            If ``mode`` is none of ``"min"`` or ``"max"``.
        RuntimeError:
            If the metric ``monitor`` is not available.

    Example::

        >>> from lightning.pytorch import Trainer
        >>> from lightning.pytorch.callbacks import EarlyStopping
        >>> early_stopping = EarlyStopping('val_loss')
        >>> trainer = Trainer(callbacks=[early_stopping])

    .. tip:: Saving and restoring multiple early stopping callbacks at the same time is supported under variation in the
        following arguments:

        *monitor, mode*

        Read more: :ref:`Persisting Callback State <extensions/callbacks_state:save callback state>`

    """

    mode_dict = {"min": torch.lt, "max": torch.gt}

    order_dict = {"min": "<", "max": ">"}

    def __init__(
        self,
        monitor_main: str,
        monitor_aux: str,
        beta: float = 0.1,
        min_delta: float = 0.0,
        patience: int = 3,
        verbose: bool = False,
        mode: str = "min",
        strict: bool = True,
        check_finite: bool = True,
        stopping_threshold: Optional[float] = None,
        divergence_threshold: Optional[float] = None,
        check_on_train_epoch_end: Optional[bool] = None,
        log_rank_zero_only: bool = False,
    ):
        super().__init__()
        self.monitor_main = monitor_main
        self.monitor_aux = monitor_aux
        self.beta = beta
        self.min_delta = min_delta
        self.patience = patience
        self.verbose = verbose
        self.mode = mode
        self.strict = strict
        self.check_finite = check_finite
        self.stopping_threshold = stopping_threshold
        self.divergence_threshold = divergence_threshold
        self.wait_count = 0
        self.stopped_epoch = 0
        self._check_on_train_epoch_end = check_on_train_epoch_end
        self.log_rank_zero_only = log_rank_zero_only

        if self.mode not in self.mode_dict:
            raise MisconfigurationException(f"`mode` can be {', '.join(self.mode_dict.keys())}, got {self.mode}")

        self.min_delta *= 1 if self.monitor_op == torch.gt else -1
        torch_inf = torch.tensor(torch.inf)
        self.best_score = torch_inf if self.monitor_op == torch.lt else -torch_inf

    @property
    @override
    def state_key(self) -> str:
        return self._generate_state_key(monitor_main=self.monitor_main, monitor_aux=self.monitor_aux, mode=self.mode)

    def _validate_condition_metric(self, logs: dict[str, Tensor]) -> bool:
        monitor_val_main = logs.get(self.monitor_main)
        monitor_val_aux = logs.get(self.monitor_aux)

        error_msg = (
            f"Early stopping conditioned on metric `{self.monitor_main} or {self.monitor_aux}` which is not available."
            " Pass in or modify your `EarlyStopping` callback to use any of the following:"
            f" `{'`, `'.join(list(logs.keys()))}`"
        )

        if monitor_val_main is None or monitor_val_aux is None:
            if self.strict:
                raise RuntimeError(error_msg)
            if self.verbose > 0:
                rank_zero_warn(error_msg, category=RuntimeWarning)

            return False

        return True

    def _run_early_stopping_check(self, trainer: "pl.Trainer") -> None:
        """Checks whether the early stopping condition is met and if so tells the trainer to stop the training."""
        logs = trainer.callback_metrics

        if trainer.fast_dev_run or not self._validate_condition_metric(  # disable early_stopping with fast_dev_run
            logs
        ):  # short circuit if metric not present
            return

        current = logs[self.monitor_main].squeeze()
        current_aux = logs[self.monitor_aux].squeeze()
        should_stop, reason = self._evaluate_stopping_criteria(current, current_aux)

        # stop every ddp process if any world process decides to stop
        should_stop = trainer.strategy.reduce_boolean_decision(should_stop, all=False)
        trainer.should_stop = trainer.should_stop or should_stop
        if should_stop:
            self.stopped_epoch = trainer.current_epoch
        if reason and self.verbose:
            self._log_info(trainer, reason, self.log_rank_zero_only)

    def _evaluate_stopping_criteria(self, current: Tensor, current_aux: Tensor) -> tuple[bool, Optional[str]]:
        should_stop = False
        reason = None
        if self.check_finite and not torch.isfinite(current):
            should_stop = True
            reason = (
                f"Monitored metric {self.monitor_main} = {current} is not finite."
                f" Previous best value was {self.best_score:.3f}. Signaling Trainer to stop."
            )
        elif self.stopping_threshold is not None and self.monitor_op(current, self.stopping_threshold):
            should_stop = True
            reason = (
                "Stopping threshold reached:"
                f" {self.monitor_main} = {current} {self.order_dict[self.mode]} {self.stopping_threshold}."
                " Signaling Trainer to stop."
            )
        elif self.divergence_threshold is not None and self.monitor_op(-current, -self.divergence_threshold):
            should_stop = True
            reason = (
                "Divergence threshold reached:"
                f" {self.monitor_main} = {current} {self.order_dict[self.mode]} {self.divergence_threshold}."
                " Signaling Trainer to stop."
            )
        # elif self.monitor_op(current - self.min_delta, self.best_score.to(current.device)):
        #     should_stop = False
        #     reason = self._improvement_message(current)
        #     self.best_score = current
        #     self.wait_count = 0
        elif self.monitor_op(current * self.beta, current_aux):
            should_stop = False
            self.wait_count = 0
        else:
            self.wait_count += 1
            if self.wait_count >= self.patience:
                should_stop = True
                reason = (
                    f"Monitored metric {self.monitor_main} did not improve in the last {self.wait_count} records."
                    f" Best score: {self.best_score:.3f}. Signaling Trainer to stop."
                )

        return should_stop, reason

    def _improvement_message(self, current: Tensor) -> str:
        """Formats a log message that informs the user about an improvement in the monitored score."""
        if torch.isfinite(self.best_score):
            msg = (
                f"Metric {self.monitor_main} improved by {abs(self.best_score - current):.3f} >="
                f" min_delta = {abs(self.min_delta)}. New best score: {current:.3f}"
            )
        else:
            msg = f"Metric {self.monitor_main} improved. New best score: {current:.3f}"
        return msg
