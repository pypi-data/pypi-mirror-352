import csv
import shutil
import time
import multiprocessing
import json
from typing import Callable, List
import requests
import os
from tinydb import TinyDB
import torch.multiprocessing
import traceback
import glob
import json

import pandas as pd

from .utils.system_utils import getCurrentCommitHash, getSystemInfo

from expiringdict import ExpiringDict

from .constant import *
from .task_manager import TaskComponent
from .task_func import task_execution_wrapper
from .model_training import (
    train,
    predict
)
from .xai_sdk import (
    get_configurations_and_exp_exp_default_root_dir
)
from .utils.module_utils import (
    load_module
)


class TaskExecutor(TaskComponent):

    # TODO: executor process db
    def __init__(self, component_path: str, mongo=False) -> None:
        self.component_path = component_path
        os.environ["COMPONENT_ROOT_PATH"] = os.path.dirname(
            self.component_path)
        component_config_path = os.path.join(
            os.environ["COMPONENT_ROOT_PATH"], "config.json")

        if not os.path.exists(component_config_path):
            print("Please provide the", component_config_path)
            exit(1)

        with open(component_config_path) as f:
            self.component_info = json.load(f)['executor_info']

        super().__init__(
            self.component_info['executor_name'],
            component_path,
            f"/{self.component_info['executor_name'].lower()}",
            mongo
        )

        self.process_holder = {}

        self.db = TinyDB(self.executor_db_file_path)
        self.executor_reg_info_tb = self.db.table('executor_info')

        # this keep the task and function mapping in memory
        self.task_func_map = {}
        self.em_tracker = {}

        self.task_execution_cache = ExpiringDict(
            max_len=1000, max_age_seconds=600)

        def remove_task_results(task_ticket, sec='logs'):
            dir = os.path.join(
                os.environ['COMPONENT_STATIC_PATH'], sec, task_ticket)
            if os.path.exists(dir):
                print(f"Removing {dir} for {task_ticket}.")
                shutil.rmtree(dir)

        self.cfs = []
        if self.component_info[ExecutorRegInfo.executor_type] == ExecutorType.model:
            print("A default training function is set to this sevice.")
            self.task_func_map['training'] = train.training
            self.task_func_map['predict'] = predict.predict

            def clean_traininig_save(task_ticket):
                remove_task_results(task_ticket)

                # remove training save
                rs_dir = None
                for path, dirs, files in os.walk(
                    os.path.join(
                        os.environ['COMPONENT_STORAGE_PATH'], 'training_save')
                ):
                    if task_ticket in dirs:
                        rs_dir = os.path.join(path, task_ticket)
                if rs_dir is not None:
                    shutil.rmtree(rs_dir)

            self.cfs.append(clean_traininig_save)
        elif self.component_info[ExecutorRegInfo.executor_type] == ExecutorType.model_evaluation:
            # print("A default model evaluation function is set to this sevice.")
            # self.task_func_map['default_eval'] = eval.eval

            self.load_task_func_from_file("eval", "_eval")

            def clean_model_evaluation_save(task_ticket):
                remove_task_results(task_ticket)

            self.cfs.append(clean_model_evaluation_save)

        elif self.component_info[ExecutorRegInfo.executor_type] == ExecutorType.xai:
            self.load_task_func_from_file("xai", "_xai")

        elif self.component_info[ExecutorRegInfo.executor_type] == ExecutorType.xai_evaluation:
            self.load_task_func_from_file("xai_eval", "_xai_eval")

    def load_task_func_from_file(self, py_file_name, task_func_postfix):
        ls = [os.path.join(os.environ['COMPONENT_ROOT_PATH'], py_file) for py_file in os.listdir(
            os.environ['COMPONENT_ROOT_PATH']) if py_file.endswith(f"{py_file_name}.py")]
        for py_file in ls:
            module = load_module(f"_custom_{py_file_name}", py_file)

            rs = [obj for obj in vars(module).values() if callable(
                obj) and obj.__name__ .endswith(task_func_postfix)]

            for obj in rs:
                print(f"Register custom function {obj.__name__}, {obj}")
                self.task_func_map[obj.__name__] = dict(
                    method_module_path=py_file,
                    method_name=obj.__name__
                )
            if len(rs) == 0:
                print(
                    f"No task func with postfix {task_func_postfix} in {py_file}.")
        if len(ls) == 0:
            print("No module in", os.environ['COMPONENT_ROOT_PATH'])

    def get_exp_rs_path(self, task_ticket):
        task_execution = self.get_task_execution_from_central(task_ticket)
        if task_execution[TaskExecution.task_type] == TaskType.training:
            datamodule_class, datamodule_cfg, model_cfg, trainer_cfg, no_train, exp_default_root_dir = \
                get_configurations_and_exp_exp_default_root_dir(
                    self.get_publisher_endpoint_url(), task_execution[TaskExecution.task_parameters])

            ticket_path = os.path.join(
                exp_default_root_dir, "lightning_logs", task_ticket)
            v0_path = os.path.join(exp_default_root_dir,
                                   "lightning_logs", "v_0")

            return ticket_path if os.path.exists(ticket_path) else v0_path
        else:
            return os.path.join(self.static_path, "rs", task_ticket)

    def get_executor_info(self):
        executor_reg_info = self.executor_reg_info_tb.all()
        if len(executor_reg_info) > 0:
            return executor_reg_info[0][ExecutorRegInfo.executor_info]
        return

    def get_publisher_endpoint_url(self) -> str:
        executor_reg_info = self.executor_reg_info_tb.all()
        if len(executor_reg_info) > 0:
            return executor_reg_info[0][ExecutorRegInfo.publisher_endpoint_url]
        return ""

    def get_executor_id(self):
        executor_reg_info = self.executor_reg_info_tb.all()
        if len(executor_reg_info) > 0:
            return executor_reg_info[0][ExecutorRegInfo.executor_id]
        return

    # should register executor to publisher
    def keep_reg_info(self, executor_id,  executor_name, executor_type: str, executor_endpoint_url: str, executor_info, publisher_endpoint_url: str, **kwargs):
        executor_reg_info = self.executor_reg_info_tb.all()
        if len(executor_reg_info) > 0:
            # remove existing reg info
            # one service instance, one record in reg info db
            self.executor_reg_info_tb.truncate()

        self.executor_reg_info_tb.insert({
            ExecutorRegInfo.executor_id: executor_id,
            ExecutorRegInfo.executor_name: executor_name,
            ExecutorRegInfo.executor_type: executor_type,
            ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
            ExecutorRegInfo.executor_info: json.loads(executor_info),
            ExecutorRegInfo.publisher_endpoint_url: publisher_endpoint_url,
        })

        return getSystemInfo()

    def update_task_status_to_central(
            self, task_ticket, task_status, running_info={}, pipeline_ticket=None):

        task_result_save_path = os.path.join(
            self.tmp_path, 'rs', task_ticket)

        task_tmp_save_path = os.path.join(
            self.tmp_path, task_ticket)

        if os.path.exists(task_result_save_path):
            files = []
            for filename in glob.iglob(task_result_save_path + '**/**', recursive=True):
                if os.path.isfile(filename):
                    just_file_name = filename.replace(
                        os.path.join(self.tmp_path, 'rs') + '/', '')
                    files.append((
                        'samples', (just_file_name, open(
                            filename, 'rb'), 'application/octet-stream')
                    ))

            resp = requests.post(
                self.get_publisher_endpoint_url() + '/task_publisher/az_blob',
                data={
                    'act': 'upload',
                    'data_set_name': 'task_execution',
                    'data_set_group_name': 'result',
                },
                files=files
            )

            if resp.status_code == 200:
                shutil.rmtree(task_result_save_path)
                if os.path.exists(task_tmp_save_path):
                    shutil.rmtree(task_tmp_save_path)

        emission_file = os.path.join(self.storage_path, 'emissions.csv')
        if os.path.exists(emission_file):
            emissions = pd.read_csv(emission_file)
            emission_info = emissions.loc[emissions['project_name'] == task_ticket].to_dict(
                'records')

            if len(emission_info) > 0:
                running_info['emission_info'] = emission_info[0]

        print(
            f"Update status of {task_ticket} as {task_status}, in pipeline_execution: {pipeline_ticket}")

        d = {
            'act': 'update_task_status',
            TaskExecution.task_ticket: task_ticket,
            TaskExecution.task_status: task_status,
            TaskExecution.running_info: json.dumps(running_info),
            PipelineExecution.pipeline_ticket: pipeline_ticket,
            # TaskExecution.code_version_hash: getCurrentCommitHash()
        }
        print(d)
        status_update_resp = requests.post(
            self.get_publisher_endpoint_url() + '/task_publisher/task_execution',
            data=d)
        print("Update status response:")
        print(status_update_resp.status_code)
        print(status_update_resp.content)

    def execution_call_back(self, output_and_status, task_ticket, pipeline_ticket, process):
        process.close()
        self.update_task_status_to_central(
            task_ticket, output_and_status[TaskExecution.task_status],
            running_info={
                TaskExecution.task_execution_std_output_str: output_and_status[TaskExecution.task_execution_std_output_str],
                TaskExecution.task_execution_std_error_str: output_and_status[TaskExecution.task_execution_std_error_str],
            },
            pipeline_ticket=pipeline_ticket
        )

    def error_call_back(self, err, task_ticket, pipeline_ticket, process):
        # this may never be called since we handler the error in task_func.py
        process.close()
        print(f'Error occurs for task_ticket: ' + task_ticket)
        error_stack_tracking = ''.join(
            traceback.TracebackException.from_exception(err).format())
        print(error_stack_tracking)
        self.update_task_status_to_central(task_ticket, TaskStatus.error, {
            'error_stack_tracking': error_stack_tracking
        }, pipeline_ticket=pipeline_ticket)

    def __file_present__(self, rs_files, task_ticket, scope, sample=None):
        pre = []
        for rs_file in rs_files:
            ext = rs_file.split('.')[-1].lower()
            if ext in ['png', 'jpeg']:
                pre.append({
                    'file_name': rs_file,
                    'address': f'/static/rs/{task_ticket}/{scope}/{rs_file}',
                    'file_type': 'img'
                })
            elif ext in ['npy']:
                pre.append({
                    'file_name': rs_file,
                    'address': f'/static/rs/{task_ticket}/{scope}/{rs_file}',
                    'file_type': 'npy',
                    'content': 'todo'
                })
        return pre

    def get_task_rs_presentation(self, task_ticket):
        task_execution = self.get_task_execution_from_central(task_ticket)
        if task_execution[TaskExecution.task_type] == TaskType.model_evaluation:
            # create a dictionary
            data = []

            csv_path = os.path.join(
                os.environ['COMPONENT_STATIC_PATH'],
                "rs",
                task_ticket,
                "metrics.csv"
            )
            if os.path.exists(csv_path):
                with open(csv_path, encoding='utf-8') as csvf:
                    csvReader = csv.DictReader(csvf)

                    # Convert each row into a dictionary
                    # and add it to data
                    for rows in csvReader:

                        # Assuming a column named 'No' to
                        # be the primary key
                        key = rows['epoch']
                        data.append(rows)

                return data

        return None

    def start_a_task(self, task_execution, pipeline_ticket):

        task_status = task_execution[TaskExecution.task_status]
        task_ticket = task_execution[TaskExecution.task_ticket]

        if task_status == TaskStatus.finished:
            # if the task is finished already, directly pass down the status
            self.update_task_status_to_central(
                task_ticket, task_status,
                running_info={
                    TaskExecution.task_execution_std_output_str: f"Task {task_ticket} is finished already.",
                },
                pipeline_ticket=pipeline_ticket
            )
        else:
            task_function_key = task_execution[TaskExecution.task_function_key]
            task_parameters = task_execution[TaskExecution.task_parameters]

            task_parameters[TaskExecution.previous_task_ticket] = task_execution.get(
                TaskExecution.previous_task_ticket)
            task_parameters[TaskExecution.next_task_ticket] = task_execution.get(
                TaskExecution.next_task_ticket)

            use_pytorch_multiprocess = False
            if task_parameters.get('executor_config') is not None:
                if task_parameters.get('executor_config').get('use_pytorch_multiprocess') is not None:
                    use_pytorch_multiprocess = True

            if use_pytorch_multiprocess:
                try:
                    torch.multiprocessing.set_start_method('spawn', force=True)
                except RuntimeError:
                    traceback.print_exc()
                process = torch.multiprocessing.Pool(processes=1)
            else:
                try:
                    # fork will not reload the task module

                    # in macOS, you should set the following two env before running the flask
                    # os.environ["no_proxy"] = "*"
                    # os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
                    # like:
                    # export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES; export no_proxy='*'; flask ...
                    # multiprocessing.set_start_method('fork', force=True)

                    multiprocessing.set_start_method('spawn', force=True)
                except RuntimeError:
                    traceback.print_exc()
                process = multiprocessing.Pool(processes=1)

            args = [
                self.task_func_map,
                task_function_key,
                os.path.join(self.storage_path),
                task_ticket, self.get_publisher_endpoint_url(),
                task_parameters
            ]
            as_rs = process.apply_async(
                task_execution_wrapper,
                args=args,
                callback=lambda output_and_status: self.execution_call_back(
                    output_and_status, task_ticket, pipeline_ticket, process),
                error_callback=lambda err: self.error_call_back(
                    err, task_ticket, pipeline_ticket, process)
            )
            st = time.time()

            self.process_holder[task_ticket] = {
                'start_time': st,
                'process': process,
                'as_rs': as_rs
            }

        return task_ticket

    def get_task_actual_staus(self, task_ticket):
        if self.process_holder.get(task_ticket) == None:
            return TaskStatus.not_exist_in_executor_process_holder
        else:
            rs = self.process_holder.get(task_ticket)
            as_rs = rs['as_rs']

            # for ready()
            # false when task is running
            # true when task is done

            # for successful()
            # raise error when task is running
            # true when task is done and not error raised
            # false when task is done and error raised
            if as_rs.ready():
                return TaskStatus.finished if as_rs.successful() else TaskStatus.error
            else:
                return TaskStatus.running

    # set cleaning function when terminating a task

    def set_clean_task_function(self, cfs: List[Callable[[str], None]] | Callable[[str], None]):
        if isinstance(cfs, list):
            self.cfs.extend(cfs)
        else:
            self.cfs.append(cfs)
        return self

    def clean_task_result(self, task_ticket):
        try:
            for cf in self.cfs:
                cf(task_ticket)
        except Exception:
            print('clean function error ', task_ticket)
            traceback.print_exc()

    def terminate_process(self, task_ticket):
        print(f'Teriminating [{task_ticket}] of pid')
        current_p = multiprocessing.current_process()
        target_p = self.process_holder.get(task_ticket)
        print(f"Current Pid: {current_p.pid}.")
        if target_p != None:
            print(f"\tterminating: {target_p['process']}.")
            self.update_task_status_to_central(
                task_ticket, TaskStatus.stopping)
            target_p['process'].terminate()
            # join to prevent termination hanging
            target_p['process'].join()
            print("Terminated.")
        self.update_task_status_to_central(task_ticket, TaskStatus.stopped)
        self.clean_task_result(task_ticket)

    def get_task_execution_from_central(self, target_ticket: str):
        cached_task_execution = self.task_execution_cache.get(target_ticket)
        if self.get_publisher_endpoint_url() == None or self.get_executor_id() == None:
            print('Executor not register')
            return None
        else:
            task_execution = None
            if cached_task_execution is None:
                response = requests.get(
                    self.get_publisher_endpoint_url() + '/task_publisher/task_execution',
                    params={
                        TaskExecution.task_ticket: target_ticket,
                    }
                )
                task_execution = json.loads(response.content)
                self.task_execution_cache[target_ticket] = task_execution
            else:
                task_execution = cached_task_execution
            return task_execution

    def define_task_func_map(self, key, func):
        self.task_func_map[key] = func
        return self

    def delete_the_task(self, task_ticket):
        task_rs_path = os.path.join(self.static_path, 'rs', task_ticket)
        if os.path.exists(task_rs_path):
            shutil.rmtree(task_rs_path)

        task_rs_zip_path = os.path.join(
            self.static_path, 'rs', f'{task_ticket}.zip')
        if os.path.exists(task_rs_zip_path):
            os.remove(task_rs_zip_path)

        task_execution_std_out_err_path = os.path.join(
            self.static_path, task_ticket
        )
        if os.path.exists(task_execution_std_out_err_path):
            shutil.rmtree(task_execution_std_out_err_path)

        self.clean_task_result(task_ticket)

    def reset(self):
        self.executor_reg_info_tb.truncate()

        # remove all files in tmp
        shutil.rmtree(self.tmp_path)
        # remove all files in static/rs
        shutil.rmtree(os.path.join(self.static_path, 'rs'))

        os.mkdir(self.tmp_path)
        os.mkdir(os.path.join(self.static_path, 'rs'))
