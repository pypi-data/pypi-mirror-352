
import shutil
from ..constant import *
from ..xai_sdk import (
    get_lightning_model,
    get_configurations_and_exp_exp_default_root_dir
)

import lightning as L
from lightning.pytorch.loggers import TensorBoardLogger
from lightning.pytorch.callbacks import LearningRateMonitor, RichProgressBar, ModelCheckpoint

import os


def training(task_ticket, publisher_endpoint_url, task_parameters):
    L.seed_everything(42)

    datamodule_class, datamodule_cfg, model_cfg, trainer_cfg, no_train, exp_default_root_dir = \
        get_configurations_and_exp_exp_default_root_dir(
            publisher_endpoint_url, task_parameters)

    logs_dir = os.path.join(exp_default_root_dir, "lightning_logs")

    # copy existing exp result
    exps_dir_0 = os.path.join(logs_dir, 'v_0').replace('training_save', 'exps')
    exps_dir_1 = os.path.join(logs_dir, 'v_1').replace('training_save', 'exps')
    if os.path.exists(exps_dir_0):
        shutil.copytree(exps_dir_0, os.path.join(logs_dir, task_ticket))
    elif os.path.exists(exps_dir_1):
        shutil.copytree(exps_dir_1, os.path.join(logs_dir, task_ticket))
    else:
        datamodule = datamodule_class(**datamodule_cfg)

        model = get_lightning_model(model_cfg, datamodule)

        versions = task_ticket
        # trainer_cfg['max_epochs'] = 1

        trainer = L.Trainer(
            precision='16-mixed',
            default_root_dir=exp_default_root_dir,
            logger=TensorBoardLogger(
                exp_default_root_dir, version=versions),
            # fast_dev_run=True,
            **trainer_cfg
        )

        trainer.callbacks = [
            RichProgressBar(),
            *trainer.callbacks,
            LearningRateMonitor(logging_interval="epoch")
        ]

        if not no_train:
            # train the model
            trainer.fit(model, datamodule=datamodule)
