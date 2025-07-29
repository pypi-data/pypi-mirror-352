import json
import multiprocessing
import traceback
from codecarbon import EmissionsTracker

from .utils.module_utils import get_task_function
from .constant import (
    TaskExecution,
    TaskStatus
)
import sys
import os
import io
import time

import os


def task_execution_wrapper(
    task_func_map, task_function_key,
    output_dir, task_ticket,
    publisher_endpoint_url,
    task_parameters
):
    # Get the current user's username
    # current_user = os.getlogin()
    p = multiprocessing.current_process()
    task_execution_info = dict(
        task_ticket=task_ticket,
        task_function_key=task_function_key,
        task_parameters=task_parameters,
        publisher_endpoint_url=publisher_endpoint_url,
        # current_user=current_user,
        pid=p.pid
    )
    print(json.dumps(task_execution_info, indent=4))

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    ticket_log_dir = os.path.join(
        os.environ['COMPONENT_STATIC_PATH'], "logs", task_ticket)
    os.makedirs(ticket_log_dir, exist_ok=True)

    std_out_file_path = os.path.join(
        ticket_log_dir, f"out.log")
    std_err_file_path = os.path.join(
        ticket_log_dir, f"err.log")
    std_out_file = open(std_out_file_path, 'w')
    std_err_file = open(std_err_file_path, 'w')

    # print(f"Output emission log to: {output_dir}")
    # tracker = EmissionsTracker(
    #     project_name=task_ticket,
    #     tracking_mode='process',
    #     output_dir=output_dir,
    #     log_level='critical',
    #     # allow_multiple_runs=True
    # )
    # tracker.start()
    try:
        sys.stdout = std_out_file
        sys.stderr = std_err_file
        task_func = get_task_function(task_func_map, task_function_key)

        status = task_func(
            task_ticket, publisher_endpoint_url, task_parameters)
        if status is None:
            status = TaskStatus.finished
    except Exception as e:
        print(''.join(
            traceback.TracebackException.from_exception(e).format()),
            file=sys.stderr)
        status = TaskStatus.error
        # raise e
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        std_out_file.close()
        std_err_file.close()
        with open(std_out_file_path) as f:
            std_output_str = f.readlines()
        with open(std_err_file_path) as f:
            std_error_str = f.readlines()
        # tracker.stop()
    return {
        TaskExecution.task_status: status,
        TaskExecution.task_execution_std_output_str: std_output_str,
        TaskExecution.task_execution_std_error_str: std_error_str
    }
