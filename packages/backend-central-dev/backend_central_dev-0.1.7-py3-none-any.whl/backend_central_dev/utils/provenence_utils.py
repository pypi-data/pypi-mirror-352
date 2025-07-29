from prov.model import ProvDocument
import datetime

# introduce the prov-constraints, to reinforce the pipeline, to assist the pipeline
# order of the activities, the linage of the data, the data flow, the data processing


def provn(prov_raw):
    prov_d = ProvDocument()
    # Declaring namespaces for various prefixes used in the example
    prov_d.add_namespace('mlxops', 'ns://mlxops')

    nodes = prov_raw['nodes']
    edges = prov_raw['edges']
    str_omit_len = 30

    prov_name_id_mapping = {}
    entity_list = []
    activity_list = []
    for node in nodes:
        node_data = node['data']
        node_id = node['id']
        for node_data_key, node_data_value in node_data.items():
            if node_data_key.endswith('_name'):
                name = node_data_value
            if node_data_key == 'node_type':
                node_type = node_data_value

        attributes = {
            'mlxops:node_type': node_type,
        }
        for node_data_key, node_data_value in node_data.items():
            if node_data_key in ['node_type', 'start_time', 'end_time']:
                continue
            if type(node_data_value) == str:
                node_data_value = node_data_value.replace(
                    "\n", "").replace("\r", "")
            elif type(node_data_value) in [dict, list]:
                node_data_value = str(node_data_value)
            else:
                node_data_value = node_data_value

            if type(node_data_value) == str and len(node_data_value) > str_omit_len:
                node_data_value = node_data_value[:str_omit_len] + "..."
            attributes[f'mlxops:{node_data_key}'] = node_data_value
        prov_id = f"mlxops:{name}_{node_id}"
        prov_name_id_mapping[node_id] = prov_id
        prov_name_id_mapping[prov_id] = node_id
        if node_type.endswith('_execution'):
            start_time = node_data.get('start_time')
            end_time = node_data.get('end_time')
            activity_list.append(
                (prov_id,
                    datetime.datetime.fromtimestamp(
                        start_time) if start_time is not None else None,
                    datetime.datetime.fromtimestamp(
                        end_time) if end_time is not None else None,
                    attributes))
        else:
            entity_list.append((prov_id, attributes))

    for entity in entity_list:
        prov_d.entity(entity[0], entity[1])
    for activity in activity_list:
        prov_d.activity(
            activity[0], activity[1] if activity[2] is not None else None, activity[2], activity[3])

    for edge in edges:
        lebel = edge['label']
        source_id = edge['source']
        target_id = edge['target']
        getattr(prov_d, lebel)(
            prov_name_id_mapping[source_id], prov_name_id_mapping[target_id])

    return prov_d
