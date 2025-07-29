from PIL import Image
from backend_central_dev.constant import *
from backend_central_dev.utils.pytorch_utils import get_device
import lightning as L
from backend_central_dev.utils.data_utils import get_tensor_from_flask_file_storage
import sys
import os

from matplotlib import pyplot as plt
import numpy as np
import torchvision.transforms as T

from ..xai_sdk import get_trained_model_and_dataset_from_services

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


def task_wrapper(task_ticket, publisher_endpoint_url, task_parameters, xai_func):
    L.seed_everything(42)
    run_mode = task_parameters.get('run_mode', None)
    if run_mode == 'run_sync':
        model_training_execution_ticket = task_parameters[TaskExecution.previous_task_ticket]
        request = task_parameters['request']
        image = request.files['image']

        model, datamodule = get_trained_model_and_dataset_from_services(
            publisher_endpoint_url,
            task_parameters[TaskExecution.previous_task_ticket],
            task_parameters
        )

        image_tensor, image_save_path = get_tensor_from_flask_file_storage(
            model_training_execution_ticket, image, datamodule)

        try:
            os.remove(image_save_path)
        except OSError:
            pass

        device = get_device()
        map = xai_func(
            model.to(device), image_tensor.to(device), None,
            **task_parameters.get('xai_parameters', {})
        ).detach().cpu().numpy()[0]

        map_save_name = f"gag_xai_{model_training_execution_ticket}_{image.filename.replace('.jpg', '.png')}"
        map_save_path = os.path.join(
            os.environ["COMPONENT_STATIC_PATH"],
            "explanation",
            map_save_name
        )

        os.makedirs(os.path.dirname(map_save_path), exist_ok=True)

        cm = plt.get_cmap('turbo')
        map = cm(map)
        img = Image.fromarray((map * 255).astype(np.uint8), mode="RGBA")

        # img.putalpha(int(255 * 0.4))
        img.save(map_save_path)

        # original_img = T.ToPILImage()(image_tensor[0]).convert(mode="RGBA")
        # original_img.paste(img, (0, 0), mask=img)

        # original_img.save(map_save_path)
        return {
            "explanation_filename": map_save_name
        }
    else:
        print(task_parameters)
        ...
