import sys
import time
import os
import json
import requests
from tinydb import TinyDB
import re
from backend_central_dev.task_manager import TaskComponent, __get_random_string__, __get_random_string_no_low__
from backend_central_dev.constant import *
from backend_central_dev.entity.WsMessage import *
import websockets


class TaskPublisher(TaskComponent):

    def __init__(self, publisher_name: str, component_path: str, import_name: str, context_path: str, mongo=True) -> None:

        super().__init__(publisher_name, component_path,
                         context_path=context_path, mongo=mongo)
        self.publisher_name = publisher_name
        self.import_name = import_name

        self.task_pipeline_manager = TaskAndPipelineManager(self)
        self.pipeline_execution_result_streaming = {}

        # self.az = AZ()

        # ANCHOR: makeup code, will be removed when stable
        if "routes" == sys.argv[-1]:
            return
        pipeline_executions = self.mondb.find(Mongo.pipeline_execution_col, {})
        pipeline_execution_count = {}
        for pipeline_execution in pipeline_executions:
            if pipeline_execution_count.get(pipeline_execution[PipelineExecution.pipeline_sheet_id]) == None:
                pipeline_execution_count[pipeline_execution[PipelineExecution.pipeline_sheet_id]] = 0
            pipeline_execution_count[pipeline_execution[PipelineExecution.pipeline_sheet_id]] += 1
            if pipeline_execution.get(PipelineExecution.pipeline_execution_name) == None:
                new_name = pipeline_execution[PipelineExecution.pipeline_sheet_name] + '-#' + str(pipeline_execution_count.get(
                    pipeline_execution[PipelineExecution.pipeline_sheet_id]))
                self.mondb.update_one(Mongo.pipeline_execution_col, {
                    PipelineExecution.pipeline_ticket: pipeline_execution[
                        PipelineExecution.pipeline_ticket]
                }, {
                    "$set": {
                        PipelineExecution.pipeline_execution_name: new_name
                    }
                })

        tasks = self.mondb.find(Mongo.task_execution_col, {})
        for task in tasks:
            if task.get(TaskExecution.task_sheet_name) == None:
                task_sheet = self.mondb.find_one(Mongo.task_sheet_col, {
                    TaskSheet.task_sheet_id: task[TaskExecution.task_sheet_id]
                })

                self.mondb.update_one(Mongo.task_execution_col, {
                    TaskExecution.task_ticket: task[TaskExecution.task_ticket]
                }, {
                    "$set": {
                        TaskExecution.task_sheet_name: task_sheet[TaskSheet.task_sheet_name]
                    }
                })

    def get_executor_registration_info(self, executor_id=None):
        if executor_id == None:
            return self.mondb.find(
                Mongo.executor_registration_col, {})
        else:
            return self.mondb.find_one(
                Mongo.executor_registration_col, {ExecutorRegInfo.executor_id: executor_id})

    def remove_task_ticket(self, executor_id, task_ticket):
        pass

    def generate_pipeline_execution_from_pipeline_sheet_and_task_execution(self, pipeline_sheet, task_execution_tickets):

        pipeline_executions = self.mondb.find(Mongo.pipeline_execution_col, {
            PipelineExecution.pipeline_sheet_id: pipeline_sheet[PipelineSheet.pipeline_sheet_id]
        })

        new_pipeline_execution_name = pipeline_sheet[PipelineSheet.pipeline_sheet_name] + \
            '-#' + str(len(pipeline_executions))

        pipeline_execution_ticket_info = {
            PipelineExecution.pipeline_sheet_id: pipeline_sheet[PipelineSheet.pipeline_sheet_id],
            PipelineExecution.pipeline_type: pipeline_sheet[PipelineSheet.pipeline_type],
            PipelineExecution.create_at: time.time(),
            PipelineExecution.pipeline_sheet_name: pipeline_sheet[PipelineSheet.pipeline_sheet_name],
            PipelineExecution.pipeline_execution_name: new_pipeline_execution_name,
            PipelineExecution.pipeline_ticket:  __get_random_string__(
                4) + '.' + __get_random_string_no_low__(
                4) + '.' + pipeline_sheet[PipelineSheet.pipeline_sheet_id],
            PipelineExecution.task_execution_tickets: task_execution_tickets
        }

        self.mondb.insert_one(Mongo.pipeline_execution_col,
                              pipeline_execution_ticket_info)

        return self.mondb.find_one(Mongo.pipeline_execution_col, {
            PipelineExecution.pipeline_ticket: pipeline_execution_ticket_info[
                PipelineExecution.pipeline_ticket]
        })

    def gen_task_execution(
        self, task_sheet, task_execution_name=None
    ):
        if task_execution_name is None:
            tasks_under_this_task_sheet = self.mondb.find(Mongo.task_execution_col, {
                TaskExecution.task_sheet_id: task_sheet[TaskSheet.task_sheet_id]
            })

            task_execution_name = task_sheet[TaskSheet.task_sheet_name] + \
                f"-#{len(tasks_under_this_task_sheet)}"

        task_type = task_sheet[TaskSheet.task_type]
        if task_type == TaskType.xai:
            main_executor_id = task_sheet[TaskSheet.xai_service_executor_id]

        elif task_type == TaskType.xai_evaluation:
            main_executor_id = task_sheet[TaskSheet.xai_evaluation_service_executor_id]

        elif task_type == TaskType.training:
            main_executor_id = task_sheet[TaskSheet.model_service_executor_id]

        elif task_type == TaskType.model_evaluation:
            main_executor_id = task_sheet[TaskSheet.model_evaluation_service_executor_id]

        else:
            # the prediction task does not involve in XAI pipeline_sheet
            pass

        if not self.if_executor_registered(main_executor_id):
            return None
        else:
            task_execution = {
                TaskExecution.task_ticket: __get_random_string__(
                    15) + '.' + main_executor_id,
                TaskExecution.executor_id: main_executor_id,
                TaskExecution.task_status: TaskStatus.initialized,
                TaskExecution.task_execution_name: task_execution_name,
                TaskExecution.publisher: self.publisher_name,

                TaskExecution.task_type: task_sheet[TaskSheet.task_type],
                TaskExecution.task_sheet_id: task_sheet[TaskSheet.task_sheet_id],
                TaskExecution.task_sheet_name: task_sheet[TaskSheet.task_sheet_name],
                TaskExecution.task_function_key: task_sheet[TaskSheet.task_function_key],
                TaskExecution.request_time: time.time(),
                TaskExecution.start_time: TaskExecution.empty,
                TaskExecution.end_time: TaskExecution.empty,
            }

            task_parameters = task_sheet[TaskSheet.task_parameters]
            main_executor_reg_info = self.get_executor_registration_info(
                main_executor_id)

            # fill main executor endpoint url
            task_execution[TaskExecution.executor_endpoint_url] = main_executor_reg_info[ExecutorRegInfo.executor_endpoint_url]

            # fill parameters with all executor url
            for should_be_executor_id_key in dir(TaskSheet):
                if should_be_executor_id_key.endswith('_service_executor_id') and \
                        task_sheet.get(should_be_executor_id_key, None) is not None:
                    service_url_key = should_be_executor_id_key.replace(
                        '_service_executor_id', '_service_url')
                    executor_reg_info = self.get_executor_registration_info(
                        executor_id=task_sheet[should_be_executor_id_key]
                    )
                    if type(executor_reg_info) is not list:
                        task_parameters[service_url_key] = executor_reg_info[ExecutorRegInfo.executor_endpoint_url]

            task_execution[TaskExecution.task_parameters] = task_parameters

            task_execution[TaskExecution.previous_task_ticket] = task_sheet.get(
                TaskSheet.previous_task_ticket)
            task_execution[TaskExecution.next_task_ticket] = task_sheet.get(
                TaskSheet.next_task_ticket)

            self.mondb.insert_one(Mongo.task_execution_col, task_execution)
            return self.mondb.find_one(Mongo.task_execution_col, {
                TaskExecution.task_ticket: task_execution[TaskExecution.task_ticket]
            })

    def ask_executor_task_actual_status(self, task_ticket, executor_endpoint_url):

        response = requests.get(
            executor_endpoint_url +
            '/task_status',
            params={
                TaskExecution.task_ticket: task_ticket,
            }
        )

        rs = json.loads(response.content.decode('utf-8'))

        return rs[TaskExecution.task_status]

    def get_all_task(self):
        return self.mondb.find(Mongo.task_execution_col, {})

    def refresh_task_actual_status(self, task_executions):
        for task in task_executions:
            if task[TaskExecution.task_status] == TaskStatus.running:
                current_acutal_status = self.ask_executor_task_actual_status(
                    task[TaskExecution.task_ticket],
                    task[TaskExecution.executor_endpoint_url]
                )

                if current_acutal_status == TaskStatus.not_exist_in_executor_process_holder:
                    # if the executor is shutdown
                    task[TaskExecution.task_status] = TaskStatus.stopped

                    self.mondb.update_one(Mongo.task_execution_col, {
                        TaskExecution.task_ticket: task[TaskExecution.task_ticket]
                    }, {
                        "$set": {
                            TaskExecution.task_status: task[TaskExecution.task_status]
                        }
                    })
        return task_executions

    def get_task_executions_by_task_sheet_id(self, task_sheet_id):
        task_executions = self.mondb.find(Mongo.task_execution_col, {
            TaskExecution.task_sheet_id: task_sheet_id
        })

        return self.refresh_task_actual_status(task_executions)

    def get_task_executions_by_executor_id_and_task_type(self, executor_id, task_type):

        # print(executor_id, task_type)
        task_executions = self.mondb.find(Mongo.task_execution_col, {
            TaskExecution.executor_id: executor_id,
            TaskExecution.task_type: task_type
        })
        # print(task_executions)

        return self.refresh_task_actual_status(task_executions)

    def get_task_execution(self, task_ticket: str):
        if task_ticket == None:
            return self.mondb.find(Mongo.task_execution_col, {})
        else:
            return self.mondb.find_one(Mongo.task_execution_col, {
                TaskExecution.task_ticket: task_ticket
            })

    def get_pipeline_execution(self, pipeline_ticket: str):
        if pipeline_ticket == None:
            return self.mondb.find(Mongo.pipeline_execution_col, {})
        else:
            return self.mondb.find_one(Mongo.pipeline_execution_col, {
                PipelineExecution.pipeline_ticket: pipeline_ticket
            })

    def register_executor_endpoint(self,
                                   executor_name: str,
                                   executor_type: str,
                                   executor_endpoint_url: str,
                                   executor_info: dict):
        existed_executor_id = None
        all_executor_registration_info = self.mondb.find(
            Mongo.executor_registration_col, {})
        # print(all_executor_registration_info)
        for e_rg_info in all_executor_registration_info:
            # if url and type is the same, consider the update
            if e_rg_info[ExecutorRegInfo.executor_endpoint_url] == executor_endpoint_url \
                    and e_rg_info[ExecutorRegInfo.executor_type] == executor_type:
                existed_executor_id = e_rg_info[ExecutorRegInfo.executor_id]
                break

        _id = None
        if existed_executor_id != None:
            _id = existed_executor_id
        else:
            _id = __get_random_string_no_low__(10)

        reg_time = time.time()

        # send reg info to executor service
        resp = requests.post(
            executor_endpoint_url + '/executor',
            data={
                'act': 'reg',
                ExecutorRegInfo.executor_id: _id,
                ExecutorRegInfo.executor_name: executor_name,
                ExecutorRegInfo.executor_register_time: reg_time,
                ExecutorRegInfo.executor_type: executor_type,
                ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
                ExecutorRegInfo.executor_info: json.dumps(executor_info),
            }
        )

        if resp.status_code == 200:
            if existed_executor_id != None:
                self.mondb.update_one(Mongo.executor_registration_col, {
                    ExecutorRegInfo.executor_id: existed_executor_id
                }, {
                    "$set": {
                        ExecutorRegInfo.executor_info: executor_info,
                    },
                    "$currentDate": {"last_modified": {"$type": "timestamp"}}
                })
            else:
                executor_reg_info = {
                    ExecutorRegInfo.executor_id: _id,
                    ExecutorRegInfo.executor_name: executor_name,
                    # ExecutorRegInfo.executor_owner: executor_owner,
                    ExecutorRegInfo.executor_register_time: reg_time,
                    ExecutorRegInfo.executor_type: executor_type,
                    ExecutorRegInfo.executor_info: executor_info,
                    ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
                    ExecutorRegInfo.sys_info: json.loads(
                        resp.content.decode('utf-8'))
                }
                self.mondb.insert_one(Mongo.executor_registration_col,
                                      executor_reg_info)
            return _id
        else:
            return None

    def if_executor_registered(self, executor_id: str):
        return self.mondb.find_one(Mongo.executor_registration_col, {
            ExecutorRegInfo.executor_id: executor_id
        }) is not None

    def delete_executor_endpoint(self, executor_id):
        self.mondb.delete_one(Mongo.executor_registration_col, {
                              ExecutorRegInfo.executor_id: executor_id})

    def build_g6_data_from_provenance_data(self, raw_data):
        data = {
            'nodes': [],
            'edges': [],
            'combos': [],
        }
        color_map_combo = {
            "executor": "#0cb2af",
            "configuration": "#a1c65d",
            "task_sheet": "#fac723",
            "task_execution": "#f29222",
            "pipeline_sheet": "#e95e50",
            "pipeline_execution": "#936fac",
        }

        combo_set = set()
        for provenance_cluster_key in [
            "configurations",
            "executors",
            "pipeline_executions",
            "pipeline_sheets",
            "task_executions",
            "task_sheets",
        ]:
            node_type = provenance_cluster_key[:-1]
            id_key = f"{node_type}_id"
            name_key = f"{node_type}_name"
            provenance_infos = raw_data[provenance_cluster_key]
            if provenance_infos is not None and len(provenance_infos) > 0:
                for provenance_info in provenance_infos:
                    del provenance_info['_id']
                    component_type_key = next(
                        k for k in provenance_info.keys() if k.endswith("_type"))
                    provenance_info['node_type'] = node_type
                    component_type = provenance_info[component_type_key]

                    combo_key = f"{component_type}_{node_type}".replace(
                        "pipeline_pipeline", "pipeline").replace("_", " ")

                    combo_key = "configuration" if combo_key.endswith(
                        "configuration") else combo_key
                    combo_key = "executor" if combo_key.endswith(
                        "executor") else combo_key

                    node_render_type = "circle"
                    if provenance_cluster_key.endswith("_executions"):
                        status_arr = [
                            pk for pk in provenance_info.keys() if pk.endswith("_status")]
                        if len(status_arr) == 1 and provenance_info[status_arr[0]] == "running":
                            node_render_type = "breathing-circle"

                    node = {
                        'id': provenance_info[provenance_cluster_key.replace("_executions", "_ticket") if provenance_cluster_key.endswith("_executions") else id_key],
                        'type': node_render_type,
                        'label': provenance_info[name_key],
                        'data': provenance_info,
                        'combo': combo_key,
                        'style': {
                            'fill': color_map_combo[node_type],
                        },
                    }

                    data['nodes'].append(node)
                    new_edges = self.provenance_edge_mapping(node)
                    data['edges'].extend(new_edges)
                    combo_set.add(combo_key)

        for combo in combo_set:
            data['combos'].append({
                'id': combo,
            })

        return data

    def provenance_edge_mapping(self, node):
        new_edges = []
        attr = node['data']
        if attr['node_type'] == "task_sheet":
            for attr_key in attr.keys():
                attr_value = attr[attr_key]
                if attr_key.endswith("_executor_id") and attr_value != "undefined":
                    new_edges.append({
                        'id': f"{node['id']}-{attr_value}",
                        'source': attr_value,
                        'target': node['id'],
                        'label': "used",
                    })
                if attr_key == "previous_task_ticket" and attr_value != "undefined":
                    new_edges.append({
                        'id': f"{node['id']}-{attr_value}",
                        'source': attr_value,
                        'target': node['id'],
                        'label': "used",
                    })

            for configuration_type in ["dataset", "model", "trainer"]:
                config_id_key = f"{configuration_type}_configuration_id"
                config_value = attr['task_parameters'].get(config_id_key)

                if config_value is not None:
                    if configuration_type == "dataset":
                        for v in config_value:
                            new_edges.append({
                                'id': f"{node['id']}-{v}",
                                'source': v,
                                'target': node['id'],
                                'label': "used",
                            })
                    else:
                        new_edges.append({
                            'id': f"{node['id']}-{config_value}",
                            'source': config_value,
                            'target': node['id'],
                            'label': "used",
                        })

        if attr['node_type'] == "task_execution":
            new_edges.append({
                'source': node['id'],
                'target': attr['task_sheet_id'],
                'label': "wasGeneratedBy",
            })

        if attr['node_type'] == "pipeline_sheet":
            for attr_key in attr.keys():
                attr_value = attr[attr_key]
                if attr_key.endswith("task_sheet_id") and attr_value != "undefined":
                    new_edges.append({
                        'id': f"{node['id']}-{attr_value}",
                        'source': node['id'],
                        'target': attr_value,
                        'label': "wasDerivedFrom",
                    })

        if attr['node_type'] == "pipeline_execution":
            new_edges.append({
                'source': node['id'],
                'target': attr['pipeline_sheet_id'],
                'label': "wasGeneratedBy",
            })
            for task_execution_ticket in attr['task_execution_tickets']:
                new_edges.append({
                    'source': task_execution_ticket,
                    'target': node['id'],
                    'label': "used",
                })

        return new_edges

    def get_provenance(self):
        rs = {
            'configurations': self.mondb.find(Mongo.configuration_col, {}),
            'executors': self.mondb.find(Mongo.executor_registration_col, {}),
            'task_sheets': self.mondb.find(Mongo.task_sheet_col, {}),
            'task_executions': self.mondb.find(Mongo.task_execution_col, {}),
            'pipeline_sheets': self.mondb.find(Mongo.pipeline_sheet_col, {}),
            'pipeline_executions': self.mondb.find(Mongo.pipeline_execution_col, {}),
        }
        prov = self.build_g6_data_from_provenance_data(rs)
        # return rs
        return prov

    def create_configuration(self, payload):
        configuration_tb = self.mondb.col(Mongo.configuration_col)

        configuration = {
            Configuration.configuration_id: __get_random_string_no_low__(8),
            Configuration.configuration_name: payload.get(Configuration.configuration_name),
            Configuration.configuration_content: payload.get(Configuration.configuration_content),
            Configuration.configuration_type: payload.get(Configuration.configuration_type),
        }
        configuration_tb.insert_one(configuration)
        return configuration[Configuration.configuration_id]

    def update_configuration(self, configuration_id, configuration_content):
        self.mondb.update_one(Mongo.configuration_col, {
            Configuration.configuration_id: configuration_id
        }, {
            "$set": {
                Configuration.configuration_content: configuration_content
            }
        })
        return self.mondb.find_one(Mongo.configuration_col, {
            Configuration.configuration_id: configuration_id
        })

    def get_configuration(self, configuration_id=None):
        if configuration_id == None:
            return self.mondb.find(
                Mongo.configuration_col, {})
        else:
            return self.mondb.find_one(
                Mongo.configuration_col, {Configuration.configuration_id: configuration_id})

    def delete_configuration(self, configuration_id):
        self.mondb.delete_one(Mongo.configuration_col, {
                              Configuration.configuration_id: configuration_id})

    def save_task_emission(self, emission_info):
        task_ticket = emission_info['project_name']
        del emission_info['project_name']
        del emission_info['run_id']
        del emission_info['experiment_id']
        del emission_info['user']
        task_execution = self.get_task_execution(task_ticket)
        running_info = task_execution.get(TaskExecution.running_info, {})
        running_info['emission_info'] = emission_info

        self.task_publisher.mondb.update_one(Mongo.task_execution_col, {
            TaskExecution.task_ticket: task_ticket
        }, {
            "$set": {
                TaskExecution.running_info: running_info
            },
        })


class TaskAndPipelineManager():

    def __init__(self, task_publisher: TaskPublisher) -> None:

        self.task_publisher = task_publisher
        self.component_name = self.task_publisher.publisher_name
        self.component_path = self.task_publisher.component_path
        self.component_path_parent = os.path.abspath(
            os.path.dirname(self.component_path))

        self.storage_path = os.path.join(
            self.component_path_parent, f'{self.component_name}_storage')
        self.import_name = self.task_publisher.import_name
        self.ws_map: dict[websockets.asyncio.server.ServerConnection] = {}

    def create_pipeline_sheet(self, pipeline_sheet_info):
        pipeline_type = pipeline_sheet_info[PipelineSheet.pipeline_type]
        pipeline_sheet_infos = []
        if pipeline_type == "training_pipeline" and ("," in pipeline_sheet_info[PipelineSheet.train_task_sheet_id]):
            train_task_sheet_ids = pipeline_sheet_info[PipelineSheet.train_task_sheet_id].split(
                ',')
            pipeline_sheet_names = pipeline_sheet_info[PipelineSheet.pipeline_sheet_name].split(
                ',')
            for i in range(len(train_task_sheet_ids)):
                pipeline_sheet_infos.append({
                    PipelineSheet.train_task_sheet_id: train_task_sheet_ids[i],
                    PipelineSheet.pipeline_sheet_name: pipeline_sheet_names[i],
                    PipelineSheet.model_evaluation_task_sheet_id: pipeline_sheet_info[PipelineSheet.model_evaluation_task_sheet_id],
                    PipelineSheet.pipeline_type: PipelineType.training_pipeline
                })
        else:
            pipeline_sheet_infos.append(pipeline_sheet_info)

        for p in pipeline_sheet_infos:
            self.create_one_pipeline(p)

    def create_one_pipeline(self, one_pipeline_sheet_info):
        pipeline_sheet_id = __get_random_string_no_low__(18)
        one_pipeline_sheet_info[PipelineSheet.pipeline_sheet_id] = pipeline_sheet_id
        one_pipeline_sheet_info[PipelineSheet.create_at] = time.time()

        self.task_publisher.mondb.insert_one(
            Mongo.pipeline_sheet_col, one_pipeline_sheet_info)
        return self.task_publisher.mondb.find_one(Mongo.pipeline_sheet_col, {
            PipelineSheet.pipeline_sheet_id: pipeline_sheet_id
        })

    def create_task_sheet(self, new_task_sheet: dict):
        new_task_sheet[TaskSheet.task_sheet_id] = __get_random_string_no_low__(
            15)
        new_task_sheet[TaskSheet.task_parameters] = json.loads(
            new_task_sheet[TaskSheet.task_parameters])
        self.task_publisher.mondb.col(
            Mongo.task_sheet_col).insert_one(new_task_sheet)
        return new_task_sheet[TaskSheet.task_sheet_id]

    async def update_task_status(self, task_ticket, task_status, code_version_hash, running_info, pipeline_ticket):
        current_task_execution = self.task_publisher.mondb.find_one(Mongo.task_execution_col, {
            TaskExecution.task_ticket: task_ticket
        })
        print(f"Update status of {task_ticket} as {task_status}")
        print(f"Task {current_task_execution.get(TaskExecution.task_type)}: {current_task_execution.get(TaskExecution.task_sheet_name)}")

        self.task_publisher.mondb.update_one(Mongo.task_execution_col, {
            TaskExecution.task_ticket: task_ticket
        }, {
            "$set": {
                TaskExecution.task_status: task_status,
                TaskExecution.end_time: time.time() if task_status == TaskStatus.finished else '',
                TaskExecution.running_info: running_info,
                TaskExecution.code_version_hash: code_version_hash
            },
        })

        current_task_execution = self.task_publisher.mondb.find_one(Mongo.task_execution_col, {
            TaskExecution.task_ticket: task_ticket
        })

        current_pipeline_execution = None
        if current_task_execution[TaskExecution.task_status] == TaskStatus.finished and pipeline_ticket is not None:
            current_pipeline_execution = self.task_publisher.mondb.find_one(Mongo.pipeline_execution_col, {
                PipelineExecution.pipeline_ticket: pipeline_ticket
            })

            task_execution_tickets = current_pipeline_execution[
                PipelineExecution.task_execution_tickets]

            idx = task_execution_tickets.index(
                current_task_execution[TaskExecution.task_ticket])
            if idx < len(task_execution_tickets) - 1:
                next_task_execution = self.task_publisher.mondb.find_one(Mongo.task_execution_col, {
                    TaskExecution.task_ticket: task_execution_tickets[idx + 1]
                })
                print(
                    f"Pass down the pipeline_execution to a {next_task_execution[TaskExecution.task_type]} task: {next_task_execution[TaskExecution.task_ticket]}")
                await self.tell_executor_to_execute_task(
                    next_task_execution, pipeline_ticket, current_pipeline_execution)

        message = WsMessage(message_type=WsMessageType.TASK_STATUS_UPDATE, payload=dict(
            task_ticket=task_ticket,
            current_task_execution=current_task_execution,
            pipeline_ticket=pipeline_ticket,
            current_pipeline_execution=current_pipeline_execution
        ))
        await send_and_remove_closed(self.ws_map, message)

    def get_pipeline(self, pipeline_sheet_id: str = None):
        if pipeline_sheet_id == None:
            pipeline_sheets = self.task_publisher.mondb.find(
                Mongo.pipeline_sheet_col, {})
        else:
            pipeline_sheets = [self.task_publisher.mondb.find_one(Mongo.pipeline_sheet_col, {
                PipelineSheet.pipeline_sheet_id: pipeline_sheet_id
            })]

        for pipeline_sheet in pipeline_sheets:
            pipeline_executions = self.get_pipeline_executions_by_pipeline_sheet_id(
                pipeline_sheet[PipelineExecution.pipeline_sheet_id])
            if len(pipeline_executions) == 0:
                pipeline_sheet[TaskExecution.task_status] = TaskStatus.initialized
            elif TaskStatus.running in [pipeline_execution[TaskExecution.task_status] for pipeline_execution in pipeline_executions]:
                pipeline_sheet[TaskExecution.task_status] = TaskStatus.running
            else:
                pipeline_sheet[TaskExecution.task_status] = TaskStatus.finished

        return pipeline_sheets

    def get_task_sheets(self, task_sheet_ids):
        if task_sheet_ids == None:
            sheets = self.task_publisher.mondb.find(Mongo.task_sheet_col, {})
        else:
            sheets = self.task_publisher.mondb.find(Mongo.task_sheet_col, {
                TaskSheet.task_sheet_id: {"$in": task_sheet_ids}
            })

        for sheet in sheets:
            task_sheet_id = sheet[TaskSheet.task_sheet_id]
            task_executions = self.task_publisher.get_task_executions_by_task_sheet_id(
                task_sheet_id)
            all_status = set([task_execution[TaskExecution.task_status]
                             for task_execution in task_executions])
            if len(all_status) == 0:
                sheet[TaskExecution.task_status] = TaskStatus.initialized
            elif TaskStatus.running in all_status:
                sheet[TaskExecution.task_status] = TaskStatus.running
            else:
                sheet[TaskExecution.task_status] = TaskStatus.finished

        return sheets

    def remove_task_sheet_to_pipeline(self, pipeline_sheet_id: str, task_sheet_id: str):
        pass

    def __get_url_from_executor_id__(self, executor_id):
        for executor_info in self.task_publisher.get_executor_registration_info():
            if executor_info[ExecutorRegInfo.executor_id] == executor_id:
                return executor_info[ExecutorRegInfo.executor_endpoint_url]

    async def tell_executor_to_execute_task(self, task_execution, pipeline_ticket, pipeline_execution=None):
        self.task_publisher.mondb.update_one(Mongo.task_execution_col, {
            TaskExecution.task_ticket: task_execution[TaskExecution.task_ticket]
        }, {
            "$set": {
                TaskExecution.task_status: TaskStatus.running,
                TaskExecution.start_time: time.time()
            }
        })

        payload = {
            'act': 'execute',
            'task_execution': json.dumps(task_execution),
            'pipeline_ticket': pipeline_ticket
        }
        requests.request(
            "POST", f"{task_execution[TaskExecution.executor_endpoint_url]}/task_execution", headers={}, data=payload)

        task_execution = self.task_publisher.mondb.find_one(Mongo.task_execution_col, {
            TaskExecution.task_ticket: task_execution[TaskExecution.task_ticket]
        })
        message = WsMessage(message_type=WsMessageType.TASK_STATUS_UPDATE, payload=dict(
            task_ticket=task_execution[TaskExecution.task_ticket],
            current_task_execution=task_execution,
            pipeline_ticket=pipeline_ticket,
            current_pipeline_execution=pipeline_execution
        ))
        await send_and_remove_closed(self.ws_map, message)
        return task_execution[TaskExecution.task_ticket]

    def delete_task(self, task_ticket):
        task_info = self.task_publisher.mondb.find_one(Mongo.task_execution_col, {
            TaskExecution.task_ticket: task_ticket
        })
        if task_info is not None:
            payload = {
                'act': 'delete',
                'task_ticket': task_ticket
            }

            response = requests.request(
                "POST", f"{task_info[TaskExecution.executor_endpoint_url]}/task_execution", headers={}, data=payload)

            if response.status_code == 200:
                self.task_publisher.mondb.delete_one(Mongo.task_execution_col, {
                    TaskExecution.task_ticket: task_ticket
                })

                # self.task_publisher.az.delete_blobs(
                #     f'task_execution/result/{task_ticket}')

    def generate_task_execution_in_pipeline(self, task_sheet, pipeline_sheet):
        existing_executions_number = len(self.task_publisher.mondb.find(Mongo.task_execution_col, {
            TaskExecution.task_sheet_id: task_sheet[TaskSheet.task_sheet_id],
        }))
        new_task_execution = self.task_publisher.gen_task_execution(
            task_sheet,
            task_execution_name=f"{pipeline_sheet[PipelineSheet.pipeline_sheet_name]}-{task_sheet[TaskSheet.task_type]}-#{existing_executions_number}"
        )
        return new_task_execution

    def generate_tasks_and_link_tasks(
        self, pipeline_sheet, train_task_sheet_id, model_evaluation_task_sheet_id,
        xai_task_sheet_id, xai_evaluation_task_sheet_id,
        reused_train_task_execution_ticket, reused_model_evaluation_pipeline_execution_ticket
    ):
        pipeline_task_executions = []

        train_task_sheet = self.task_publisher.mondb.find_one(Mongo.task_sheet_col, {
            TaskSheet.task_sheet_id: train_task_sheet_id
        })
        model_evaluation_task_sheet = self.task_publisher.mondb.find_one(Mongo.task_sheet_col, {
            TaskSheet.task_sheet_id: model_evaluation_task_sheet_id
        })
        xai_task_sheet = self.task_publisher.mondb.find_one(Mongo.task_sheet_col, {
            TaskSheet.task_sheet_id: xai_task_sheet_id
        })
        xai_evaluation_task_sheet = self.task_publisher.mondb.find_one(Mongo.task_sheet_col, {
            TaskSheet.task_sheet_id: xai_evaluation_task_sheet_id
        })

        if reused_train_task_execution_ticket is None:
            if reused_model_evaluation_pipeline_execution_ticket is not None:
                reused_model_evaluation_task_execution = self.task_publisher.mondb.find_one(Mongo.task_execution_col, {
                    TaskExecution.task_ticket: reused_train_task_execution_ticket
                })
                pipeline_task_executions.append(
                    reused_model_evaluation_task_execution)
            else:
                assert train_task_sheet_id is not None
        else:
            # force train_task_sheet_id to be None
            train_task_sheet = None
            train_task_sheet_id = None
            reused_train_task_execution = self.task_publisher.mondb.find_one(Mongo.task_execution_col, {
                TaskExecution.task_ticket: reused_train_task_execution_ticket
            })
            pipeline_task_executions.append(reused_train_task_execution)

        for ts in [
            train_task_sheet, model_evaluation_task_sheet,
            xai_task_sheet, xai_evaluation_task_sheet
        ]:
            if ts is not None:
                pipeline_task_executions.append(
                    self.generate_task_execution_in_pipeline(
                        ts, pipeline_sheet)
                )

        print(pipeline_task_executions)
        for i, current_task_execution in enumerate(pipeline_task_executions):
            if i > 0:
                previous_task_execution = pipeline_task_executions[i - 1]
                if current_task_execution.get(TaskExecution.previous_task_ticket) is None:
                    current_task_execution[TaskExecution.previous_task_ticket] = previous_task_execution[TaskExecution.task_ticket]

                    self.task_publisher.mondb.update_one(Mongo.task_execution_col, {
                        TaskExecution.task_ticket: current_task_execution[TaskExecution.task_ticket]
                    }, {
                        "$set": {
                            TaskExecution.previous_task_ticket: previous_task_execution[
                                TaskExecution.task_ticket]
                        }
                    })

        return pipeline_task_executions

    async def execute_pipeline(self, pipeline_sheet):
        pipeline_task_executions, pipeline_execution = self.generate_pipeline_execution_from_pipeline_sheet(
            pipeline_sheet)

        await self.tell_executor_to_execute_task(
            pipeline_task_executions[0], pipeline_execution[PipelineExecution.pipeline_ticket])

        return pipeline_execution

    def generate_pipeline_execution_from_pipeline_sheet(self, pipeline_sheet):
        train_task_sheet_id = pipeline_sheet.get(
            PipelineSheet.train_task_sheet_id)
        model_evaluation_task_sheet_id = pipeline_sheet.get(
            PipelineSheet.model_evaluation_task_sheet_id)
        xai_task_sheet_id = pipeline_sheet.get(PipelineSheet.xai_task_sheet_id)
        xai_evaluation_task_sheet_id = pipeline_sheet.get(
            PipelineSheet.xai_evaluation_task_sheet_id)

        reused_train_task_execution_ticket = pipeline_sheet.get(
            PipelineSheet.reused_train_task_execution_ticket)
        reused_model_evaluation_pipeline_execution_ticket = pipeline_sheet.get(
            PipelineSheet.reused_model_evaluation_pipeline_execution_ticket)

        print("Create pipeline_sheet for")
        print(pipeline_sheet)

        pipeline_task_executions = self.generate_tasks_and_link_tasks(
            pipeline_sheet,
            train_task_sheet_id, model_evaluation_task_sheet_id,
            xai_task_sheet_id, xai_evaluation_task_sheet_id,
            reused_train_task_execution_ticket, reused_model_evaluation_pipeline_execution_ticket
        )

        task_execution_tickets = [task_execution[TaskExecution.task_ticket]
                                  for task_execution in pipeline_task_executions]

        pipeline_execution = self.task_publisher.generate_pipeline_execution_from_pipeline_sheet_and_task_execution(
            pipeline_sheet, task_execution_tickets
        )
        return pipeline_task_executions, pipeline_execution

    def get_pipeline_execution_by_ticket(self, pipeline_ticket):
        return self.task_publisher.mondb.find_one(Mongo.pipeline_execution_col, {
            PipelineExecution.pipeline_ticket: pipeline_ticket
        })

    def get_pipeline_executions_by_pipeline_sheet_id(self, pipeline_sheet_id):
        pipeline_executions = self.task_publisher.mondb.find(Mongo.pipeline_execution_col, {
            PipelineExecution.pipeline_sheet_id: pipeline_sheet_id
        })

        for pipeline_execution in pipeline_executions:
            tasks = self.task_publisher.mondb.find(Mongo.task_execution_col, {
                TaskExecution.task_ticket: {
                    "$in": pipeline_execution[PipelineExecution.task_execution_tickets]
                }
            })

            pipeline_execution_status = []
            for task in tasks:
                current_acutal_status = task[TaskExecution.task_status]
                if current_acutal_status == TaskStatus.running:
                    current_acutal_status = self.task_publisher.ask_executor_task_actual_status(
                        task[TaskExecution.task_ticket],
                        task[TaskExecution.executor_endpoint_url]
                    )

                    if current_acutal_status == TaskStatus.not_exist_in_executor_process_holder:
                        # if the executor is shutdown
                        current_acutal_status = TaskStatus.stopped

                    if current_acutal_status != task[TaskExecution.task_status]:
                        self.task_publisher.mondb.update_one(Mongo.task_execution_col, {
                            TaskExecution.task_ticket: task[TaskExecution.task_ticket]
                        }, {
                            "$set": {
                                TaskExecution.task_status: current_acutal_status
                            }
                        })
                pipeline_execution[f"{task[TaskExecution.task_type]}_task_status"] = current_acutal_status

            for k in dir(TaskType):
                if not k.endswith('__'):
                    if pipeline_execution.get(f"{k}_task_status", None) is None:
                        pipeline_execution[f"{k}_task_status"] = 'NaN'
                    pipeline_execution_status.append(
                        pipeline_execution[f"{k}_task_status"])

            if TaskStatus.running in pipeline_execution_status:
                pipeline_execution[TaskExecution.task_status] = TaskStatus.running
            elif TaskStatus.initialized in pipeline_execution_status:
                pipeline_execution[TaskExecution.task_status] = TaskStatus.initialized
            else:
                pipeline_execution[TaskExecution.task_status] = TaskStatus.finished

        return pipeline_executions

    async def execute_task_sheet_directly(self, task_sheet_id):
        task_sheet = self.get_task_sheets([task_sheet_id])[0]

        required_task = self.task_publisher.gen_task_execution(
            task_sheet
        )

        if required_task != None:
            return await self.tell_executor_to_execute_task(required_task, None)
        else:
            return None

    def duplicate_pipeline(self, pipeline_sheet_id):
        pass

    def stop_a_task(self, task_ticket):
        task = self.task_publisher.mondb.find_one(Mongo.task_execution_col, {
            TaskExecution.task_ticket: task_ticket
        })
        requests.post(
            task[TaskExecution.executor_endpoint_url] + '/task_execution',
            data={
                'act': 'stop',
                TaskExecution.task_ticket: task_ticket
            }
        )

    def stop_pipeline_execution(self, pipeline_ticket):
        pipeline_execution = self.task_publisher.mondb.find_one(Mongo.pipeline_execution_col, {
            PipelineExecution.pipeline_ticket: pipeline_ticket
        })

        for task_ticket in pipeline_execution[PipelineExecution.task_execution_tickets]:
            self.stop_a_task(task_ticket)

    def get_task_execution_presentation(self, task_ticket, task_execution=None):

        if task_execution is None:
            task_execution = self.task_publisher.get_task_execution(
                task_ticket)

        resp = requests.get(
            task_execution[TaskExecution.executor_endpoint_url] +
            f'/task_result_present',
            params={
                "task_ticket": task_ticket
            }
        )

        trp = None
        try:
            trp = resp.json()
        except Exception as e:
            pass

        rs = {
            **self.get_task_execution_std_out_and_err(task_ticket),
            "task_execution_presentation": trp
        }

        return rs

    def get_pipeline_execution_presentations(self, pipeline_ticket, pipeline_execution=None):
        if pipeline_execution is None:
            pipeline_execution = self.task_publisher.get_pipeline_execution(
                pipeline_ticket)
        task_execution_tickets = pipeline_execution[PipelineExecution.task_execution_tickets]
        # task_execution_results = [self.get_task_execution_std_out_and_err(
        #     task_execution_ticket) for task_execution_ticket in task_execution_tickets]
        task_executions = [self.task_publisher.get_task_execution(
            task_ticket) for task_ticket in task_execution_tickets]
        hasRunning = False
        for task_execution in task_executions:
            hasRunning = hasRunning or (
                task_execution[TaskExecution.task_status] == TaskStatus.running)
        return hasRunning, [
            self.get_task_execution_presentation(task_execution_ticket, task_executions[i]) for i, task_execution_ticket in enumerate(task_execution_tickets)
        ]

    def get_task_execution_std_out_and_err(self, task_ticket):
        task_execution = self.task_publisher.mondb.find_one(Mongo.task_execution_col, {
            TaskExecution.task_ticket: task_ticket
        })
        out_log_response = requests.get(
            task_execution[TaskExecution.executor_endpoint_url] +
            f'/static/logs/{task_ticket}/out.log',
        )
        err_log_response = requests.get(
            task_execution[TaskExecution.executor_endpoint_url] +
            f'/static/logs/{task_ticket}/err.log',
        )
        return dict(
            task_execution_name=task_execution[TaskExecution.task_execution_name],
            task_status=task_execution[TaskExecution.task_status],
            std_out=re.split('\r|\n', out_log_response.content.decode(
                'utf-8')) if out_log_response.status_code == 200 else [],
            std_err=re.split('\r|\n', err_log_response.content.decode(
                'utf-8')) if err_log_response.status_code == 200 else [],
        )

    def get_task_executor_task_function_key(self, executor_id):
        executor_registration_info = self.task_publisher.get_executor_registration_info(
            executor_id)
        executor_endpoint_url = executor_registration_info[ExecutorRegInfo.executor_endpoint_url]

        response = requests.get(
            executor_endpoint_url + f'/get_available_task_function_key',
        )

        return json.loads(response.content.decode('utf-8'))

    def delete_pipeline(self, pipeline_sheet_id):

        pipeline_executions = self.task_publisher.mondb.find(Mongo.pipeline_execution_col, {
            PipelineExecution.pipeline_sheet_id: pipeline_sheet_id
        })

        for pipeline_execution in pipeline_executions:
            self.delete_pipeline_execution(
                pipeline_execution[PipelineExecution.pipeline_ticket])

        self.task_publisher.mondb.delete_one(Mongo.pipeline_sheet_col, {
            PipelineSheet.pipeline_sheet_id: pipeline_sheet_id
        })

    def delete_pipeline_execution(self, pipeline_ticket):
        pipeline_execution = self.task_publisher.mondb.find_one(Mongo.pipeline_execution_col, {
            PipelineExecution.pipeline_ticket: pipeline_ticket
        })

        task_execution_tickets = pipeline_execution[PipelineExecution.task_execution_tickets]
        for task_execution_ticket in task_execution_tickets:
            self.delete_task(task_execution_ticket)

        self.task_publisher.mondb.delete_one(Mongo.pipeline_execution_col, {
            PipelineExecution.pipeline_ticket: pipeline_ticket
        })

    def delete_task_sheet(self, task_sheet_id):

        tasks = self.task_publisher.mondb.find(Mongo.task_execution_col, {
            TaskSheet.task_sheet_id: task_sheet_id
        })

        for task in tasks:
            self.delete_task(task[TaskExecution.task_ticket])

        self.task_publisher.mondb.delete_one(Mongo.task_sheet_col, {
            TaskSheet.task_sheet_id: task_sheet_id
        })

    def predict_and_explain(
        self, image_fs,
        model_service_executor_id,
        model_training_execution_ticket,
        xai_service_executor_id,
        xai_task_function_key
    ):
        image_save_path = os.path.join(
            os.environ["COMPONENT_TMP_PATH"], f"predict_{model_training_execution_ticket}_{image_fs.filename}")
        image_file_name = image_fs.filename
        image_fs.save(image_save_path)

        training_task_execution = self.task_publisher.get_task_execution(
            model_training_execution_ticket)
        model_endpoint_url = training_task_execution[
            TaskExecution.task_parameters][TaskExecution.model_service_url]

        # https://stackoverflow.com/a/53143960/17094075
        # https://requests.readthedocs.io/en/latest/user/quickstart/#post-a-multipart-encoded-file
        with open(image_save_path, 'rb') as image:
            image_file = {
                'image': (image_file_name, image)
            }

            predict_resp = requests.post(
                model_endpoint_url + '/task_execution',
                data={
                    'act': 'run_sync',
                    'task_function_key': 'predict',
                    TaskExecution.task_parameters: json.dumps({
                        TaskExecution.previous_task_ticket: model_training_execution_ticket,
                    })
                },
                files=image_file
            )
            result = predict_resp.json()
            # create prediction task
            # create xai task

        explanation_url = None
        with open(image_save_path, 'rb') as image:
            image_file = {
                'image': (image_file_name, image)
            }

            if (xai_service_executor_id not in [None, 'undefined'] and xai_task_function_key not in [None, 'undefined']):
                xai_registration_info = self.task_publisher.get_executor_registration_info(
                    xai_service_executor_id)
                xai_endpoint_url = xai_registration_info[ExecutorRegInfo.executor_endpoint_url]
                xai_resp = requests.post(
                    xai_endpoint_url + '/task_execution',
                    data={
                        'act': 'run_sync',
                        'task_function_key': xai_task_function_key,
                        TaskSheet.task_parameters: json.dumps({
                            TaskSheet.previous_task_ticket: model_training_execution_ticket,
                            **training_task_execution[
                                TaskExecution.task_parameters]
                        })
                    },
                    files=image_file
                )

                explanation_url = f"{xai_endpoint_url}/static/explanation/{xai_resp.json()['explanation_filename']}"

        return {
            'prediction': result,
            'explanation_url': explanation_url,
        }
