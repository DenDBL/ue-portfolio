# -*- coding: utf-8 -*-

import time
import tempfile
import os


def get_task_id_from_response(response):
    return response.json().get('data').get('id')


def get_list_of_samples_from_response(response):
    samples_data_list = response.json().get('data').get('attributes').get('samples')

    samples_url_list = []
    for sample in samples_data_list:
        samples_url_list.append(sample.get('s3_url'))

    return samples_url_list


def get_list_of_fbx_from_response(response):
    fbx_urls = response.get('fbx_urls')

    return fbx_urls


def download_fbx(fbx_url, fbx_save_path):
    import wget

    return wget.download(fbx_url, fbx_save_path)


def get_timestamp_str():
    timestr = time.strftime("%Y%m%d-%H%M%S")

    return timestr


def get_temp_fbx_file_path(additional_str=''):
    temp_dir = tempfile.mkdtemp()
    file_name = f'anim_{additional_str}_{get_timestamp_str()}.fbx'

    return os.path.join(temp_dir, file_name)


def get_models_from_response(response):
    models = response.json().get('data')

    return models


def get_model_name(model):
    return model.get('attributes').get('name')


def get_model_id(model):
    return model.get('id')
