# -*- coding: utf-8 -*-
"""Библиотека для работы с ассетами(SkM, текстуры, материалы) Unreal-проекта. Методы взаимодействующие с Cerebro помечены
префиксом ``cf`` """
import os
import sys
from pathlib import Path
import unreal

scriptDir = os.path.dirname(__file__)
sys.path.append(scriptDir)

# import settings
import Source.hash.hash_test as hash

import ue_path_mngr as ue_path

try:
    import Programs.Cerebro.c_functions as cerebro
except:
    unreal.log_warning("Не удалось подключить функции cerebro. Некоторый функционал может быть недоступен")

# CHARACTER_TA = settings.get_activity_name_by_id(144487276)  # Character TA ID
# PROPS_TA = settings.get_activity_name_by_id(144487277)  # Props TA ID
# LOCATION_TA = settings.get_activity_name_by_id(145266902)  # Location TA ID
# CLEANUP_TA = settings.get_activity_name_by_id(28857527)  # Animation TA ID

ACTOR_SYSTEM = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
EDITOR_ASSET_SYSTEM = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
LS_SYSTEM = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
ASSET_REGISTRY = unreal.AssetRegistryHelpers.get_asset_registry()
SUBOBJECT_SYSTEM = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

ASSET_TOOLS = unreal.AssetToolsHelpers.get_asset_tools()

MATERIAL_EDITING_LIBRARY = unreal.MaterialEditingLibrary

BC_POSTFIX = '_bc'
NORMAL_POSTFIX = '_n'
ORM_POSTFIX = '_orm'


def _build_abc_import_options():
    """
    Создаёт настройки импорта алембика

    Parameters
    -----------

    Returns
    -------
    unreal.FbxImportUI
        Настройки импорта
        """
    options = unreal.AbcImportSettings()

    return options


def _build_animation_import_options(skeleton_path):
    """
    Создаёт настройки импорта анимации

    Parameters
    -----------
    skeleton_path: str
        Путь до Skeleton-ассета для которого импортируется анимация



    Returns
    -------
    unreal.FbxImportUI
        Настройки импорта
    """
    options = _build_import_options(False, False, True)

    options.skeleton = unreal.load_asset(skeleton_path)
    # unreal.FbxMeshImportData
    options.anim_sequence_import_data.set_editor_property('import_translation', unreal.Vector(0.0, 0.0, 0.0))
    options.anim_sequence_import_data.set_editor_property('import_rotation', unreal.Rotator(0.0, 0.0, 0.0))
    options.anim_sequence_import_data.set_editor_property('import_uniform_scale', 1.0)
    # unreal.FbxAnimSequenceImportData
    # options.anim_sequence_import_data.set_editor_property('animation_length',
    #                                                       unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    options.anim_sequence_import_data.set_editor_property('remove_redundant_keys', False)
    options.anim_sequence_import_data.set_editor_property('import_bone_tracks', True)
    options.anim_sequence_import_data.set_editor_property('snap_to_closest_frame_boundary', True)
    options.anim_sequence_import_data.set_editor_property('animation_length', unreal.FBXAnimationLengthImportType.FBXALIT_ANIMATED_KEY)
    options.anim_sequence_import_data.set_editor_property('delete_existing_morph_target_curves',
                                                          False)
    options.anim_sequence_import_data.set_editor_property('delete_existing_non_curve_custom_attributes',
                                                          False)
    options.anim_sequence_import_data.set_editor_property('delete_existing_custom_attribute_curves',
                                                          False)
    options.anim_sequence_import_data.set_editor_property('do_not_import_curve_with_zero',
                                                          False)
    return options


def _build_export_options():
    override_options = unreal.FbxExportOption()
    override_options.ascii = False
    override_options.map_skeletal_motion_to_root = False
    override_options.force_front_x_axis = False
    override_options.vertex_color = False
    override_options.level_of_detail = False
    override_options.export_morph_targets = False
    override_options.export_preview_mesh = False
    override_options.export_local_time = True
    override_options.fbx_export_compatibility = unreal.FbxExportCompatibility.FBX_2013

    return override_options


def _build_import_options(mesh=False, skeletal=False, animation=False, materials=False, textures=False):
    """
    Создаёт настройки импорта

    Parameters
    -----------
    mesh : bool
        Использовать mesh объекта
    skeletal:   bool
        Загрузить объект как SkM
    animation: bool
        Загрузить анимации объекта
    materials: bool
        Загрузить материалы объекта
    textures: bool
        Загрузить текстуры объекта

    Returns
    -------
    unreal.FbxImportUI
        Настройки импорта
    """
    options = unreal.FbxImportUI()
    # unreal.FbxImportUI
    if skeletal and not animation:
        options.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    elif animation:
        options.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_ANIMATION)
    else:
        options.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_STATIC_MESH)

    options.set_editor_property('import_as_skeletal', skeletal)
    options.set_editor_property('import_mesh', mesh)
    options.set_editor_property('import_animations', animation)
    options.set_editor_property('import_textures', textures)
    options.set_editor_property('import_materials', materials)
    options.set_editor_property('create_physics_asset', False)
    options.set_editor_property('import_rigid_mesh', False)
    options.set_editor_property('automated_import_should_detect_type', False)

    options.static_mesh_import_data.set_editor_property("build_nanite", False)
    options.static_mesh_import_data.set_editor_property("auto_generate_collision", False)
    options.static_mesh_import_data.set_editor_property('combine_meshes', True)
    options.static_mesh_import_data.set_editor_property('import_translation', unreal.Vector(0.0, 0.0, 0.0))
    options.static_mesh_import_data.set_editor_property('import_rotation', unreal.Rotator(0.0, 0.0, 0.0))
    options.static_mesh_import_data.set_editor_property('import_uniform_scale', 1.0)

    options.skeletal_mesh_import_data.set_editor_property('import_translation', unreal.Vector(0.0, 0.0, 0.0))
    options.skeletal_mesh_import_data.set_editor_property('import_rotation', unreal.Rotator(0.0, 0.0, 0.0))
    options.skeletal_mesh_import_data.set_editor_property('import_uniform_scale', 1.0)
    options.skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)
    options.skeletal_mesh_import_data.set_editor_property('update_skeleton_reference_pose', True)
    options.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose', True)
    options.skeletal_mesh_import_data.set_editor_property('import_vertex_attributes', True)
    options.skeletal_mesh_import_data.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)

    return options


def _build_import_task(filename='', destination_path='', destination_name='', options=None):
    """
    Создаёт задачу импорта

    Parameters
    -----------
    filename: str
        Путь до файла вне проекта
    destination_path:
        Директория файла внутри проекта
    destination_name:
        Имя файла внутри проекта
    options: unreal.FbxImportUI

    Returns
    -------
    unreal.AssetImportTask
        Задача импорта
    """
    task = unreal.AssetImportTask()
    task.set_editor_property('automated', True)
    task.set_editor_property('destination_name', destination_name)
    task.set_editor_property('destination_path', destination_path)
    task.set_editor_property('filename', filename)
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('save', True)
    task.set_editor_property('options', options)

    return task


def _execute_import_tasks(tasks=[]):
    """
        Создаёт задачу импорта

        Parameters
        -----------
        tasks: list[unreal.AssetImportTask]
            Список задач импорта

        Returns
        -------
        list[str]
            Список путей до импортированных файлов
    """

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

    imported_asset_paths = []

    for task in tasks:
        for path in task.get_editor_property('imported_object_paths'):
            imported_asset_paths.append(path)

    return imported_asset_paths


def _get_texture_sets_from_project_dir(dirpath):
    """
         Возвращает сеты текстур. Пытается найти BC, NORMAL, ORM

         Parameters
         -----------
         dirpath: str
            Путь до директории с текстурами внутри UE-проекта


         Returns
         -------
         list[list[str]]
             Список сетов путей до текстур
    """
    textures_paths = EDITOR_ASSET_SYSTEM.list_assets(dirpath, recursive=False)

    bc_textures = []
    for texture_path in textures_paths:
        try:
            unreal.Texture.cast(unreal.load_asset(texture_path))
        except:
            continue

        texture_name = os.path.basename(texture_path).split('.')[0]
        if BC_POSTFIX in texture_name:
            bc_textures.append(texture_name)

    sets = []
    for bc_texture in bc_textures:
        n_texture = bc_texture.replace(BC_POSTFIX, NORMAL_POSTFIX)
        orm_texture = bc_texture.replace(BC_POSTFIX, ORM_POSTFIX)

        bc_texture_path = os.path.join(dirpath, bc_texture).replace('\\', '/')
        n_texture_path = os.path.join(dirpath, n_texture).replace('\\', '/')
        orm_texture_path = os.path.join(dirpath, orm_texture).replace('\\', '/')

        sets.append([bc_texture_path,
                     n_texture_path,
                     orm_texture_path])

    return sets


def _import_abc(filepath, destination_path, destination_name=''):
    """
    Импортирует алембик

    Parameters
    -----------
    filepath:str
        Путь до алембика
    destination_path: str
        Директория внутри unreal-проекта
    destination_name: str
        имя внутри unreal-проекта

    Returns
    -------
    list[str]
        Список путей до импортированных файлов
    """
    ue_path.create_dir(destination_path)

    options = _build_abc_import_options()
    task = _build_import_task(filepath, destination_path, destination_name, options)

    asset_paths = _execute_import_tasks([task])

    md5 = hash.md5(filepath)

    for asset_path in asset_paths:
        set_asset_metadata(asset_path, MFA_hash=md5)

    return asset_paths


def _import_animation(filepath, skeleton_path, destination_path, destination_name=''):
    """
    Импортирует анимайию

    Parameters
    -----------
    filepath:str
        Путь до анимации
    skeleton_path: str
        Путь до Skeleton-ассета объект, для которого загружается анимация
    destination_path: str
        Директория внутри unreal-проекта
    destination_name: str
        имя внутри unreal-проекта

    Returns
    -------
    list[str]
        Список путей до импортированных файлов
    """
    ue_path.create_dir(destination_path)

    options = _build_animation_import_options(skeleton_path)
    task = _build_import_task(filepath, destination_path, destination_name, options)

    asset_paths = _execute_import_tasks([task])

    md5 = hash.md5(filepath)

    for asset_path in asset_paths:
        set_asset_metadata(asset_path, MFA_hash=md5)

    return asset_paths


def _import_asset(filepath, destination_path, destination_name='', mesh=True, skeletal=False, animation=False):
    """
    Импортирует ассет. Используется в основном для импорта ``static mesh``

    Parameters
    -----------
    filepath:str
        Путь до файла

    destination_path: str
        Директория внутри unreal-проекта
    destination_name: str
        имя внутри unreal-проекта
     mesh : bool
        Использовать mesh объекта
    skeletal:   bool
        Загрузить объект как SkM
    animation: bool
        Загрузить анимации объекта

    Returns
    -------
    list[str]
        Список путей до импортированных файлов
    """
    ue_path.create_dir(destination_path)

    options = _build_import_options(mesh=mesh, skeletal=skeletal, animation=animation)
    task = _build_import_task(filepath, destination_path, destination_name, options)

    asset_paths = _execute_import_tasks([task])

    md5 = hash.md5(filepath)

    for asset_path in asset_paths:
        set_asset_metadata(asset_path, MFA_hash=md5)

    return asset_paths


def _import_st9(filepath, destination_path, destination_name=''):
    ue_path.create_dir(destination_path)

    task = _build_import_task(filepath, destination_path, destination_name)

    asset_paths = _execute_import_tasks([task])

    md5 = hash.md5(filepath)

    for asset_path in asset_paths:
        set_asset_metadata(asset_path, MFA_hash=md5)

    return asset_paths


def _import_texture(filepath, destination_path, destination_name=''):
    """
    Импортирует ассет. Используется в основном для импорта ``static mesh``

    Parameters
    -----------
    filepath:str
        Путь до файла

    destination_path: str
        Директория внутри unreal-проекта
    destination_name: str
        имя внутри unreal-проекта


    Returns
    -------
    list[str]
        Список путей до импортированных файлов
    """
    ue_path.create_dir(destination_path)

    task = _build_import_task(filepath, destination_path, destination_name)

    asset_paths = _execute_import_tasks([task])

    md5 = hash.md5(filepath)

    for asset_path in asset_paths:
        set_asset_metadata(asset_path, MFA_hash=md5)
        unreal.Texture.cast(unreal.load_asset(asset_path)).set_editor_property('virtual_texture_streaming', True)

    return asset_paths


def _load_animation(filepath, skeleton_path, destination_path, destination_name=''):
    """
        Умная загрузка анимации в unreal-проект. Загружает файл только в случае отсутствия файла в проекте или несовпадения хешей

        Parameters
        -----------
        filepath:str
            Путь до файла
        skeleton_path: str
            Путь до Skeleton-ассета объект, для которого загружается анимация
        destination_path: str
            Директория внутри unreal-проекта
        destination_name: str
            имя внутри unreal-проекта


        Returns
        -------
        list[str]
            Список путей до импортированных файлов
    """
    if not destination_name:
        destination_name = os.path.basename(filepath).split('.')[0]

    path = os.path.join(destination_path, destination_name).replace("\\", "/")

    if not is_asset_exists(path):
        asset_paths = _import_animation(filepath, skeleton_path, destination_path, destination_name)
    elif hash.md5(filepath) != get_asset_metadata(path, "MFA_hash"):
        asset_paths = _import_animation(filepath, skeleton_path, destination_path, destination_name)
    else:
        asset_paths = [path]

    return asset_paths


def _load_simulation(filepath, destination_path, destination_name=''):
    """
     Умная загрузка алембиков в unreal-проект. Загружает файл только в случае отсутствия файла в проекте или несовпадения хешей

     Parameters
     -----------
     filepath:str
         Путь до файла
     destination_path: str
         Директория внутри unreal-проекта
     destination_name: str
         имя внутри unreal-проекта


     Returns
     -------
     list[str]
         Список путей до импортированных файлов
     """
    path = os.path.join(destination_path, destination_name).replace("\\", "/")

    if not is_asset_exists(path):
        asset_paths = _import_abc(filepath, destination_path, destination_name)
    elif hash.md5(filepath) != get_asset_metadata(path, "MFA_hash"):
        asset_paths = _import_abc(filepath, destination_path, destination_name)
    else:
        asset_paths = [path]

    return asset_paths


def _load_skm(filepath, destination_path, destination_name=''):
    """
     Умная загрузка SkM в unreal-проект. Загружает файл только в случае отсутствия файла в проекте или несовпадения хешей

     Parameters
     -----------
     filepath:str
         Путь до файла

     destination_path: str
         Директория внутри unreal-проекта
     destination_name: str
         имя внутри unreal-проекта


     Returns
     -------
     list[str]
         Список путей до импортированных файлов
     """
    path = os.path.join(destination_path, destination_name).replace("\\", "/")

    if not is_asset_exists(path):
        asset_paths = _import_asset(filepath, destination_path, destination_name, True, True)
    elif hash.md5(filepath) != get_asset_metadata(path, "MFA_hash"):
        asset_paths = _import_asset(filepath, destination_path, destination_name, True, True)
    else:
        asset_paths = [path]

    return asset_paths


def _load_sm(filepath, destination_path, destination_name=''):
    """
         Умная загрузка Static Mesh в unreal-проект. Загружает файл только в случае отсутствия файла в проекте или несовпадения хешей

         Parameters
         -----------
         filepath:str
             Путь до файла

         destination_path: str
             Директория внутри unreal-проекта
         destination_name: str
             имя внутри unreal-проекта


         Returns
         -------
         list[str]
             Список путей до импортированных файлов
    """
    path = os.path.join(destination_path, destination_name).replace("\\", "/")

    if not is_asset_exists(path):
        asset_paths = _import_asset(filepath, destination_path, destination_name, True)
    elif hash.md5(filepath) != get_asset_metadata(path, "MFA_hash"):
        asset_paths = _import_asset(filepath, destination_path, destination_name, True)
    else:
        asset_paths = [path]

    return asset_paths


def _load_st9(filepath, destination_path, destination_name=''):
    path = os.path.join(destination_path, destination_name).replace("\\", "/")

    if not is_asset_exists(path):
        asset_paths = _import_st9(filepath, destination_path, destination_name)
    elif hash.md5(filepath) != get_asset_metadata(path, "MFA_hash"):
        asset_paths = _import_st9(filepath, destination_path, destination_name)
    else:
        asset_paths = [path]

    return asset_paths


def _load_texture(filepath, destination_path, destination_name=''):
    path = os.path.join(destination_path, destination_name).replace("\\", "/")

    if not is_asset_exists(path):
        asset_paths = _import_texture(filepath, destination_path, destination_name)
    elif hash.md5(filepath) != get_asset_metadata(path, "MFA_hash"):
        asset_paths = _import_texture(filepath, destination_path, destination_name)
    else:
        asset_paths = [path]

    return asset_paths


def _load_textures_from_dir(dirpath, destination_path):
    for file in os.listdir(dirpath):

        filename = os.path.basename(file)
        filepath = os.path.join(dirpath, file)

        if os.path.isdir(filepath):
            continue

        sep_name = filename.split('.')
        if sep_name[1].isdigit():
            if sep_name[1] == '1001':
                _load_texture(filepath, destination_path, sep_name[0])

        else:
            _load_texture(filepath, destination_path, sep_name[0])


def add_subobject(subsystem,
                  blueprint,
                  new_class,
                  name) -> (unreal.SubobjectDataHandle, unreal.Object):
    root_data_handle = subsystem.k2_gather_subobject_data_for_blueprint(context=blueprint)[1]

    sub_handle, fail_reason = subsystem.add_new_subobject(
        params=unreal.AddNewSubobjectParams(
            parent_handle=root_data_handle,
            new_class=new_class,
            blueprint_context=blueprint))

    if not fail_reason.is_empty():
        raise Exception("ERROR from sub_object_subsystem.add_new_subobject: {fail_reason}")

    subsystem.rename_subobject(handle=sub_handle, new_name=unreal.Text(name))
    subsystem.attach_subobject(owner_handle=root_data_handle, child_to_add_handle=sub_handle)

    BFL = unreal.SubobjectDataBlueprintFunctionLibrary
    obj = BFL.get_object(BFL.get_data(sub_handle))

    return sub_handle, obj


def apply_list_of_materials(materials, asset):
    """Пытается применить список материалов к объекту

    Parameters
    -----------
    materials: list[unreal.MaterialInterafce]
        Список материалов
    asset: unreal.StaticMesh unreal.SkeletonMesh
        Объект
    """
    for mat in materials:
        apply_material(mat, asset)


def apply_material(material, asset):
    """Пытается применить материал на объект в нужный слот по имени материала.

    Parameters
    -----------
    material: unreal.MaterialInterface
        Материал
    asset: unreal.StaticMesh unreal.SkeletonMesh
        Объект
    """
    material_name = material.get_name().replace('mi_t_', '')

    if isinstance(asset, unreal.SkeletalMesh):
        for mat in asset.materials:
            if material_name == mat.material_slot_name:
                mat.material_interface = material

    else:
        mat_index = asset.get_material_index(material_name)
        if mat_index is not None:
            asset.set_material(mat_index, material)


def cf_load_asset_by_task_info(task_info):
    """
     Загрузка ассета по его task_info

     Parameters
     -----------
     task_info: dict
        Task info ассета


     Returns
     -------
     list[str]
         Список путей до импортированных файлов
     """

    if task_info['task_activity_name'] == 'Foliage':
        path = ue_path.cf_get_foliage_st9_path(task_info)
        if path:
            return load_foliage_to_project(path, task_info['task_activity_name'], task_info['task_name'])

    path = ue_path.cf_get_asset_fbx_path(task_info)
    if not path:
        return None

    assets = load_asset_to_project(path, task_info['task_activity_name'], task_info['task_name'])

    # textures_dir = ue_path.cf_get_textures_dir(task_info)
    # if textures_dir:
    #     materials = load_textures_and_create_materials(textures_dir, task_info['task_activity_name'],
    #                                                    task_info['task_name'])
    #     for asset in assets:
    #         apply_list_of_materials(materials, unreal.load_asset(asset))

    return assets


def create_bp_for_skm(skeletal_mesh_path):
    print(skeletal_mesh_path)
    skeletal_mesh_name = os.path.basename(skeletal_mesh_path).rsplit('.')[-1]
    package_path = os.path.dirname(skeletal_mesh_path)
    blueprint_name = 'BP_' + skeletal_mesh_name.split('_', 1)[1].rsplit('_', 1)[0]

    print(package_path, blueprint_name)
    if ue_path.is_asset_exists(os.path.join(package_path, blueprint_name)):
        return

    bp = make_blueprint(package_path, blueprint_name)
    sub_handle, component = add_subobject(SUBOBJECT_SYSTEM, bp, unreal.SkeletalMeshComponent, skeletal_mesh_name)
    setup_skeletal_mesh_component(component, skeletal_mesh_path)


def create_material_for_texture_set(texture_list, destination_path, destination_name, body=True):
    """
    Создаёт материал для переданного сета. Если материал существует - задаёт ему новые параметры. Создаёт
    MaterialInstance на основе мастер-материала

    Parameters
    -----------
    texture_list: list
        Сет текстур в проекте
    destination_path: str
        Директория материала
    destination_name: str
        Имя материала
    body: bool
        Тип материала. Если true - тип = тело, иначе пропс/ткань. По умолчанию true



    Returns
    -------
    unreal.MaterialInterface
        Материал
    """
    mi_full_path = os.path.join(destination_path, destination_name)

    def set_mi_texture(mi_asset, param_name, tex_path):
        if not unreal.EditorAssetLibrary.does_asset_exist(tex_path):
            unreal.log_warning("Can't find texture: " + tex_path)
            return False

        tex_asset = unreal.Texture.cast(unreal.EditorAssetLibrary.find_asset_data(tex_path).get_asset())
        return unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(mi_asset, param_name,
                                                                                           tex_asset)

    if is_asset_exists(mi_full_path):
        mi_asset = EDITOR_ASSET_SYSTEM.find_asset_data(mi_full_path).get_asset()
        unreal.log("Asset already exists")
    else:
        mi_asset = ASSET_TOOLS.create_asset(destination_name, destination_path, unreal.MaterialInstanceConstant,
                                            unreal.MaterialInstanceConstantFactoryNew())

    if body:
        if not is_asset_exists(ue_path.get_chars_master_material_path()):
            unreal.log_warning('Unable to find master material for character')
            return

        MATERIAL_EDITING_LIBRARY.set_material_instance_parent(mi_asset,
                                                              unreal.load_asset(
                                                                  ue_path.get_chars_master_material_path()))

        for texture_path in texture_list:

            texture = unreal.load_asset(texture_path)

            if BC_POSTFIX in texture.get_name():
                set_mi_texture(mi_asset, "Tex_BaseColor", texture.get_path_name())

            elif NORMAL_POSTFIX in texture.get_name():
                set_mi_texture(mi_asset, "Tex_Normal", texture.get_path_name())

            elif ORM_POSTFIX in texture.get_name():
                set_mi_texture(mi_asset, "Tex_ORM", texture.get_path_name())

    else:
        if not is_asset_exists(ue_path.get_props_master_material_path()):
            unreal.log_warning('Unable to find master material for props')
            return

        MATERIAL_EDITING_LIBRARY.set_material_instance_parent(mi_asset,
                                                              unreal.load_asset(
                                                                  ue_path.get_props_master_material_path()))

        for texture_path in texture_list:

            texture = unreal.load_asset(texture_path)

            if BC_POSTFIX in texture.get_name():
                set_mi_texture(mi_asset, "Tex_BaseColor_VT", texture.get_path_name())

            elif NORMAL_POSTFIX in texture.get_name():
                set_mi_texture(mi_asset, "Tex_Normal_VT", texture.get_path_name())

            elif ORM_POSTFIX in texture.get_name():
                set_mi_texture(mi_asset, "Tex_ORM_VT", texture.get_path_name())

    return mi_asset


def find_bp_asset_by_name(name, activity):
    assets_dir = ue_path.get_activity_asset_dir(activity)
    asset_path = os.path.join(assets_dir, name).replace('\\', '/')
    if ue_path.is_dir_exists(asset_path):
        skeletal = find_skeletal_mesh(asset_path)

        return skeletal


def find_skeletal_asset_by_name(name, activity):
    assets_dir = ue_path.get_activity_asset_dir(activity)
    asset_path = os.path.join(assets_dir, name).replace('\\', '/')
    if ue_path.is_dir_exists(asset_path):
        skeletal = find_skeletal_mesh(asset_path)

        return skeletal


def find_skeletal_mesh(directory_path):
    """
     Поиск SkeletonMesh-ассета в директории. В случае отсутствия - вывод предупреждения и вывод ``None``

     Parameters
     -----------
     directory_path: str
        Директория поиска

     Returns
     -------
     str
        Путь до skeleton-ассета
     """
    assets = EDITOR_ASSET_SYSTEM.list_assets(directory_path)

    for asset in assets:
        if unreal.load_asset(asset).get_class() == unreal.SkeletalMesh.static_class():
            return asset

    unreal.log_warning(f'Unable to find any Skeleton in directory: {directory_path}')
    return


def find_skeleton(directory_path):
    """
     Поиск skeleton-ассета в директории. В случае отсутствия - вывод предупреждения и вывод ``None``

     Parameters
     -----------
     directory_path: str
        Директория поиска

     Returns
     -------
     str
        Путь до skeleton-ассета
     """
    assets = EDITOR_ASSET_SYSTEM.list_assets(directory_path)

    for asset in assets:
        if unreal.load_asset(asset).get_class() == unreal.Skeleton.static_class():
            return asset

    unreal.log_warning(f'Unable to find any Skeleton in directory: {directory_path}')
    return


def find_static_asset_by_name(name, activity):
    assets_dir = ue_path.get_activity_asset_dir(activity)
    asset_path = os.path.join(assets_dir, name).replace('\\', '/')
    if ue_path.is_dir_exists(asset_path):
        skeletal = find_static_mesh(asset_path)

        return skeletal


def find_static_mesh(directory_path):
    """
     Поиск StaticnMesh-ассета в директории. В случае отсутствия - вывод предупреждения и вывод ``None``

     Parameters
     -----------
     directory_path: str
        Директория поиска

     Returns
     -------
     str
        Путь до static-ассета
     """
    assets = EDITOR_ASSET_SYSTEM.list_assets(directory_path)

    for asset in assets:
        if isinstance(unreal.load_asset(asset), unreal.StaticMesh):
            return asset

    unreal.log_warning(f'Unable to find any Skeleton in directory: {directory_path}')
    return


def get_all_assets_of_python_class(python_class):
    """Возвращает все ассеты проекта, принадлежащие Python-классу

           Parameters
           -----------
            python_class: Class
                Python-класс ассета
           Returns
           ---------
           list[unreal.AssetData]
                Список ассетов проекта
    """
    static_class = python_class.static_class()

    package_path = static_class.get_path_name().split('.')[0]
    asset_name = static_class.get_path_name().split('.')[1]

    assets = ASSET_REGISTRY.get_assets_by_class(unreal.TopLevelAssetPath(package_path, asset_name), True)

    return assets


def get_all_object_metadata(obj):
    asset = {
        'id': get_object_metadata(obj, 'MFA_ID'),
        'file': get_object_metadata(obj, 'MFA_FILE'),
        'task_name': get_object_metadata(obj, 'MFA_TASK_NAME'),
        'task_id': get_object_metadata(obj, 'MFA_TASK_ID'),
        'task_activity_id': get_object_metadata(obj, 'MFA_TASK_ACTIVITY_ID'),
        'publish_path': get_object_metadata(obj, 'MFA_PUBLISH_PATH')
    }

    return asset


def get_asset_metadata(asset_path, key):
    """Возвращает метадату ассета в проекта

    Parameters
    -----------
    asset_path: str
        Путь до ассета в проекте
    key:str
        Ключ значения
    Returns
    ---------
    str
        Значение
    """
    loaded_asset = unreal.EditorAssetLibrary.load_asset(asset_path)

    value = unreal.EditorAssetLibrary.get_metadata_tag(loaded_asset, key)

    unreal.SystemLibrary.collect_garbage()
    return value


def get_object_metadata(object, key):
    """Возвращает метадату подгруженного объекта в проекте

        Parameters
        -----------
        object: unreal.Object
            Объект
        key: str
            Ключ значения

        Returns
        ---------
        str
            Значение
    """
    value = unreal.EditorAssetLibrary.get_metadata_tag(object, key)

    return value


def is_asset_exists(name):
    """
    Проверят, существует ли ассет в проекте

    Parameters
    -----------
    name: Полный путь до ассета в ```Content browser```

    Returns
    -------
    bool
    """
    return unreal.EditorAssetLibrary.does_asset_exist(name.replace("\\", "/"))


def load_animation_to_project(path, sequence, skeleton_path, activity=None):
    """
    Загружает анимацию в нужную директорию внутри проекта на основании секвенции и вида деятельности


    Parameters
    -----------
    path: str
        Путь до файла анимации
    sequence: unreal.MovieSceneSequence
        Секвенция, рядом с котрой будет загружен файл анимации
    skeleton_path: str
        Путь до Skeleton-ассета объекта, для которого подгружается эта анимация
    activity: str
        Вид деятельности задачи этой анимации

    Returns
    -------
    str
        Путь до загруженной анимации
    """
    # if get_object_metadata(sequence, 'MFA_TYPE') != 'CUT':
    #     return

    subdir = activity if activity else ''

    sequence_dir = os.path.dirname(sequence.get_path_name())
    destination_path = os.path.join(sequence_dir, 'Animation', subdir).replace('\\', '/')

    asset_paths = _load_animation(path, skeleton_path, destination_path)
    if not asset_paths:
        return

    return asset_paths[0]


def load_asset_to_project(path, activity=None, name=None):
    """
    Загружает объект в нужную директорию внутри проекта на основании секвенции и вида деятельности


    Parameters
    -----------
    path: str
        Путь до файла
    activity: str
        Вид деятельности задачи этой анимации
    name: str
        Имя объекта внутри unreal-проекта

    Returns
    -------
    list[str]
        Пути до загруженных объектов
    """
    if not path or not os.path.exists(path):
        unreal.log_warning(f'Unable load asset from {path}')
        return

    def _load_asset(sm=True, skm=False, animation=False):
        destination_path = ue_path.get_activity_asset_dir(activity)
        if name:
            destination_path = os.path.join(destination_path, name).replace('\\', '/')

        sm_name = ue_path.get_basename_without_ext(path).replace('_skm', '_sm')
        skm_name = ue_path.get_basename_without_ext(path)
        result = []
        if sm:
            sm_paths = _load_sm(path, destination_path, sm_name)
            result.extend(sm_paths)

        if skm:
            skm_paths = _load_skm(path, destination_path, skm_name)
            for skm_path in skm_paths:
                if isinstance(unreal.load_asset(skm_path), unreal.SkeletalMesh):
                    create_bp_for_skm(skm_path)

            result.extend(skm_paths)

        for asset_path in result:
            set_asset_metadata(asset_path, MFA_task_activity_name=activity)

        return result

    if activity == CHARACTER_TA:
        return _load_asset(skm=True)

    if activity == PROPS_TA:
        return _load_asset(skm=True)

    if activity == LOCATION_TA:
        return _load_asset()


def load_foliage_to_project(path, activity=None, name=None):
    if not path or not os.path.exists(path):
        unreal.log_warning(f'Unable load asset from {path}')
        return

    destination_path = ue_path.get_activity_asset_dir(activity)
    if name:
        destination_path = os.path.join(destination_path, name).replace('\\', '/')

    assets = _load_st9(path, destination_path, name)

    for asset in EDITOR_ASSET_SYSTEM.list_assets(destination_path, recursive=False):
        try:
            unreal.Texture.cast(unreal.load_asset(asset))
            texture_dir = os.path.join(destination_path, 'Textures').replace('\\', '/')
            ue_path.create_dir(texture_dir)
            texture_path = os.path.join(texture_dir, os.path.basename(asset)).replace('\\', '/')

            if EDITOR_ASSET_SYSTEM.does_asset_exist(texture_path):
                EDITOR_ASSET_SYSTEM.delete_asset(texture_path)

            EDITOR_ASSET_SYSTEM.rename_asset(asset, texture_path)
        except:
            pass

        try:
            unreal.MaterialInterface.cast(unreal.load_asset(asset))
            mats_dir = os.path.join(destination_path, 'Materials').replace('\\', '/')
            ue_path.create_dir(mats_dir)
            mat_path = os.path.join(mats_dir, os.path.basename(asset)).replace('\\', '/')

            if EDITOR_ASSET_SYSTEM.does_asset_exist(mat_path):
                EDITOR_ASSET_SYSTEM.delete_asset(mat_path)

            EDITOR_ASSET_SYSTEM.rename_asset(asset, mat_path)
        except:
            pass

    return assets


def load_textures_and_create_materials(texturesdir, activity=None, name=None):
    """Загружает текстуры в проект и создаёт под ни материалы

    Parameters
    -----------
    texturesdir: str
        Директория с текстурами
    activity: str
        Вид деятельности
    name:
        Имя объекта


    Returns
    -----------

    list[unreal.MaterialInterface]
        Список материалов
    """
    destination_path = ue_path.get_activity_asset_dir(activity)
    if name:
        destination_path = os.path.join(destination_path, name).replace('\\', '/')

    texture_destination_path = os.path.join(destination_path, "Textures").replace('\\', '/')

    _load_textures_from_dir(texturesdir, texture_destination_path)
    sets = _get_texture_sets_from_project_dir(texture_destination_path)

    material_destination_path = os.path.join(destination_path, "Materials").replace('\\', '/')

    materials = []
    for t_set in sets:
        body = True if 'body' in t_set[0].lower() else False
        material_name = 'mi_' + os.path.basename(t_set[0]).replace(BC_POSTFIX, '')
        mat = create_material_for_texture_set(t_set, material_destination_path, material_name, body)
        materials.append(mat)

    return materials


def make_blueprint(package_path: str, asset_name: str):
    factory = unreal.BlueprintFactory()
    factory.set_editor_property(name="parent_class", value=unreal.Pawn)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    asset = asset_tools.create_asset(asset_name=asset_name,
                                     package_path=package_path,
                                     asset_class=None,
                                     factory=factory)
    if not isinstance(asset, unreal.Blueprint):
        raise Exception("Failed to create blueprint asset")

    return asset


def set_asset_metadata(asset_path, **kwargs):
    """Устанавливает метадату ассета в проекте

    Parameters
    -----------
    asset_path: str
        Путь до ассета в проекте
    kwargs
        Пара ключ - значение
    """
    loaded_asset = unreal.EditorAssetLibrary.load_asset(asset_path)

    for key, value in kwargs.items():
        unreal.EditorAssetLibrary.set_metadata_tag(loaded_asset, unreal.Name(key), str(value))
        unreal.EditorAssetLibrary.save_asset(asset_path)

    unreal.SystemLibrary.collect_garbage()


def set_object_metadata(object, **kwargs):
    """Устанавливает метадату подгруженного объекта

    Parameters
    -----------
    object: unreal.Object
        Объект
    kwargs
        Пара ключ - значение
    """
    for key, value in kwargs.items():
        unreal.EditorAssetLibrary.set_metadata_tag(unreal.Object.cast(object), unreal.Name(key), str(value))


def set_object_metadata_with_dict(obj, data):
    set_object_metadata(obj, MFA_ID=data.get('id'))
    set_object_metadata(obj, MFA_FILE=data.get('file'))
    set_object_metadata(obj, MFA_TASK_NAME=data.get('task_name'))
    set_object_metadata(obj, MFA_TASK_ID=data.get('task_id'))
    set_object_metadata(obj, MFA_TASK_ACTIVITY_ID=data.get('task_activity_id'))
    set_object_metadata(obj, MFA_PUBLISH_PATH=data.get('publish_path'))


def setup_skeletal_mesh_component(component, skeletal_mesh_path):
    component.set_skeletal_mesh_asset(unreal.load_asset(skeletal_mesh_path))


if __name__ == '__main__':
    create_bp_for_skm(r'/Game/Frog/Assets/Character/Mago/chr_Mago_skm.chr_Mago_skm')
