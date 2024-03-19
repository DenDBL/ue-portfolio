# -*- coding: utf-8 -*-

import unreal

import Source.cfg.config_reader as cfg

ASSET_SUBSYSTEM = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)

DEFAULT_SOURCE_POSE_NAME = cfg.get_default_source_pose_name()


def build_global_settings(rtg_controller):
    global_settings = rtg_controller.get_global_settings()
    global_settings.set_editor_property("enable_ik", True)

    return global_settings


def make_rtg_controller(retargeter):
    rtg_controller = unreal.IKRetargeterController.get_controller(retargeter)

    return rtg_controller


def set_up_rtg_controller(rtg_controller: unreal.IKRetargeterController,
                          source_ik_rig: unreal.IKRigDefinition,
                          target_ik_rig: unreal.IKRigDefinition,
                          target_pose_name="A-Pose"):
    rtg_controller.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source_ik_rig)
    rtg_controller.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, target_ik_rig)

    rtg_controller.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)

    rtg_controller.set_current_retarget_pose(target_pose_name, unreal.RetargetSourceOrTarget.TARGET)
    rtg_controller.set_current_retarget_pose(DEFAULT_SOURCE_POSE_NAME, unreal.RetargetSourceOrTarget.SOURCE)

    global_settings = build_global_settings(rtg_controller)

    rtg_controller.set_global_settings(global_settings)


def retarget_animations(animations: list,
                        rtg_asset_path,
                        source_ik_rig_path,
                        target_ik_rig_path,
                        target_pose_name="A-Pose"):
    rtg = unreal.load_asset(name=rtg_asset_path)

    rtg_controller = make_rtg_controller(rtg)

    source_ik_rig = unreal.load_asset(name=source_ik_rig_path)
    target_ik_rig = unreal.load_asset(name=target_ik_rig_path)

    set_up_rtg_controller(rtg_controller, source_ik_rig, target_ik_rig, target_pose_name)

    assets_to_retarget = []
    for anim_asset in animations:
        assets_to_retarget.append(ASSET_SUBSYSTEM.find_asset_data(anim_asset))

    batch_op = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
        assets_to_retarget,
        None,
        None,
        rtg,
        search="",
        replace="",
        prefix="",
        suffix="",
        remap_referenced_assets=True)

    return batch_op
