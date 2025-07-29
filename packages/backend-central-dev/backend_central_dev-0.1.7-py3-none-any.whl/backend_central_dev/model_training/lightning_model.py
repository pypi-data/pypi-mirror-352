import torchmetrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
import torchmetrics.classification
import time
import lightning as L
import torch
import torch.nn as nn
import datetime
import numpy as np
from ..utils.pytorch_utils import clear_memory
from ..utils import plotting_utils
from typing import Callable
from dataclasses import dataclass, field


@dataclass(kw_only=True)
class FineTunableModel():

    model_init_func: Callable[[], nn.Module]
    model_fine_tune_func: Callable[[nn.Module, int], nn.Module]

    def __call__(self, output_features, model_init_kwargs: dict = {}):
        return self.model_fine_tune_func(
            self.model_init_func(**model_init_kwargs),
            output_features
        )


class MyLightningModel(L.LightningModule):

    def __init__(
        self,
    ) -> None:
        super().__init__()
        clear_memory()

    def forward(self, inputs, **kwargs):
        return self.model(inputs)

    def on_train_epoch_start(self) -> None:
        if self.st is None:
            self.st = time.time()
        if self.trainer.progress_bar_metrics.get("time_spent") is None:
            self.trainer.progress_bar_metrics["time_spent"] = "--:--:--"
        if self.trainer.progress_bar_metrics.get("time_left") is None:
            self.trainer.progress_bar_metrics["time_left"] = "--:--:--"
        return super().on_train_epoch_start()

    def on_train_epoch_end(self) -> None:
        used_time = time.time() - self.st
        avg_time = used_time / self.trainer.global_step
        time_left = int(
            (self.trainer.estimated_stepping_batches - self.trainer.global_step)
            * avg_time
        )
        self.trainer.progress_bar_metrics["time_spent"] = str(
            datetime.timedelta(seconds=int(used_time))
        )
        self.trainer.progress_bar_metrics["time_left"] = str(
            datetime.timedelta(seconds=time_left)
        )
        return super().on_train_epoch_end()


class MlxOps_LightningModel(MyLightningModel):

    def __init__(
        self,
        fine_tunable_model: FineTunableModel,
        output_features: int,
        loss_fn_key="CrossEntropyLoss",
        loss_fn_hparams: dict = {},
        optimizer_key="Adam",
        optimizer_hparams: dict = {},
        lr_scheduler_key=None,
        lr_scheduler_hparams: dict = {},
        model_init_kwargs: dict = {},
        task="multiclass",
        debug: bool = False,
        **kwargs
    ):
        super().__init__()
        self.save_hyperparameters(ignore=['fine_tunable_model'])
        self.model = fine_tunable_model(
            output_features, model_init_kwargs=model_init_kwargs)
        self.loss_fn = getattr(torch.nn, loss_fn_key)(**loss_fn_hparams)

        self.st = None
        self.y_true = np.array([])
        self.y_pred = np.array([])
        self.losses = np.array([])
        self.cm = None
        self.cr = None

        kwargs = {}
        kwargs["num_classes"] = output_features

        if task == "multiclass":
            self.metrics = dict(
                acc=torchmetrics.Accuracy(task=task, top_k=1, **kwargs),
                macro_acc=torchmetrics.Accuracy(
                    task=task, top_k=1, average="macro", **kwargs
                ),
                f1=torchmetrics.F1Score(task=task, average="macro", **kwargs),
                roc_auc=torchmetrics.AUROC(task=task, **kwargs),
            )

        self.metrics_in_batch = {}

    def on_fit_start(self):
        # if self.rebalancedmix is not None:
        #     self.rebalancedmix.init(self.trainer.datamodule.train)
        if self.trainer.datamodule.mixed_aug_with_target_and_model is not None:
            self.trainer.datamodule.mixed_aug_with_target_and_model.setup_saliency_model(
                self
            )

    def on_fit_end(self):
        # if self.comixup is not None:
        #     self.comixup.mpp.close()
        pass

    def on_train_end(self):
        if (
            self.trainer.fast_dev_run
            and self.trainer.datamodule.train.__se__ is not None
        ):
            print(
                [
                    round(rr, 8)
                    for rr in self.trainer.datamodule.mix_aug_sampler.get_class_sampling_prob()
                ]
            )
            print(self.trainer.datamodule.mix_aug_sampler)
            # print(self.crp)

    def eval_metrics(self, event_key, batch, batch_idx, output, loss):
        x, y = batch
        # print(x.mean().item(), x.max().item(), x.min().item())
        # print(event_key)
        # plotting_utils.plot_hor([xx.cpu().permute(1,2,0) for xx in x[:8]])
        metrics = {}
        if self.hparams.task == "multiclass":
            _y = y.detach().cpu()
            odc = output.detach().cpu()
            for k, v in self.metrics.items():
                key = f"{event_key}_{k}"

                # we have to make the y to cpu to avoid MPS glitch
                if len(_y.shape) > 1:
                    _y = _y.argmax(dim=1)
                score = v(odc.float(), _y).item()
                metrics[key] = score
                # self.trainer.progress_bar_metrics[k] = metrics[key]
                if event_key == "val":
                    if self.metrics_in_batch.get(key) is None:
                        self.metrics_in_batch[key] = []
                    self.metrics_in_batch[key].append(score)

            if event_key == "val":
                self.y_true = np.append(self.y_true, _y.numpy())
                self.y_pred = np.append(
                    self.y_pred, torch.argmax(odc, dim=1).numpy()
                )
                self.losses = np.append(self.losses, loss.cpu().item())

                ytp = torch.from_numpy(self.y_pred)
                ytt = torch.from_numpy(self.y_true)
                overall_val_acc = self.metrics["acc"](ytp, ytt)
                self.trainer.progress_bar_metrics["max_val_acc"] = max(
                    overall_val_acc,
                    self.trainer.progress_bar_metrics.get("max_val_acc", 0.0),
                )

        metrics[f"{event_key}_loss"] = loss.item()
        self.trainer.progress_bar_metrics["loss"] = metrics[f"{event_key}_loss"]
        self.log_dict(metrics)

    def get_loss(self, x, y, batch_idx):
        if hasattr(self.model, "get_output_loss"):
            return self.model.get_output_loss(x, y, self.loss_fn)
        else:
            output = self.model(x)
            loss = self.loss_fn(output, y)
            return output, loss

    def training_step(self, batch, batch_idx):
        _x, _y = batch
        if self.hparams.debug:
            plotting_utils.plot_hor([i.permute(1, 2, 0)
                                    for i in _x[:4].detach().cpu()])
            print(_y[:4])

        if self.hparams.task == "multiclass":
            if self.trainer.datamodule.has_mixed_based_aug():
                aug_result = self.trainer.datamodule.mixed_based_transform(
                    _x, _y)
                _x, _y = self.trainer.datamodule.get_x_y_from_mixed_based_result(
                    aug_result)
                output = self.model(_x)
                loss = self.trainer.datamodule.get_loss_from_mixed_based_result(
                    output, aug_result, self.loss_fn)
            else:
                output, loss = self.get_loss(_x, _y, batch_idx)
        if self.hparams.task == "image-captioning":
            output, loss = self.model.get_output_loss(_x, _y, self.loss_fn)

        if self.hparams.debug:
            plotting_utils.plot_hor([i.permute(1, 2, 0)
                                    for i in _x[:4].detach().cpu()])
            print(_y[:4])

        self.eval_metrics("train", batch, batch_idx, output, loss)
        return loss

    def test_step(self, batch, batch_idx):
        self.eval_metrics("test", batch, batch_idx, *
                          self.get_loss(*batch, batch_idx))

    def validation_step(self, batch, batch_idx):
        self.eval_metrics("val", batch, batch_idx, *
                          self.get_loss(*batch, batch_idx))

    def configure_optimizers(self):

        params = self.model.parameters()

        self.optimizer = getattr(torch.optim, self.hparams.optimizer_key)(
            params, **self.hparams.optimizer_hparams
        )

        if self.hparams.lr_scheduler_key is not None:
            self.lr_scheduler = getattr(
                torch.optim.lr_scheduler, self.hparams.lr_scheduler_key
            )(self.optimizer, **self.hparams.lr_scheduler_hparams)
            # https://lightning.ai/docs/pytorch/stable/api/lightning.pytorch.core.LightningModule.html#lightning.pytorch.core.LightningModule.configure_optimizers
            return dict(
                optimizer=self.optimizer,
                lr_scheduler=dict(scheduler=self.lr_scheduler,
                                  name="lr_scheduler"),
            )
        else:
            return self.optimizer

    def on_validation_end(self) -> None:
        if self.hparams.task == "multiclass":
            target_names = [str(i)
                            for i in range(self.hparams.output_features)]
            self.cr = classification_report(
                self.y_true,
                self.y_pred,
                target_names=target_names,
                output_dict=True,
                labels=[i for i in range(self.hparams.output_features)],
                zero_division=1
            )
            self.crp = classification_report(
                self.y_true,
                self.y_pred,
                target_names=target_names,
                labels=[i for i in range(self.hparams.output_features)],
                zero_division=1
            )
            cm = confusion_matrix(self.y_true, self.y_pred)
            self.cm = cm

    # https://arxiv.org/pdf/1910.09217
    def classifer_retrian_setup(self):
        pass
