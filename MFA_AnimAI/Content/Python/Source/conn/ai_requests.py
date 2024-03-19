# -*- coding: utf-8 -*-

import DLLs.requests as requests
import Source.cfg.config_reader as cfg

IP_ADDRESS = cfg.get_ip_address()
MAIN_PORT = cfg.get_main_port()
FBX_PORT = cfg.get_fbx_port()


def make_url(path='', is_fbx=False):
    port = MAIN_PORT if not is_fbx else FBX_PORT

    return f'{IP_ADDRESS}:{port}' + path


def handle_response(response: requests.Response):
    if response.status_code not in range(200, 299):
        raise Exception(str(response.reason))


def get_models() -> requests.Response:
    url_path = make_url('/models')

    response = requests.get(url_path)
    handle_response(response)

    return response


def request_generation(in_params)-> requests.Response:
    url_path = make_url('/tasks/generate')

    response = requests.post(url_path, json=in_params)
    print(response.status_code)
    handle_response(response)

    return response


def get_progress()-> requests.Response:
    url_path = make_url('/tasks/progress')

    response = requests.get(url_path)
    handle_response(response)

    return response


def get_result(task_id)-> requests.Response:
    url_path = make_url(f'/tasks/{str(task_id)}')

    response = requests.get(url_path)
    handle_response(response)

    return response


def is_task_done(task_id)-> requests.Response:
    response = get_result(task_id)

    data = response.json()

    status = data.get('data', {}).get('attributes', {}).get('status')

    if not status:
        raise Exception('Task status is None')

    return status == 'DONE'


def get_fbx_from_list_of_bvh(bvh_s3_paths: list):
    url_path = make_url(f'/export/fbx/', is_fbx=True)

    response = requests.post(url_path, json={'bvh_anim_urls': bvh_s3_paths})

    return response