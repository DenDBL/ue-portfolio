# -*- coding: utf-8 -*-

"""Библиотека для работы с путями внутри Unreal-проекта и путями из Cerebro. Методы взаимодействующие с Cerebro
помечены префиксом ``cf`` """

import os
import sys
from pathlib import Path
import unreal


scriptDir = os.path.dirname(__file__)
sys.path.append(scriptDir)

# import settings
import Source.hash.hash_test as hash

try:
    import Programs.Cerebro.c_functions as cerebro
except:
    unreal.log_warning("Не удалось подключить функции cerebro. Некоторый функционал может быть недоступен")

PROJECT_NAME = os.environ.get('MF_PROJECT_FOLDER_NAME', "PROJECT_NAME")

EPISODES_PATH = "/Game/{PROJECT_NAME}/Cinematics/Episodes"

FBX_SEARCH_ORDER_LIST = ['skm',
                         'rigging',
                         'modeling and unwrap',
                         'texturing']

PROPS_MASTER_MATERIAL_PATH = "/Game/{PROJECT_NAME}/Utilities/Materials/MasterMaterials/mm_PropsClothes.mm_PropsClothes"
CHARS_MASTER_MATERIAL_PATH = "/Game/{PROJECT_NAME}/Utilities/Materials/MasterMaterials/mm_CharsBody.mm_CharsBody"

ACTOR_SYSTEM = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
EDITOR_ASSET_SYSTEM = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
LS_SYSTEM = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
ASSET_REGISTRY = unreal.AssetRegistryHelpers.get_asset_registry()


def _format_ep_number(number):
    """Возвращает число в формате ``###``

    Parameters
    -----------
    number : int
        номер

    Returns
    ---------
    str
        Номер  в формате ``###``
    """
    return "{:03d}".format(number)


def _format_shotcut_number(number):
    """Возвращает число в формате ``##``

        Parameters
        -----------
        number : int
            номер

        Returns
        ---------
        str
            Номер  в формате ``##``
    """
    return "{:02d}".format(number)


def cf_get_asset_fbx_path(task_info):
    for ta in FBX_SEARCH_ORDER_LIST:
        path = cf_get_child_task_publish_path(task_info, ta)
        if path:
            return path


def cf_get_child_task_publish_path(task_info, child_ta, endswith='.fbx'):
    """Возвращает паблиш путь дочерней задачи до fbx-файла

        Parameters
        -----------
        task_info : dict
            Словарь ``task_info`` родителя
        child_ta: str
            Вид деятельности дочерней задачи
        Returns
        ---------
        str
            Путь до fbx-файла. Если в директории дочерней задачи нет fbx-файла - возвращает ``None``,
            выводит предупреждение в консоль Unreal Engine
    """
    child_task_id = cerebro.get_children_tasks(task_info['task_id'], child_ta)[0][1]
    child_task_info = cerebro.task_info_by_task_id(child_task_id)

    publish_path = cerebro.get_task_file_path(child_task_info, 'PUBLISH')

    publish_dir = os.path.dirname(publish_path)
    if not os.path.exists(publish_dir):
        unreal.log_warning(f'Unable to find directory {publish_dir} for {task_info.get("task_name")}')
        return

    base_name = cerebro.task_versions_paths(child_task_info).base_name

    publish_path = os.path.join(publish_dir, base_name + endswith)

    if not os.path.exists(publish_path):
        for file in os.listdir(publish_dir):
            if file.lower().endswith(endswith):
                publish_path = os.path.join(publish_dir, file)
                break

    if not publish_path or not os.path.exists(publish_path):
        unreal.log_warning(f'Unable to find path {publish_path} for {task_info.get("task_name")}')
        return

    return publish_path


def cf_get_epshotcut(task_info):
    cut_task_info, _, _ = cerebro.get_parent_task_by_activity(task_info, settings.get_activity_name_by_id(144825575))
    shot_task_info, _, _ = cerebro.get_parent_task_by_activity(task_info, settings.get_activity_name_by_id(144949542))
    ep_task_info, _, _ = cerebro.get_parent_task_by_activity(task_info, settings.get_activity_name_by_id(144433137))

    return ep_task_info['task_name'], shot_task_info['task_name'], cut_task_info['task_name']


def cf_get_foliage_st9_path(task_info):
    for ta in reversed(FBX_SEARCH_ORDER_LIST):
        path = cf_get_child_task_publish_path(task_info, ta, '.st9')
        if path:
            return path


def cf_get_textures_dir(task_info):
    """Возвращает путь задачи texturing до директории high-текстур

        Parameters
        -----------
        task_info : dict
            Словарь ``task_info`` родителя

        Returns
        ---------
        str
            Путь до директории текстур
    """
    child_task_id = cerebro.get_children_tasks(task_info['task_id'], 'texturing')[0][1]
    child_task_info = cerebro.task_info_by_task_id(child_task_id)

    publish_path = cerebro.get_task_file_path(child_task_info, 'PUBLISH')

    publish_dir = os.path.dirname(publish_path)
    if not os.path.exists(publish_dir):
        unreal.log_warning(f'Unable to find directory {publish_dir} for {task_info.get("task_name")}')
        return

    output_path = os.path.join(publish_dir, 'Output')

    for file in os.listdir(output_path):
        if 'h' in file.lower():
            output_path = os.path.join(output_path, file)

    return output_path


def create_dir(path):
    """Создаёт директорию в Unreal-проекте, если таковой не существует

           Parameters
           -----------
            path: str
                Путь директории
       """
    if not is_dir_exists(path):
        unreal.EditorAssetLibrary.make_directory(path)


# def get_all_assets_of_python_class(python_class):
#     """Возвращает все ассеты проекта, принадлежащие Python-классу
#
#            Parameters
#            -----------
#             python_class: Class
#                 Python-класс ассета
#            Returns
#            ---------
#            list[unreal.AssetData]
#                 Список ассетов проекта
#     """
#     static_class = python_class.static_class()
#
#     package_path = static_class.get_path_name().split('.')[0]
#     asset_name = static_class.get_path_name().split('.')[1]
#
#     assets = ASSET_REGISTRY.get_assets_by_class(unreal.TopLevelAssetPath(package_path, asset_name), True)
#
#     return assets


def get_activity_asset_dir(activity):
    return f"/Game/{get_project_name()}/Assets/{activity}"


def get_basename_without_ext(path):
    """Возвращает имя файла без расширения

      Parameters
      -----------
       path: str
            Путь до файла
      Returns
      ---------
      str
            имя файла без расширения
    """
    return Path(path).stem


def get_bp_path_from_sekeletal_path(skeletal_mesh_path):
    skeletal_mesh_name = os.path.basename(skeletal_mesh_path).rsplit('.')[-1]
    package_path = os.path.dirname(skeletal_mesh_path)
    blueprint_name = 'BP_' + skeletal_mesh_name.split('_', 1)[1].rsplit('_', 1)[0]

    return os.path.join(package_path, blueprint_name).replace('\\','/')


def get_chars_master_material_path():
    return CHARS_MASTER_MATERIAL_PATH.format(PROJECT_NAME=get_project_name())


def get_cut_dir(ep_number, shot_number, cut_number):
    """Возвращает путь до директории ката внутри UE-проекта

    Parameters
    -----------
    ep_number: int
        Номер эпизода
    shot_number: int
        Номер шота
    cut_number
        Номер ката

    Returns
    ---------
    str
        Путь до директории ката
    """
    cut_folder = "cut" + _format_shotcut_number(cut_number)

    return os.path.join(get_shot_dir(ep_number, shot_number), cut_folder)


def get_episode_dir(ep_number):
    """Возвращает путь до директории эпизода внутри UE-проекта

    Parameters
    -----------
    ep_number: int
        Номер эпизода

    Returns
    ---------
    str
        Путь до директории эпизода
    """
    ep_folder = "ep" + _format_ep_number(ep_number)

    return os.path.join(get_episodes_path(), ep_folder)


def get_episodes_path():
    return EPISODES_PATH.format(PROJECT_NAME=get_project_name())


def get_project_name():
    return os.environ.get('MF_PROJECT_FOLDER_NAME', "PROJECT_NAME")


def get_props_master_material_path():
    return PROPS_MASTER_MATERIAL_PATH.format(PROJECT_NAME=get_project_name())


def get_shot_dir(ep_number, shot_number):
    """Возвращает путь до директории шота внутри UE-проекта

    Parameters
    -----------
    ep_number: int
        Номер эпизода
    shot_number: int
        Номер шота

    Returns
    ---------
    str
        Путь до директории шота
    """
    shot_folder = "sh" + _format_shotcut_number(shot_number)

    return os.path.join(get_episode_dir(ep_number), shot_folder)


def is_asset_exists(path):
    """Проверяет существует ли ассет внутри UE-проекта

    Parameters
    -----------
    path: str
        Путь

    Returns
    ---------
    bool
    """
    return unreal.EditorAssetLibrary.does_asset_exist(path.replace("\\", "/"))


def is_dir_exists(path):
    """Проверяет существует ли путь внутри UE-проекта

    Parameters
    -----------
    path: str
        Путь

    Returns
    ---------
    bool
    """
    return unreal.EditorAssetLibrary.does_directory_exist(path.replace("\\", "/"))
