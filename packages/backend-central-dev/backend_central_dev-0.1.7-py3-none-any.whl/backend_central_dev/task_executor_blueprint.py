import subprocess
import threading
import time
from dotenv import dotenv_values
import glob
import os
import sys
import json
import shutil
from flask import Blueprint, request, jsonify, send_file, Flask, abort

from .utils.system_utils import getCurrentCommitHash
from .task_executor import TaskExecutor
from .constant import ExecutorRegInfo, TaskExecution, ExecutorType

from .xai_sdk import *

from flask_cors import CORS


def create_tmp_dir(service_init_path):
    basedir = os.path.abspath(os.path.dirname(service_init_path))
    tmpdir = os.path.join(basedir, "tmp")
    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir)


def load_env(mode, **kwargs):
    os.environ["ENV"] = mode
    print("CWD:", os.getcwd())
    print("App Mode: ", os.environ["ENV"])
    env_file = os.path.join(os.getcwd(), f".env.{os.environ['ENV']}")

    for k, v in kwargs.items():
        os.environ[k] = v

    print("Env file: ", env_file)
    config = dotenv_values(env_file)
    for k in config.keys():
        if os.getenv(k) == None:
            os.environ[k] = config[k]


def set_app(app: Flask):
    # cors
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.static_folder = os.environ['COMPONENT_STATIC_PATH']


class ExecutorBluePrint(Blueprint):

    def __init__(
        self, init_file_name, component_path, *args, mongo=False, **kwargs
    ) -> None:
        print(sys.argv)
        if not sys.argv[0].endswith("flask"):
            self.app = 'dummy'
            print("Not in flask environment, skip the initialization, please use the 'flask --app ...' command to start the service")
            return
        load_env(os.environ.get("ENV", "dev"))

        self.te = TaskExecutor(
            component_path=component_path,
            mongo=mongo,
        )

        super().__init__(
            self.te.component_name,
            init_file_name,
            url_prefix=os.environ['CONTEXT_PATH'],
            *args, **kwargs
        )

        self.tmp_path = self.te.tmp_path

        @self.route("/reset", methods=["GET"])
        def reset():
            self.te.reset()
            return ""

        @self.route("/register_to_central", methods=["POST"])
        def register_to_central():
            if request.method == "POST":
                data = request.json
                central_url = data["central_url"]
                service_url = data["service_url"]
                self.publisher_endpoint_url = f"{central_url}"
                self.te.component_info[ExecutorRegInfo.executor_endpoint_url] = service_url + \
                    os.environ['CONTEXT_PATH']
                return register_executor(central_url, **self.te.component_info)

        @self.route("/get_available_task_function_key", methods=["GET"])
        def available_task_function_key():
            return jsonify(list(self.te.task_func_map.keys()))

        @self.route("/task_execution_result", methods=["GET"])
        def task_result():
            if request.method == "GET":
                task_ticket = request.args["task_ticket"]

                exp_rs_path = self.te.get_exp_rs_path(task_ticket)
                zip_path = os.path.join(
                    self.te.static_path, "rs", f"{task_ticket}.zip")

                if not os.path.exists(zip_path):
                    shutil.make_archive(
                        zip_path.replace('.zip', ''),
                        "zip",
                        exp_rs_path,
                    )

                if os.path.exists(zip_path):
                    return send_file(zip_path, as_attachment=True)
                else:
                    # TODO: should follow the restful specification
                    return "no such task"

        @self.route("/task_result_present", methods=["GET"])
        def task_result_present():
            if request.method == "GET":
                task_ticket = request.args["task_ticket"]
                pre = self.te.get_task_rs_presentation(task_ticket)
                return jsonify(pre)
            return ""

        @self.route("/task_status", methods=["GET", "POST"])
        def task_status():
            if request.method == "GET":
                task_ticket = request.args["task_ticket"]
                return jsonify(
                    {TaskExecution.task_status: self.te.get_task_actual_staus(
                        task_ticket)}
                )

        @self.route("/task_execution", methods=["GET", "POST"])
        def task():
            if request.method == "GET":
                pass
            else:
                form_data = request.form
                act = form_data["act"]
                # stop a task
                if act == "stop":
                    task_ticket = form_data[TaskExecution.task_ticket]
                    self.te.terminate_process(task_ticket)

                # execute a task which assigned by the central
                if act == "execute":
                    task_execution = json.loads(form_data["task_execution"])
                    pipeline_ticket = form_data.get("pipeline_ticket")
                    self.te.start_a_task(task_execution, pipeline_ticket)

                if act == "delete":
                    task_ticket = form_data[TaskExecution.task_ticket]
                    self.te.delete_the_task(task_ticket)

                if act == "run_sync":
                    task_function_key = form_data[TaskSheet.task_function_key]
                    task_parameters = json.loads(
                        form_data[TaskExecution.task_parameters])
                    task_parameters['request'] = request
                    task_parameters['run_mode'] = "run_sync"
                    publisher_endpoint_url = self.te.get_publisher_endpoint_url()
                    return jsonify(get_task_function(self.te.task_func_map, task_function_key)(
                        None,
                        publisher_endpoint_url,
                        task_parameters
                    ))

            return ""

        @self.route("/executor", methods=["POST"])
        def exe():
            if request.method == "POST":
                # register executor
                form_data = request.form
                act = form_data["act"]
                if act == "reg" or act == "update":
                    executor_id = form_data[ExecutorRegInfo.executor_id]
                    executor_name = form_data[ExecutorRegInfo.executor_name]
                    endpoint_type = form_data[ExecutorRegInfo.executor_type]
                    endpoint_url = form_data[ExecutorRegInfo.executor_endpoint_url]
                    executor_info = form_data[ExecutorRegInfo.executor_info]
                    sys_info = self.te.keep_reg_info(
                        executor_id,
                        executor_name,
                        endpoint_type,
                        endpoint_url,
                        executor_info,
                        self.publisher_endpoint_url,
                    )
                    return jsonify(sys_info)

            return ""

        if self.te.component_info['executor_type'] == ExecutorType.dataset:
            @self.route("/dataset_source_file", methods=['GET'])
            def dataset_source_file():
                dataset_file = os.path.join(
                    self.te.component_path_parent, "dataset.py")
                if os.path.exists(dataset_file):
                    with open(dataset_file) as f:
                        content = f.read()
                        return content
                else:
                    abort(404)

        if self.te.component_info['executor_type'] == ExecutorType.model:
            @self.route("/model_source_file", methods=['GET'])
            def model_source_file():
                dataset_file = os.path.join(
                    self.te.component_path_parent, "model.py")
                if os.path.exists(dataset_file):
                    with open(dataset_file) as f:
                        content = f.read()
                        return content
                else:
                    abort(404)

        self.app = create_service(self)

    def get_task_executor(self):
        return self.te


def create_service(bp: ExecutorBluePrint):

    context_path = os.environ["CONTEXT_PATH"]
    static_url_path = context_path + "/static"

    app = Flask(
        __name__,
        instance_relative_config=True,
        static_url_path=static_url_path
    )

    set_app(app)
    app.register_blueprint(bp)

    bp.te.component_info[ExecutorRegInfo.executor_info]['code_version_hash'] = getCurrentCommitHash()
    print("Current code version hash: ",
          bp.te.component_info[ExecutorRegInfo.executor_info]['code_version_hash'])

    return app
