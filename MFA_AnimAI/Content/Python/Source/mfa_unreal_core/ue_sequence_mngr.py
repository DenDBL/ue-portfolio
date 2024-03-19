# -*- coding: utf-8 -*-
"""
Библиотека для работы с секвенциями уровней Unreal-проекта. Методы взаимодействующие с Cerebro
помечены префиксом ``cf``
"""
import os
import sys
import threading
import time
import traceback
import uuid
from pathlib import Path
import unreal

scriptDir = os.path.dirname(__file__)
sys.path.append(scriptDir)

import ue_content_mngr as ue_content
import ue_path_mngr as ue_path

# import settings

# import System_file.metadat as metadata

try:
    import Programs.Cerebro.c_functions as cerebro
except:
    unreal.log_warning("Не удалось подключить функции cerebro. Некоторый функционал может быть недоступен")

ACTOR_SYSTEM = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
EDITOR_SYSTEM = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EDITOR_LEVEL_SYSTEM = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EDITOR_ASSET_SYSTEM = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
LAYERS_SYSTEM = unreal.get_editor_subsystem(unreal.LayersSubsystem)
LS_SYSTEM = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
ASSET_TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
ASSET_REGISTRY = unreal.AssetRegistryHelpers.get_asset_registry()


def _build_anim_sequence_export_options():
    options = unreal.FbxExportOption()

    options.export_morph_targets = False
    options.export_local_time = False
    options.collision = False

    return options


def _create_spawnable(actor_path, sequence):
    """Создаёт spawnable в секвенции

    Parameters
    -----------
    actor_path:str
        Путь до объекта
    sequence: unreal.MovieSceneSequence
        Секвенция

    Returns
    ---------
    unreal.SequencerBindingProxy
        Binding объекта
    """
    actor = EDITOR_ASSET_SYSTEM.load_asset(actor_path)
    actor_binding = sequence.add_spawnable_from_instance(actor)

    transform_track = actor_binding.add_track(unreal.MovieScene3DTransformTrack)
    transform_section = transform_track.add_section()
    transform_section.set_start_frame_bounded(0)
    transform_section.set_end_frame_bounded(sequence.get_playback_end())

    return actor_binding


def _extract_number(cut_object):
    return int(cut_object[4][3:])


def _get_not_found_assets(content_metadata, sequence):
    invalid_assets = []

    for asset in content_metadata:
        if not find_binding_by_mfa_id(asset['id'], sequence):
            invalid_assets.append(asset)

    return invalid_assets


def _get_object_of_binding(binding_proxy, sequence):
    """Возвращает связанный с секвенцией объект

    Parameters
    -----------
    binding_proxy: unreal.SequencerBindingProxy
        Bindning актора
    sequence: unreal.MovieSceneSequence
        Секвенция

    Returns
    ---------
    unreal.Object
        Объект
    """
    return binding_proxy.get_object_template()

    # world = EDITOR_SYSTEM.get_editor_world()
    # bound_objects = unreal.SequencerTools().get_bound_objects(world, sequence,
    #                                                           [binding_proxy],
    #                                                           sequence.get_playback_range())
    #
    # for b_obj in bound_objects:
    #     return b_obj.bound_objects[0]


def _get_parent_binding(track, sequence=None):
    """Возвращает родительский binding трека

    Parameters
    -----------
    track: unreal.MovieSceneTrack
        Дочерний трек
    sequence: unreal.MovieSceneSequence
        Секвенция

    Returns
    ---------
    unreal.SequencerBindingProxy
        Binding
    """
    sequences = []

    if sequences:
        sequences.append(sequence)
    else:
        sequences = get_all_sequences()

    for sequence in sequences:
        bindings = sequence.get_bindings()

        for binding in bindings:
            if track in binding.get_tracks():
                return binding


def _get_parent_sequence_of_binding(binding):
    """Возвращает родительскую секвенцию у binding

    Parameters
    -----------
    binding: unreal.SequencerBindingProxy
       Bindning актора

    Returns
    ---------
    unreal.MovieSceneSequence
       Секвенция
    """
    return binding.sequence


def _get_parent_sequence_of_master_track(track):
    """Возвращает родительскую секвенцию у мастер-трек

    Parameters
    -----------
    track: unreal.MovieSceneTrack
      Мастер-трек

    Returns
    ---------
    unreal.MovieSceneSequence
      Секвенция
    """
    sequences = get_all_sequences()

    for sequence in sequences:
        if track in sequence.get_master_tracks():
            return sequence


def _get_parent_track(section, sequence):
    """Возвращает родительский трек секции

    Parameters
    -----------
    section: unreal.MovieSceneSection
        Секция
    sequence: unreal.MovieSceneSequence
      Секвенция

    Returns
    ---------
    unreal.MovieSceneTrack
      Мастер-трек
    """
    bindings = sequence.get_bindings()

    for binding in bindings:
        for track in binding.get_tracks():
            if section in track.get_sections():
                return track


def add_animation_to_binding(binding, animation_path, start_frame=0):
    """Добавляет анимацию актору секвенции

    Parameters
    -----------
    binding: unreal.SequencerBindingProxy
        Binding
    animation_path:str
        Путь до анимации в unreal-проекте
    start_frame: int
        Начальный кадр секции с анимацией

    Returns
    ---------
    unreal.MovieSceneTrack
     Трек анимации
    """
    animation_asset = unreal.AnimSequence.cast(unreal.load_asset(animation_path))

    params = unreal.MovieSceneSkeletalAnimationParams()
    params.set_editor_property('Animation', animation_asset)

    animation_track = binding.add_track(track_type=unreal.MovieSceneSkeletalAnimationTrack)

    sequence = binding.sequence

    animation_section = animation_track.add_section()
    animation_section.set_editor_property('Params', params)
    animation_section.set_range(start_frame, sequence.get_playback_end() - start_frame)

    return animation_track


def add_section(track, start_frame=None, end_frame=None):
    """Добавляет секцию в трек

    Parameters
    -----------
    track: unreal.MovieSceneTrack
        Трек
    start_frame: int
        Начальный фрейм. Если None, то ноль
    end_frame: int
        Конечный кадр. Если None, то последний кадр секвенции

    Returns
    ---------
    unreal.MovieSceneSection
     Секция
    """
    binding = _get_parent_binding(track)
    if binding:
        sequence = _get_parent_sequence_of_binding(binding)
    else:
        sequence = _get_parent_sequence_of_master_track(track)

    if start_frame is None:
        start_frame = 0

    if end_frame is None:
        end_frame = sequence.get_playback_end()

    section = track.add_section()
    section.set_range(start_frame, end_frame)

    return section


def add_to_cut_sequence(sequence, asset_path):
    actor_binding = _create_spawnable(asset_path, sequence)

    return actor_binding


def apply_metadata_to_asset(task_info, binding, sequence=None):
    set_binding_metadata(binding,
                         MFA_ID=str(uuid.uuid4()),
                         MFA_TASK_NAME=str(task_info['task_name']),
                         MFA_TASK_ID=str(task_info['task_id']),
                         MFA_TASK_ACTIVITY_ID=task_info['task_activity_id'],
                         MFA_FILE='',
                         # MFA_PUBLISH_PATH=cerebro.get_children_path_by_activity(
                         #     task_info['task_id'],
                         #     'rigging',
                         #     "PUBLISH"
                         # ).replace('\\', '/')
                         )


def cf_add_asset_to_sequence_by_asset_path(task_info, sequence, asset_path):
    """Добавляет уже загруженный объект в секвенцию по его asset_path. Записывает метадату. Выведет предупреждение в случае неудачи и вернёт ``None``

    Parameters
    -----------
    task_info: dict
        Task info ассета
    sequence: unreal.MovieSceneSequence
        Секвенция
    Returns
    ---------
    unreal.SequencerBindingProxy
        Binding актора
    """

    actor_binding = add_to_cut_sequence(sequence, asset_path)

    if not actor_binding:
        return

    apply_metadata_to_asset(task_info, actor_binding, sequence)

    return actor_binding


def cf_load_asset_to_sequence_by_meta(asset_metadata, sequence, bp=False):
    """Загружает ассет в секвенцию по его метадате

    Parameters
    ---------
    asset_metadata: dict
        Метадата ассета
    sequence: unreal.MovieSceneSequence
        Секвенция

    Returns
    ---------
    unreal.SequencerBindingProxy
       Bindning актора
    """
    task_info = cerebro.task_info_by_task_id(asset_metadata.get('task_id'))

    bindings = sequence.get_bindings()

    actor_binding = None

    actor_binding = find_binding_by_mfa_id(asset_metadata.get('id', None), sequence)

    if actor_binding:
        return actor_binding

    actor_binding = cf_load_asset_to_sequence_by_task_info(task_info, sequence, bp)
    if not actor_binding:
        return

    # bound_object = _get_object_of_binding(actor_binding, sequence)
    # ue_content.set_object_metadata(bound_object, MFA_ID=asset_metadata.get('id'))

    set_binding_metadata(actor_binding, MFA_ID=asset_metadata.get('id'))

    return actor_binding


def cf_load_asset_to_sequence_by_task_info(task_info, sequence, bp=False):
    """Загружает объект в секвенцию по его task_info. Записывает метадату. Выведет предупреждение в случае неудачи и вернёт ``None``

    Parameters
    -----------
    task_info: dict
        Task info ассета
    sequence: unreal.MovieSceneSequence
        Секвенция
    Returns
    ---------
    unreal.SequencerBindingProxy
        Binding актора
    """
    path = ue_path.cf_get_asset_fbx_path(task_info)

    if not path or not os.path.exists(path):
        unreal.log_warning(f'Unable to find path {path} for {task_info.get("task_name")}')
        return

    actor_binding = load_asset_to_sequence(path, sequence, task_info['task_activity_name'], task_info['task_name'], bp)

    if not actor_binding:
        return

    apply_metadata_to_asset(task_info, actor_binding, sequence)

    return actor_binding


def cf_make_cut_section(cut_dir, cut_ls_name, cut_task, shot_sequence, offset):
    """Создаёт секцию ката и секвенцию для него.Также записывает метадату для секвеции

    Parameters
    -----------
    cut_dir: str
        Директория секвенции ката
    cut_ls_name:
        Имя секвенции ката
    cut_task: list
        Список задачи ката по db. Используется для избежания дополнительного обращения к базе данных
    shot_sequence: unreal.MovieSceneSequence
        Секвецния шота
    offset: int
        Смещение секции на таймлайне



    Returns
    ---------
    unreal.MovieSceneSection
        Секция ката
    """
    cut_task_info = cerebro.task_info_by_task_id(cut_task[1])

    start_frame = metadata.get(cut_task_info, 'start_frame') + offset
    end_frame = metadata.get(cut_task_info, 'end_frame') + offset

    task_name = cut_task_info['task_name']
    task_id = cut_task_info['task_id']
    task_activity = cut_task_info['task_activity_name']

    cut_section = create_cut_section(cut_dir, cut_ls_name, shot_sequence)

    ue_content.set_asset_metadata(os.path.join(cut_dir, cut_ls_name), MFA_TASK_NAME=str(task_name),
                                  MFA_TASK_ID=str(task_id), MFA_TASK_ACTIVITY=task_activity, MFA_TYPE='CUT')

    cut_ls = cut_section.get_sequence()

    cut_ls.set_playback_start(0)
    cut_ls.set_playback_end(end_frame - offset)
    cut_section.set_range(start_frame, end_frame)

    return cut_section


def cf_make_episode_sequences(episode_task_info):
    """Генерирует все иерархию секвенций  эпизода

    Parameters
    -----------
    episode_task_info: dict
        Task info эпизода


    Returns
    ---------
    None
    """
    ep_ls_name = 'LS_' + episode_task_info['task_name']

    episode_dir = os.path.join(ue_path.get_episodes_path(), episode_task_info['task_name']).replace("\\", "/")

    episode_ls = create_level_sequence(episode_dir, ep_ls_name)
    episode_mt = create_master_track(episode_ls)

    ue_content.set_asset_metadata(os.path.join(episode_dir, ep_ls_name),
                                  MFA_TASK_NAME=str(episode_task_info['task_name']),
                                  MFA_TASK_ID=str(episode_task_info['task_id']),
                                  MFA_TASK_ACTIVITY=episode_task_info['task_activity_name'],
                                  MFA_TYPE='EPISODE')

    shot_tasks = cerebro.get_children_tasks(episode_task_info['task_id'], 'Shot')

    sorted_shots = sorted(shot_tasks, key=_extract_number)
    shot_tasks = sorted_shots
    with unreal.ScopedSlowTask(len(shot_tasks), "Episode creation/update") as slow_task:
        slow_task.make_dialog(True)  # Makes the dialog visible, if it isn't already

        shots_last_frame = 0
        for shot_task in shot_tasks:
            # shot_task_info = cerebro.task_info_by_task_id(shot_task[1])
            if slow_task.should_cancel():  # True if the user has pressed Cancel in the UI
                break

            shot_dir = os.path.join(episode_dir, shot_task[4]).replace("\\", "/")
            shot_ls_name = 'LS_' + episode_task_info['task_name'] + shot_task[4]

            shot_section = cf_make_shot_section(shot_dir, shot_ls_name, shot_task, episode_ls, shots_last_frame)

            shots_last_frame = shot_section.get_end_frame()

            slow_task.enter_progress_frame(1)

        episode_ls.set_playback_start(0)
        episode_ls.set_playback_end(shots_last_frame)
        episode_ls.set_view_range_end(shots_last_frame / 24)


def cf_make_shot_section(shot_dir, shot_ls_name, shot_task, episode_sequence, offset):
    """Создаёт секцию шота и секвенцию для него. Также записывает метадату для него

    Parameters
    -----------
    shot_dir: str
        Директория секвенции ката
    shot_ls_name:
        Имя секвенции ката
    shot_task: list
        Список задачи ката по db. Используется для избежания дополнительного обращения к базе данных
    episode_sequence: unreal.MovieSceneSequence
        Секвецния шота
    offset: int
        Смещение секции на таймлайне



    Returns
    ---------
    unreal.MovieSceneSection
        Секция шота
    """
    cut_tasks = cerebro.get_children_tasks(shot_task[1], 'Cut')

    shot_section = create_shot_section(shot_dir, shot_ls_name, episode_sequence)
    shot_ls = shot_section.get_sequence()

    ue_content.set_asset_metadata(os.path.join(shot_dir, shot_ls_name), MFA_TASK_NAME=str(shot_task[4]),
                                  MFA_TASK_ID=str(shot_task[1]), MFA_TASK_ACTIVITY=shot_task[6], MFA_TYPE='SHOT')

    sorted_cuts = sorted(cut_tasks, key=_extract_number)
    cut_tasks = sorted_cuts

    shot_range = [0, 100]
    cuts_last_frame = 0
    for cut_task in cut_tasks:
        cut_dir = os.path.join(shot_dir, cut_task[4]).replace("\\", "/")
        ep_name = ue_content.get_asset_metadata(episode_sequence.get_path_name(), 'MFA_TASK_NAME')
        cut_ls_name = 'LS_' + ep_name + shot_task[4] + cut_task[4]

        cut_section = cf_make_cut_section(cut_dir, cut_ls_name, cut_task, shot_ls, cuts_last_frame)

        cuts_last_frame = cut_section.get_end_frame()
        shot_range = [0, cuts_last_frame]

    shot_ls.set_playback_start(shot_range[0])
    shot_ls.set_playback_end(shot_range[1])

    start_frame = shot_range[0] + offset
    end_frame = shot_range[1] + offset

    shot_section.set_range(start_frame, end_frame)

    return shot_section


def cf_update_cut_metadata(cut_sequence):
    """Обновляет метадату ката в  Cerebro

    Parameters
    -----------

    cut_sequence: unreal.MovieSceneSequence
        секвецния ката


    Returns
    ---------
    None
    """
    if not cut_sequence:
        return

    cut_id = ue_content.get_asset_metadata(cut_sequence.get_path_name(), 'MFA_TASK_ID')
    if not cut_id:
        return

    cut_task_info = cerebro.task_info_by_task_id(cut_id)

    start_frame = cut_sequence.get_playback_start()
    end_frame = cut_sequence.get_playback_end()
    metadata.patch(cut_task_info, start_frame=start_frame, end_frame=end_frame)


def cf_update_cut_task_content_DEPRECATED(cut_sequence):
    """Обновляет контент ката в Cerebro

    Parameters
    ---------
    cut_sequence: unreal.MovieSceneSequence
        секвенция


    Returns
    ---------
    None
    """
    bindings = cut_sequence.get_bindings()

    objects = []
    for binding in bindings:
        obj = _get_object_of_binding(binding, cut_sequence)
        if obj:
            objects.append(obj)

    cut_task_id = ue_content.get_object_metadata(cut_sequence, 'MFA_TASK_ID')
    cut_task_info = cerebro.task_info_by_task_id(cut_task_id)

    cut_content = metadata.get(cut_task_info, 'content')

    def _find_asset_by_uuid(asset_id, content):
        for asset in content:
            if asset.get('id') == asset_id:
                return asset

    new_content = []
    uuids = []
    for obj in objects:
        asset_id = ue_content.get_object_metadata(obj, 'MFA_ID')
        asset = _find_asset_by_uuid(asset_id, cut_content)

        if asset:
            if asset['id'] in uuids:
                asset['id'] = uuid.uuid4()
                ue_content.set_object_metadata(obj, MFA_ID=asset['id'])
        else:
            asset = {
                'id': ue_content.get_object_metadata(obj, 'MFA_ID'),
                'file': ue_content.get_object_metadata(obj, 'MFA_FILE'),
                'task_name': ue_content.get_object_metadata(obj, 'MFA_TASK_NAME'),
                'task_id': ue_content.get_object_metadata(obj, 'MFA_TASK_ID'),
                'task_activity_id': ue_content.get_object_metadata(obj, 'MFA_TASK_ACTIVITY_ID'),
                'publish_path': ue_content.get_object_metadata(obj, 'MFA_PUBLISH_PATH'),
                'bake_transform': ''
            }

        uuids.append(asset['id'])
        new_content.append(asset)

    metadata.patch(cut_task_info, content=new_content)


def cf_update_cut_task_timings(cut_sequence):
    """Обновляет тайминги ката в Cerebro

    Parameters
    ---------
    cut_sequence: unreal.MovieSceneSequence
        секвенция


    Returns
    ---------
    None
    """
    if ue_content.get_asset_metadata(cut_sequence.get_path_name(), 'MFA_TYPE') != 'CUT':
        return

    cut_task_id = ue_content.get_asset_metadata(cut_sequence.get_path_name(), 'MFA_TASK_ID')
    cut_task_info = cerebro.task_info_by_task_id(cut_task_id)

    start_frame = 0
    end_frame = cut_sequence.get_playback_end()

    metadata.patch(cut_task_info, start_frame=start_frame, end_frame=end_frame)


def cf_update_episode_metadata(episode_task_info):
    """Обновляет метадату всей иерархии эпизода в Cerebro

    Parameters
    -----------

    episode_task_info: dict
        Task info эпизода


    Returns
    ---------
    None
    """
    ep_ls_name = 'LS_' + episode_task_info['task_name']
    episode_dir = os.path.join(ue_path.get_episodes_path(), episode_task_info['task_name']).replace("\\", "/")
    episode_ls = create_level_sequence(episode_dir, ep_ls_name)

    for track in episode_ls.find_master_tracks_by_type(unreal.MovieSceneCinematicShotTrack):
        for shot_section in track.get_sections():
            shot_sequence = shot_section.get_sequence()

            cf_update_shot_metadata(shot_sequence)


def cf_update_shot_metadata(shot_sequence):
    """Обновляет метадату всей иерархии шота в Cerebro

    Parameters
    -----------

    shot_sequence: unreal.MovieSceneSequence
        Секвенция шота

    Returns
    -----------
    None
    """
    if not shot_sequence:
        return

    if not ue_content.get_asset_metadata(shot_sequence.get_path_name(), 'MFA_TASK_ID'):
        return

    for track in shot_sequence.find_master_tracks_by_type(unreal.MovieSceneCinematicShotTrack):
        for cut_section in track.get_sections():
            cut_sequence = cut_section.get_sequence()

            cf_update_cut_metadata(cut_sequence)


def create_cut_section(cut_dir, cut_ls_name, shot_sequence):
    """Создаёт секцию ката и секвенцию для него

    Parameters
    -----------
    cut_dir: str
        Директория секвенции ката
    cut_ls_name:
        Имя секвенции ката
    shot_sequence: unreal.MovieSceneSequence
        Секвецния шота


    Returns
    ---------
    unreal.MovieSceneSection
        Секция ката
    """
    cut_ls = create_level_sequence(cut_dir, cut_ls_name)

    cut_section = get_parent_section_of_sequence(cut_ls, shot_sequence)
    if not cut_section:
        shot_mt = shot_sequence.find_master_tracks_by_type(unreal.MovieSceneTrack)[0]
        cut_section = add_section(shot_mt)
        cut_section.set_sequence(cut_ls)

    return cut_section


def create_level_sequence(destination_path, destination_name):
    """Создаёт секвенцию. Если она уже существует - возвращает на неё ссылку

    Parameters
    -----------
    destination_path: str
        Директория секвенции
    destination_name: str
        Имя секвенции

    Returns
    ---------
    unreal.MovieSceneSequence
        Секвенция ката
    """
    if ue_content.is_asset_exists(os.path.join(destination_path, destination_name).replace("\\", "/")):
        return unreal.load_asset(os.path.join(destination_path, destination_name).replace("\\", "/"))

    ue_path.create_dir(destination_path)

    sequence = ASSET_TOOLS.create_asset(asset_name=destination_name,
                                        package_path=destination_path,
                                        asset_class=unreal.LevelSequence,
                                        factory=unreal.LevelSequenceFactoryNew())

    return sequence


def duplicate_level_sequence(sequence_asset, destination_path, destination_name):
    """Создаёт секвенцию. Если она уже существует - возвращает на неё ссылку

    Parameters
    -----------
    destination_path: str
        Директория секвенции
    destination_name: str
        Имя секвенции

    Returns
    ---------
    unreal.MovieSceneSequence
        Секвенция ката
    """
    if ue_content.is_asset_exists(os.path.join(destination_path, destination_name).replace("\\", "/")):
        return unreal.load_asset(os.path.join(destination_path, destination_name).replace("\\", "/"))

    ue_path.create_dir(destination_path)

    sequence_asset = ASSET_TOOLS.duplicate_asset(asset_name=destination_name,
                                                 package_path=destination_path,
                                                 original_object=sequence_asset)

    return sequence_asset


def create_master_track(sequence):
    """Создаёт мастер трек в секвенции. Если он уже существует - возвращает на него ссылку

    Parameters
    -----------
    sequence:  unreal.MovieSceneSequence
        Секвенция

    Returns
    ---------
    unreal.MovieSceneCinematicShotTrack
        Мастер-трек
    """
    tracks = sequence.find_master_tracks_by_exact_type(unreal.MovieSceneCinematicShotTrack)
    if len(tracks) != 0:
        master_track = tracks[0]

        if master_track:
            return master_track

    return sequence.add_master_track(unreal.MovieSceneCinematicShotTrack)


def create_metadata_track(binding):
    metadata_track = binding.add_track(unreal.MovieSceneEventTrack)
    metadata_track.set_editor_property('display_name', 'mfa_metadata')
    # metadata_track.rename('mfa_metadata')
    metadata_track.set_editor_property('track_tint', unreal.Color(0, 0, 0, 1))

    return metadata_track


def create_shot_section(shot_dir, shot_ls_name, episode_sequence):
    """Создаёт секцию ката и секвенцию для него

   Parameters
   -----------
   shot_dir: str
       Директория секвенции шота
   shot_ls_name:
       Имя секвенции шота
   episode_sequence: unreal.MovieSceneSequence
       Секвецния эпизода


   Returns
   ---------
   unreal.MovieSceneSection
       Секция шота
   """
    shot_ls = create_level_sequence(shot_dir, shot_ls_name)

    shot_mt = create_master_track(shot_ls)

    shot_section = get_parent_section_of_sequence(shot_ls, episode_sequence)
    if not shot_section:
        episode_mt = episode_sequence.find_master_tracks_by_type(unreal.MovieSceneTrack)[0]
        shot_section = add_section(episode_mt)
        shot_section.set_sequence(shot_ls)

    return shot_section


def export_animation_track(bindings, sequence, fbx_path, root_sequence=None):
    world = EDITOR_SYSTEM.get_editor_world()
    anim_seq_export_options = _build_anim_sequence_export_options()

    params = unreal.SequencerExportFBXParams()

    if not root_sequence:
        root_sequence = get_current_level_sequence()

    tracks = []

    # for binding in bindings:
    #     tracks.append(binding.get_tracks())

    params.bindings = bindings
    params.sequence = sequence
    params.override_options = anim_seq_export_options
    params.world = world
    params.root_sequence = root_sequence
    params.fbx_file_name = fbx_path
    # params.master_tracks = tracks

    unreal.SequencerTools.export_level_sequence_fbx(params)


def export_binding_as_fbx(binding, fbx_path, root_sequence=None):
    sequence = _get_parent_sequence_of_binding(binding)

    data = ue_content.get_all_object_metadata(_get_object_of_binding(binding, sequence))

    binding = LS_SYSTEM.convert_to_possessable(binding)
    bindings = [binding]

    root_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence() if not root_sequence else root_sequence
    export_fbx(bindings, sequence, fbx_path, root_sequence=root_sequence)

    binding = LS_SYSTEM.convert_to_spawnable(binding)[0]
    ue_content.set_object_metadata_with_dict(_get_object_of_binding(binding, sequence), data)

    return binding


def export_fbx(bindings, sequence, fbx_path, root_sequence=None, master_tracks=None, override_options=None, world=None):
    root_sequence = sequence if not root_sequence else root_sequence
    master_tracks = sequence.get_master_tracks() if not master_tracks else master_tracks
    override_options = ue_content._build_export_options() if not override_options else override_options
    world = EDITOR_SYSTEM.get_editor_world() if not world else world

    ExportFBXParams = unreal.SequencerExportFBXParams()
    ExportFBXParams.world = world
    ExportFBXParams.sequence = sequence
    ExportFBXParams.root_sequence = root_sequence
    ExportFBXParams.bindings = bindings
    ExportFBXParams.master_tracks = master_tracks
    ExportFBXParams.override_options = override_options
    ExportFBXParams.fbx_file_name = fbx_path

    unreal.SequencerTools.export_level_sequence_fbx(ExportFBXParams)


def export_fbx_animation_in_range(bindings, sequence, fbx_path, start_frame, end_frame, root_sequence=None):
    s_frame, e_frame = sequence.get_playback_start(), sequence.get_playback_end()

    sequence.set_playback_start(start_frame)
    sequence.set_playback_end(end_frame)
    export_animation_track(bindings, sequence, fbx_path, root_sequence)

    sequence.set_playback_start(s_frame)
    sequence.set_playback_end(e_frame)


def export_fbx_animation_under_cameracut(bindings, sequence, fbx_path, camera_cut, root_sequence=None):
    start_frame = camera_cut.get_start_frame()
    end_frame = camera_cut.get_end_frame()

    export_fbx_animation_in_range(bindings, sequence, fbx_path, start_frame, end_frame, root_sequence)


def find_binding_by_mfa_id(mfa_id, sequence):
    bindings = sequence.get_spawnables()

    for binding in bindings:
        obj_id = get_metadata_section(binding, 'MFA_ID')
        if str(obj_id) == str(mfa_id):
            return binding


def find_metadata_track(binding):
    tracks = binding.find_tracks_by_exact_type(unreal.MovieSceneEventTrack)

    for track in tracks:
        if track.get_display_name() == 'mfa_metadata':
            return track


def find_rendered_objects(camera_cut_section: unreal.MovieSceneSection, sequence, step=10):
    start_frame = camera_cut_section.get_start_frame() + 1
    end_frame = camera_cut_section.get_end_frame()

    bindings = sequence.get_spawnables()

    rendered_bindings = list()
    with unreal.ScopedSlowTask(end_frame - start_frame,
                               f'Scanning section {camera_cut_section.get_name()}') as slow_task:
        slow_task.make_dialog(True)
        for frame in range(start_frame, end_frame, step):
            unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(frame)
            for binding in bindings:
                binding_id = sequence.get_portable_binding_id(sequence, binding)
                objects = [binding.get_object_template()]

                if is_binding_visible_on_frame(binding, frame):
                    rendered_bindings.append(binding)
                    bindings.remove(binding)
            slow_task.enter_progress_frame(step)

    return rendered_bindings


def find_valid_assets_under_camera_cut_section(camera_cut_section, sequence):
    bindings = find_rendered_objects(camera_cut_section, sequence)
    valid_objects = []
    for binding in bindings:
        if get_metadata_section(binding, 'MFA_ID'):
            valid_objects.append(binding)

    return valid_objects


def get_all_sequences():
    """Возвращает список всех секвенций в проекте

    Parameters
    -----------


    Returns
    ---------
    list[unreal.MovieSceneSequence]
        Список секвенций в проекте
    """
    list_of_paths = ue_content.get_all_assets_of_python_class(unreal.MovieSceneSequence)

    sequences = []

    for path in list_of_paths:
        sequences.append(EDITOR_ASSET_SYSTEM.load_asset(path.package_name))

    return sequences


def get_camera_cut_index(camera_cut_section, sequence):
    track = sequence.find_master_tracks_by_exact_type(unreal.MovieSceneCameraCutTrack)[0]
    sections: list = track.get_sections()

    return sections.index(camera_cut_section)


def get_camera_cut_sections(sequence: unreal.MovieSceneSequence):
    tracks = sequence.find_master_tracks_by_type(unreal.MovieSceneCameraCutTrack)

    sections = []
    for track in tracks:
        for section in track.get_sections():
            sections.append(section)

    return sections


def get_camera_of_camera_cut(camera_cut, sequence):
    camera_binding_id = camera_cut.get_camera_binding_id()
    bindning = sequence.find_binding_by_id(camera_binding_id.get_editor_property('guid'))

    return bindning


def get_current_level_sequence():
    """Возвращает текущую открытую секвенцию


   Returns
   ---------
   unreal.MovieSceneSequence
       Секвенция
   """
    return unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()


def get_cut_sequence_by_id(task_id):
    """Возвращает секвенцию ката по ``ID`` задачи

    Parameters
    ---------
    task_id: int
        ``ID``

    Returns
    ---------
    unreal.MovieSceneSequence
       Секвенция ката
    """
    sequences = get_all_sequences()

    for sequence in sequences:
        if str(ue_content.get_asset_metadata(sequence.get_path_name(), 'MFA_TASK_ID')) == str(task_id):
            return sequence


def get_focused_level_sequence() -> unreal.MovieSceneSequence:
    """Возвращает текущую открытую секвенцию внутри другой секвенции


   Returns
   ---------
   unreal.MovieSceneSequence
       Секвенция
   """
    return unreal.LevelSequenceEditorBlueprintLibrary.get_focused_level_sequence()


def get_invalid_spawnables(sequence, bindings=None):
    invalid_spawnables = []

    if not bindings:
        bindings = sequence.get_spawnables()
    for binding in bindings:
        mfa_id = get_metadata_section(binding, 'MFA_ID')
        if not mfa_id:
            invalid_spawnables.append(binding)

    return invalid_spawnables


def get_metadata_section(binding, key):
    track = find_metadata_track(binding)
    if not track:
        return None

    def _find_section_by_key():
        sections = track.get_sections()
        for section in sections:
            if section.get_name().split(':')[0] == key:
                return section

    section = _find_section_by_key()
    if not section:
        return None

    key_value = section.get_name()

    if ':' not in key_value:
        return None

    return key_value.split(':')[1]


def get_parent_section_of_sequence(child_sequence, sequence):
    """Возвращает родительскую секцию секвенции

    Parameters
    ---------
    child_sequence: unreal.MovieSceneSequence
        Дочерняя секвенция
    sequence: unreal.MovieSceneSequence
        Секвенция, в которой расположена эта секция

    Returns
    ---------
    unreal.MovieSceneSection
       Секция
    """
    master_tracks = sequence.find_master_tracks_by_type(unreal.MovieSceneSubTrack)

    for track in master_tracks:
        sections = track.get_sections()
        for section in sections:
            if section.get_sequence() == child_sequence:
                return section

    return None


def get_selected_sections():
    """Возвращает выбранные секции


    Returns
    ---------
    list[unreal.MovieSceneSection]
       Список секций
    """
    return unreal.LevelSequenceEditorBlueprintLibrary.get_selected_sections()


def get_sub_sections(sequence: unreal.MovieSceneSequence):
    tracks = sequence.find_master_tracks_by_type(unreal.MovieSceneSubTrack)

    sections = []
    for track in tracks:
        for section in track.get_sections():
            sections.append(section)

    return sections


def get_sub_sequences(sequence: unreal.MovieSceneSequence):
    tracks = sequence.find_master_tracks_by_type(unreal.MovieSceneSubTrack)

    sequences = []
    for track in tracks:
        for section in track.get_sections():
            sequences.append(section.get_sequence())

    return sequences


def get_valid_spawnables(sequence, bindings=None):
    valid_spawnables = []

    if not bindings:
        bindings = sequence.get_spawnables()
    for binding in bindings:
        mfa_id = get_metadata_section(binding, 'MFA_ID')
        if mfa_id:
            valid_spawnables.append(binding)

    return valid_spawnables


def load_animation_to_sequence(path, actor_binding, sequence, activity='', start_frame=0):
    """Загружает файл анимации в секвенцию

    Parameters
    ---------
    path: str
        путь до файла
    actor_binding: unreal.SequencerBindingProxy
        binding актора для которого загружается анимация
    sequence: unreal.MovieSceneSequence
        секвенция
    activity: str
        Вид деятельности задачи анимации

    Returns
    ---------
    None
    """

    obj = _get_object_of_binding(actor_binding, sequence)

    if obj.static_class() == unreal.Pawn.static_class():
        world = LS_SYSTEM.get_world()
        pos_binding = LS_SYSTEM.convert_to_possessable(actor_binding)
        obj = unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(sequence.get_binding_id(pos_binding))[0]

        skeletal_mesh_component = unreal.Actor.cast(obj).get_component_by_class(unreal.SkeletalMeshComponent)
        skm = skeletal_mesh_component.get_skeletal_mesh_asset()
        skeleton = skm.skeleton
        component_binding = sequence.add_possessable(skeletal_mesh_component)
        actor_binding = LS_SYSTEM.convert_to_spawnable(pos_binding)
        actor_binding = component_binding
    else:
        skm = obj.skeletal_mesh_component.get_skeletal_mesh_asset()
        skeleton = skm.skeleton

    if not skeleton:
        skeleton = ue_content.find_skeleton(os.path.dirname(skm.get_path_name()))
    if not skeleton:
        unreal.log_warning(
            f"Unable to load animation to {sequence.get_fname()}: can't find skeleton for {actor_binding.get_name()}")
        return

    anim_path = ue_content.load_animation_to_project(path, sequence,
                                                     skeleton.get_path_name(), activity)
    if not anim_path:
        return

    return add_animation_to_binding(actor_binding, anim_path, start_frame)


def load_asset_to_sequence(path, sequence, activity, name, bp=False):
    """Загружает файл ассета в секвенцию

    Parameters
    ---------
    path: str
        путь до файла
    sequence: unreal.MovieSceneSequence
        секвенция
    activity: str
        Вид деятельности задачи анимации
    name: str
        Имя ассета

    Returns
    ---------
    unreal.SequencerBindingProxy
        Bindning актора
    """
    if not os.path.exists(path):
        return
    actor_paths = ue_content.load_asset_to_project(path, activity, name)
    if not actor_paths:
        return

    actor_path = actor_paths[-1]
    print(actor_path)
    if bp:
        bp_path = ue_path.get_bp_path_from_sekeletal_path(actor_path)
        if not ue_path.is_asset_exists(bp_path):
            unreal.log_warning(
                f"Unable to find bp in {bp_path}")
        actor_path = bp_path if ue_path.is_asset_exists(bp_path) else actor_path

    actor_binding = add_to_cut_sequence(sequence, actor_path)

    return actor_binding


def set_binding_metadata(binding, **kwargs):
    for key, value in kwargs.items():
        set_metadata_section(binding, str(key), str(value))


def set_metadata_section(binding, key, value):
    track = find_metadata_track(binding)
    if not track:
        track = create_metadata_track(binding)

    def _find_section_by_key():
        sections = track.get_sections()
        for section in sections:
            if section.get_name().split(':')[0] == key:
                return section

    section = _find_section_by_key()
    if not section:
        section = track.add_event_trigger_section()

    section.set_is_active(False)
    section.rename(name=f'{key}:{value}')


def validate_content_in_sequence(sequence_content, cut_content: list, sequence):
    def _find_asset_by_uuid(asset_id, content):
        for asset in content:
            if asset.get('id') == asset_id:
                return asset

    def _find_asset_by_task_name(asset_name, content):
        for asset in content:
            if asset.get('task_name') == asset_name:
                return asset

    uuids = []

    unbound_content = []
    unfound_cut_content = cut_content.copy()
    for seq_asset in sequence_content:

        seq_asset['task_activity_id'] = int(seq_asset.get('task_activity_id'))
        seq_asset['task_id'] = int(seq_asset.get('task_id'))

        if seq_asset.get('id') in uuids:
            binding = find_binding_by_mfa_id(seq_asset.get('id'), sequence)
            new_id = str(uuid.uuid4())
            seq_asset['id'] = new_id
            if binding:
                set_binding_metadata(binding, MFA_ID=new_id)

        uuids.append(seq_asset.get('id'))

        founded_asset = _find_asset_by_uuid(seq_asset.get('id'), cut_content)
        if founded_asset:
            seq_asset['file'] = founded_asset.get('file')
            unfound_cut_content.pop(unfound_cut_content.index(founded_asset))
            continue

        unbound_content.append(seq_asset)

    for unbound_asset in unbound_content:
        founded_asset = _find_asset_by_task_name(unbound_asset.get('task_name'), unfound_cut_content)
        if founded_asset:
            binding = find_binding_by_mfa_id(unbound_asset.get('id'), sequence)
            # unbound_asset['id'] = founded_asset.get('id')
            unbound_asset['file'] = founded_asset.get('file')
            if not binding:
                unreal.log_warning(f'Unable to find binding by id: {unbound_asset.get("id")}')
                continue

            # set_binding_metadata(binding, MFA_ID=founded_asset.get('id'))
    for asset in cut_content:
        if asset.get('task_activity_id') == settings.ACTIVITIES.get('Location'):
            if not _find_asset_by_task_name(asset.get('task_name'), sequence_content):
                sequence_content.append(asset)
                break


def create_temp_lvl_sequence():
    # Create a Level Sequence with name LevelSequenceName in root content folder

    if ue_path.is_asset_exists('/Game/_temp_sequence_mfa'):
        return unreal.load_asset('/Game/_temp_sequence_mfa')

    level_sequence = ASSET_TOOLS.create_asset(asset_name="_temp_sequence_mfa", package_path="/Game/",
                                              asset_class=unreal.LevelSequence.static_class(),
                                              factory=unreal.LevelSequenceFactoryNew())
    level_sequence.set_display_rate(unreal.FrameRate(24))

    track = level_sequence.add_master_track(unreal.MovieSceneCinematicShotTrack)
    section: unreal.MovieSceneSection = track.add_section()
    section.set_start_frame(0)
    section.set_end_frame(1000)

    return level_sequence


def remove_temp_lvl_sequence():
    # EDITOR_ASSET_SYSTEM.save_asset('/Game/_temp_sequence_mfa._temp_sequence_mfa')
    EDITOR_ASSET_SYSTEM.delete_loaded_asset(unreal.load_asset('/Game/_temp_sequence_mfa._temp_sequence_mfa'))


def build_capture_settings(sequence_path, start_frame, end_frame, output_dir, video_filename,
                           audio_filename):
    capture_settings = unreal.AutomatedLevelSequenceCapture()
    capture_settings.level_sequence_asset = unreal.SoftObjectPath(sequence_path)

    capture_settings.set_audio_capture_protocol_type(
        unreal.load_class(None, '/Script/MovieSceneCapture.MasterAudioSubmixCaptureProtocol'))
    capture_settings.get_audio_capture_protocol().file_name = audio_filename
    capture_settings.custom_start_frame = unreal.FrameNumber(start_frame)
    capture_settings.custom_end_frame = unreal.FrameNumber(end_frame)
    capture_settings.use_custom_end_frame = True
    capture_settings.use_custom_start_frame = True
    capture_settings.settings.cinematic_engine_scalability = False
    capture_settings.settings.output_directory = unreal.DirectoryPath(output_dir)
    capture_settings.settings.output_format = video_filename
    capture_settings.settings.overwrite_existing = True

    capture_settings.use_separate_process = False
    capture_settings.write_final_cut_pro_xml = False
    capture_settings.write_edit_decision_list = False

    return capture_settings


def render_sequence_to_movie_and_audio(sequence_path, start_frame, end_frame, output_dir, video_filename,
                                       audio_filename, callback_func=None):
    capture_settings = build_capture_settings(sequence_path, start_frame, end_frame, output_dir, video_filename,
                                              audio_filename)

    global callback
    callback = unreal.OnRenderMovieStopped()
    if callback_func:
        callback.bind_callable(callback_func)
    try:
        print("Rendering to movie...")
        unreal.SequencerTools.render_movie(capture_settings, callback)
    except Exception as e:
        print("Python Caught Exception:")
        print(e)


def is_binding_visible_on_frame(binding: unreal.MovieSceneBindingProxy, frame):
    tracks = binding.find_tracks_by_exact_type(unreal.MovieSceneVisibilityTrack.static_class())
    if not tracks:
        return True

    for track in tracks:
        sections = track.get_sections()
        for section in sections:
            channels = section.get_all_channels()
            for channel in channels:
                range = unreal.SequencerScriptingRange(has_start_value=True,
                                                       has_end_value=True)
                range.set_start_frame(frame)
                range.set_end_frame(frame + 24)

                framerate = unreal.FrameRate(numerator=1)
                keys = channel.get_keys()

                if not keys:
                    return channel.get_default()

                closest_key = keys[0]
                for key in keys:
                    frame_numnder = key.get_time().frame_number.value
                    if frame_numnder <= frame and frame_numnder > closest_key.get_time().frame_number.value:
                        closest_key = key

                if closest_key.get_value():
                    return True

    return False


def is_binding_spawned(binding):
    tracks = binding.find_tracks_by_exact_type(unreal.MovieSceneSpawnTrack.static_class())
    for track in tracks:
        for s in track.get_sections():
            for c in s.get_all_channels():
                return c.get_default()

    return False


def get_camera_cut_at_frame(frame):
    sequence = get_focused_level_sequence()
    tracks = sequence.find_master_tracks_by_exact_type(unreal.MovieSceneCameraCutTrack.static_class())
    closet_sec = None
    for track in tracks:
        for section in track.get_sections():
            if section.get_start_frame() <= frame < section.get_end_frame():
                closet_sec = section

    return closet_sec


def toggle_hidden_under_section_range(binding: unreal.MovieSceneBindingProxy, section):
    start_frame = section.get_start_frame()
    end_frame = section.get_end_frame()

    def get_key_at_frame(channel, frame):
        for key in channel.get_keys():
            if key.get_time().frame_number.value == frame:
                return key

    visibility_tracks = binding.find_tracks_by_exact_type(unreal.MovieSceneVisibilityTrack.static_class())
    if not visibility_tracks:
        track = binding.add_track(unreal.MovieSceneVisibilityTrack.static_class())
        sec = track.add_section()
        visibility_tracks.append(track)

    for track in visibility_tracks:
        for section in track.get_sections():
            for channel in section.get_all_channels():
                channel.add_key(unreal.FrameNumber(-5),
                                True)

                start_key = get_key_at_frame(channel, start_frame)

                if start_key:
                    start_key.set_value(not start_key.get_value())
                else:
                    channel.add_key(unreal.FrameNumber(start_frame),
                                    False)

                end_key = get_key_at_frame(channel, end_frame)
                if not end_key:
                    channel.add_key(unreal.FrameNumber(end_frame),
                                    True)


def build_sequence_import_fbx_settings():
    import_settings = unreal.MovieSceneUserImportFBXSettings()

    import_settings.set_editor_property('convert_scene_unit', True)
    import_settings.set_editor_property('create_cameras', False)
    import_settings.set_editor_property('force_front_x_axis', False)
    import_settings.set_editor_property('import_uniform_scale', 1)
    import_settings.set_editor_property('reduce_keys', False)
    import_settings.set_editor_property('match_by_name_only', False)
    import_settings.set_editor_property('replace_transform_track', True)
    return import_settings


def create_and_import_camera_in_sequence(filepath, sequence, name=None):
    if not name:
        name = os.path.basename(name).split('.')[0]

    camera_object = unreal.EditorLevelLibrary().spawn_actor_from_class(unreal.CineCameraActor.static_class(),
                                                                       unreal.Vector())
    unreal.Actor.cast(camera_object).set_actor_label(name)
    camera_binding = sequence.add_possessable(camera_object)

    world = EDITOR_SYSTEM.get_editor_world()
    import_settings = build_sequence_import_fbx_settings()

    unreal.SequencerTools.import_level_sequence_fbx(world, sequence, [camera_binding], import_settings, filepath)

    LS_SYSTEM.convert_to_spawnable(camera_binding)


def toggle_hidden_under_current_camera_cut():
    frame = unreal.LevelSequenceEditorBlueprintLibrary.get_current_local_time()
    cc = get_camera_cut_at_frame(frame)

    bindings = unreal.LevelSequenceEditorBlueprintLibrary.get_selected_bindings()

    for binding in bindings:
        toggle_hidden_under_section_range(binding, cc)


def get_vector_to_pixel_norm_coord_position(normalized_x, normalized_y, camera_actor: unreal.CineCameraActor):
    camera_component = unreal.CineCameraComponent(camera_actor.camera_component)
    camera_view = camera_component.get_camera_view(0)
    view_matrix, projection_matrix, vp_matrix = unreal.GameplayStatics.get_view_projection_matrix(camera_view)

    clip_space_x = view_matrix * normalized_x
    clip_space_y = view_matrix * normalized_y

    near_plane = vp_matrix.get_frustum_near_plane()

    view_space_x = view_matrix.get_inverse() * clip_space_x
    view_space_y = view_matrix.get_inverse() * clip_space_y

    print(near_plane)


def move_track(track: unreal.MovieSceneTrack, offset):
    sections = track.get_sections()

    for section in sections:

        property_track = False
        try:
            section.get_end_frame()
        except:
            property_track = True

        if not isinstance(track, unreal.MovieScenePropertyTrack) and not property_track:

            section.set_start_frame(section.get_start_frame() + offset)
            section.set_end_frame(section.get_end_frame() + offset)

        else:
            for channel in section.get_all_channels():
                keys: list = list(channel.get_keys())

                if offset > 0:
                    keys.reverse()
                for key in keys:
                    key.set_time(key.get_time().frame_number + offset)


def trim_track(track: unreal.MovieSceneTrack, start_frame, end_frame):
    def _get_closest_left_key(keys, frame):
        closet_key = None
        for key in keys:
            if key.get_time().frame_number.value <= frame:
                if not closet_key:
                    closet_key = key
                    continue

                if key.get_time().frame_number.value > closet_key.get_time().frame_number.value:
                    closet_key = key
        return closet_key

    def _get_closest_right_key(keys, frame):
        closet_key = None
        for key in keys:
            if key.get_time().frame_number.value >= frame:
                if not closet_key:
                    closet_key = key
                    continue

                if key.get_time().frame_number.value < closet_key.get_time().frame_number.value:
                    closet_key = key
        return closet_key

    def _get_keys_inside_range(keys, start, end):
        keys_in_range = []
        for key in keys:
            if start < key.get_time().frame_number.value < end:
                keys_in_range.append(key)

        return keys_in_range

    sections = track.get_sections()

    for section in sections:

        property_track = False
        try:
            section.get_end_frame()
        except:
            property_track = True

        if not isinstance(track, unreal.MovieScenePropertyTrack) and not property_track:

            if section.get_start_frame() > end_frame or section.get_end_frame() < start_frame:
                track.remove_section(section)
                continue

            if section.get_start_frame() < start_frame:
                if hasattr(section, 'params'):
                    if hasattr(section.params, 'start_frame_offset'):
                        cur_offset = section.params.start_frame_offset.value
                        start_frame_offset = cur_offset + abs(start_frame - section.get_start_frame())
                        section.params.start_frame_offset = unreal.FrameNumber(start_frame_offset) * 1000

                section.set_start_frame(start_frame)

            if section.get_end_frame() > end_frame:
                section.set_end_frame(end_frame)


        else:
            for channel in section.get_all_channels():
                keys: list = list(channel.get_keys())
                if len(keys) == 1:
                    for key in keys:
                        key.set_time(unreal.FrameNumber((start_frame + end_frame) / 2))

                keys_to_keep = _get_keys_inside_range(keys, start_frame, end_frame)
                closest_left = _get_closest_left_key(keys, start_frame)
                if closest_left is not None:
                    if not hasattr(closest_left, 'get_interpolation_mode') or \
                            closest_left.get_interpolation_mode() == unreal.RichCurveInterpMode.RCIM_CONSTANT:
                        closest_left.set_time(unreal.FrameNumber(start_frame))
                    keys_to_keep.append(closest_left)
                closest_right = _get_closest_right_key(keys, end_frame)
                if closest_right is not None:
                    if not hasattr(closest_right, 'get_interpolation_mode') or \
                            closest_right.get_interpolation_mode() == unreal.RichCurveInterpMode.RCIM_CONSTANT:
                        closest_right.set_time(unreal.FrameNumber(end_frame))
                    keys_to_keep.append(closest_right)

                for key in keys:
                    if key not in keys_to_keep:
                        channel.remove_key(key)


def cut_sequence(sequence: unreal.MovieSceneSequence, start_frame, end_frame):
    bindings = sequence.get_bindings()
    offset = start_frame
    with unreal.ScopedSlowTask(len(bindings), f'Clearing  camera cuts in {sequence.get_name()}...') as slow_task:
        slow_task.make_dialog(True)  # Makes the dialog visible, if it isn't already
        for binding in bindings:
            for track in binding.get_tracks():
                trim_track(track, start_frame, end_frame)
                move_track(track, -offset)

                slow_task.enter_progress_frame(1)


def make_single_camera_cut(camera_cut_section, sequence: unreal.MovieSceneSequence):
    camera_cut_tracks = sequence.find_master_tracks_by_type(
        unreal.MovieSceneCameraCutTrack.static_class())
    with unreal.ScopedSlowTask(100, f'Clearing  camera cuts in {sequence.get_name()}...') as slow_task:
        slow_task.make_dialog(True)  # Makes the dialog visible, if it isn't already
        for camera_cut_track in camera_cut_tracks:

            offset = -camera_cut_section.get_start_frame()

            for section in camera_cut_track.get_sections():
                section.set_is_locked(False)
                if section != camera_cut_section:
                    camera_binding = get_camera_of_camera_cut(section, sequence)
                    for child in camera_binding.get_child_possessables():
                        child.remove()
                    camera_binding.remove()
                    camera_cut_track.remove_section(section)

                slow_task.enter_progress_frame(5)

            move_track(camera_cut_track, offset)


def clear_cut_sequence(camera_cut_section_index, sequence):
    for i, camera_cut_section in enumerate(get_camera_cut_sections(sequence)):

        if i != camera_cut_section_index:
            continue

        s, e = camera_cut_section.get_start_frame(), camera_cut_section.get_end_frame()

        cut_sequence(sequence, s, e)
        make_single_camera_cut(camera_cut_section, sequence)

        sequence.set_playback_start(0)
        sequence.set_playback_end(e - s)


def cut_hierarchy_of_sequences(root_sequence: unreal.MovieSceneSequence, callback=None):
    ren_sequence = create_level_sequence(os.path.dirname(root_sequence.get_path_name()).replace('\\', '/'),
                                         root_sequence.get_name() + '_ren')
    shot_tracks: unreal.Array[unreal.MovieSceneCinematicShotTrack] = root_sequence.find_master_tracks_by_type(
        unreal.MovieSceneCinematicShotTrack.static_class())
    if not shot_tracks:
        for track in ren_sequence.get_master_tracks():
            ren_sequence.remove_master_track(track)

        shot_track = ren_sequence.add_master_track(unreal.MovieSceneCinematicShotTrack.static_class())

        for i, cc_section in enumerate(get_camera_cut_sections(root_sequence)):
            cut_sequence_dir = os.path.join(os.path.dirname(root_sequence.get_path_name()),
                                            'Cuts').replace('\\', '/')
            cut_sequence_name = root_sequence.get_name().split('_')[0] + f'cut' + ue_path._format_shotcut_number(
                i + 1) + '_mst_ren'

            cut_ren_sequence = duplicate_level_sequence(root_sequence, cut_sequence_dir, cut_sequence_name)

            clear_cut_sequence(i, cut_ren_sequence)

            shot_section = shot_track.add_section()
            shot_section.set_sequence(cut_ren_sequence)
            shot_section.set_range(cc_section.get_start_frame(), cc_section.get_end_frame())

            ren_sequence.set_playback_end(shot_section.get_end_frame())

            clear_invisible_props(cut_ren_sequence)
            make_all_folder_names_upper_case(cut_ren_sequence)

            if callback:
                callback()

        return ren_sequence

    for track in shot_tracks:
        ren_shot_track = ren_sequence.add_master_track(unreal.MovieSceneCinematicShotTrack.static_class())
        for section in track.get_sections():
            new_sequence = cut_hierarchy_of_sequences(section.get_sequence(), callback)
            shot_section = ren_shot_track.add_section()
            shot_section.set_sequence(new_sequence)
            shot_section.set_range(section.get_start_frame(), section.get_end_frame())
            ren_sequence.set_playback_end(shot_section.get_end_frame())

    return ren_sequence


def make_cuts_from_selected_sequence():
    if unreal.EditorDialog.show_message('Cutter',
                                        unreal.Text(
                                            f"Создать Ren-секвенции?"),
                                        unreal.AppMsgType.YES_NO,
                                        unreal.AppReturnType.NO) == unreal.AppReturnType.YES:

        for asset in unreal.EditorUtilityLibrary.get_selected_assets():
            try:
                sequence = unreal.MovieSceneSequence.cast(asset)
            except:
                continue

            with unreal.ScopedSlowTask(1000, f'Cutting {sequence.get_name()}...') as slow_task:
                slow_task.make_dialog(True)

                def callback_func():
                    slow_task.enter_progress_frame(1)

                cut_hierarchy_of_sequences(sequence, callback_func)


def get_hierarchy_from_root_sequence():
    sequence = get_current_level_sequence()

    if not sequence:
        return {}

    shot_sequences = get_sub_sequences(sequence)
    shots_hierarchy = {}

    for seq in shot_sequences:
        cut_sequences = get_sub_sequences(seq)
        if cut_sequences:
            cut_sections = get_sub_sections(seq)
            cut_lvl_sequences_paths = {}

            for i, cut_seq in enumerate(cut_sequences):
                section = cut_sections[i]
                end_frame = section.get_end_frame() - section.get_start_frame()
                cut_lvl_sequences_paths[cut_seq.get_path_name()] = {
                    'cut_timings': [0, end_frame - 1]
                }

            shots_hierarchy[seq.get_path_name()] = cut_lvl_sequences_paths
        else:
            cut_sections = get_camera_cut_sections(seq)
            cut_lvl_sequences_paths = {}

            for i, cut_seq in enumerate(cut_sections):
                binding_id = cut_seq.get_camera_binding_id().get_editor_property('guid')
                binding_name = seq.find_binding_by_id(binding_id).get_name()

                section = cut_sections[i]
                end_frame = section.get_end_frame() - section.get_start_frame()
                cut_lvl_sequences_paths[binding_name] = {
                    'cut_timings': [0, end_frame - 1]
                }

            shots_hierarchy[seq.get_path_name()] = cut_lvl_sequences_paths
    return {
        sequence.get_path_name(): shots_hierarchy
    }


def make_all_folder_names_upper_case(sequence: unreal.MovieSceneSequence):
    folders = sequence.get_root_folders_in_sequence()
    for folder in folders:
        new_name = unreal.Name(str(folder.get_folder_name()).upper())
        folder.set_folder_name(new_name)


def clear_invisible_props(sequence: unreal.MovieSceneSequence):
    for binding in sequence.get_spawnables():
        if binding.get_object_template().static_class() == unreal.StaticMeshActor.static_class():
            if not is_binding_visible(binding) or not is_binding_spawned(binding):
                for child in binding.get_child_possessables():
                    child.remove()
                binding.remove()


def is_binding_visible(binding, start_frame=None, end_frame=None):
    tracks = binding.find_tracks_by_exact_type(unreal.MovieSceneVisibilityTrack.static_class())
    sequence = binding.sequence

    if not tracks:
        return True

    if start_frame is None:
        start_frame = sequence.get_playback_start()
    if end_frame is None:
        end_frame = sequence.get_playback_end() - 1

    for track in tracks:
        sections = track.get_sections()
        for section in sections:
            channels = section.get_all_channels()
            for channel in channels:
                keys = channel.get_keys()
                for key in keys:

                    if start_frame <= key.get_time().frame_number.value <= end_frame:
                        if key.get_value():
                            return True
    return False


def get_skm_bindings(sequence, bindings=None):
    if not bindings:
        bindings = unreal.LevelSequenceEditorBlueprintLibrary.get_selected_bindings()

    skm_bindings = []
    for binding in bindings:
        obj = unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(sequence.get_binding_id(binding))[0]
        if obj.static_class() == unreal.SkeletalMeshActor.static_class():
            skm_bindings.append(binding)

    return skm_bindings

def get_skm_and_skeleton_of_binding(binding, sequence):
    obj = unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(sequence.get_binding_id(binding))[0]
    obj = unreal.SkeletalMeshActor.cast(obj)

    skm = obj.skeletal_mesh_component.get_skeletal_mesh_asset()
    skeleton = skm.skeleton

    return skm, skeleton



