import os
import importlib.util
from ..model_training.lightning_model import FineTunableModel


def init_object(class_path: str, init_args):
    module_name, class_name = class_path.rsplit(".", 1)

    tran = getattr(importlib.import_module(module_name), class_name)
    if type(init_args) is dict:
        return tran(**init_args)
    if type(init_args) is list:
        args = []
        for a in init_args:
            if type(a) is dict and a.get("class_path") is not None:
                args.append(init_object(a["class_path"], a["init_args"]))
            else:
                args.append(a)
        return tran(args)


def load_module(module_name, module_file_path):
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        spec = importlib.util.spec_from_file_location(
            module_name, module_file_path)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # print(f"Load module {module_name} from {module_file_path}")
    print(f"Load module {module_name}")
    return module


def get_model_module(model_module_file_path=None):
    if model_module_file_path is None:
        model_module_file_path = os.path.join(
            os.environ['COMPONENT_ROOT_PATH'], "model.py"
        )
    model_module = load_module("model", model_module_file_path)
    return model_module


def get_fine_tunable_model_from_model_module_file(model_module_file_path=None):
    model_module = get_model_module(model_module_file_path)
    return FineTunableModel(
        model_init_func=model_module.model_init_func,
        model_fine_tune_func=model_module.model_fine_tune_func
    )


def filter_form_data_params_by_module(form, module):
    return {k: v for k, v in form.items() if k in dir(module)}


def init_callbacks_for_trainer_config(trainer_configuration):
    callbacks = []
    if trainer_configuration.get("callbacks") is not None:
        for callback_config in trainer_configuration.get("callbacks"):
            callback = init_object(
                callback_config["class_path"], callback_config["init_args"]
            )
            callbacks.append(callback)

    trainer_configuration["callbacks"] = callbacks
    return trainer_configuration


def get_task_function(task_func_map, task_function_key):
    task_func = task_func_map[task_function_key]
    # load task func by file path
    if type(task_func) is dict:
        module = load_module(
            "custom_eval", task_func['method_module_path'])
        print(
            # f"Loading function {task_func['method_name']} to execute from {task_func['method_module_path']}")
            f"Loading function {task_func['method_name']}")
        task_func = getattr(module, task_func['method_name'])

    return task_func
