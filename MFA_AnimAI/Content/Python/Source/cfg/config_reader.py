# -*- coding: utf-8 -*-
import sys
import os
import json

source_dir = os.path.normpath(os.path.join(__file__, '../..'))
CFG_FILEPATH = os.path.join(source_dir, 'config.json')


def get_json_object_from_cfg(config_file=CFG_FILEPATH):
    config_file = os.path.abspath(config_file)
    with open(config_file, 'r') as f:
        json_data = json.load(f)

    return json_data


def get_retargeter_config():
    json_object = get_json_object_from_cfg()
    retargeter_cfg = json_object.get('RETARGETER')

    return retargeter_cfg


def get_default_source_pose_name():
    retargeter_cfg = get_retargeter_config()
    source_pose_name = retargeter_cfg.get("DEFAULT_SOURCE_POSE_NAME",'A-Pose')

    return source_pose_name


def get_conn_config():
    json_object = get_json_object_from_cfg()
    conn_cfg = json_object.get('CONN')

    return conn_cfg


def get_ip_address():
    conn_cfg = get_conn_config()
    ip_adress = conn_cfg.get('ADDRESS')
    return ip_adress


def get_main_port():
    conn_cfg = get_conn_config()
    port = conn_cfg.get('MAIN_PORT')
    return port


def get_fbx_port():
    conn_cfg = get_conn_config()
    port = conn_cfg.get('FBX_PORT')
    return port

def get_source_ik_rig_path():
    retargeter_cfg = get_retargeter_config()
    source_ik_rig_path = retargeter_cfg.get("SOURCE_IK_RIG")

    return source_ik_rig_path

def get_rtg_path():
    retargeter_cfg = get_retargeter_config()
    rtg_path = retargeter_cfg.get("IK_RETARGETER")

    return rtg_path

def get_source_skeleton_path():
    retargeter_cfg = get_retargeter_config()
    source_skeleton_path = retargeter_cfg.get("SOURCE_SKELETON")

    return source_skeleton_path