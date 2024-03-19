# -*- coding: utf-8 -*-

import traceback
import os
import unreal

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import Source.conn.ai_requests as ai_requests
import Source.utils as utils
import Source.ui.qt_window_spawn_ue as window_spawner

import Source.mfa_unreal_core.ue_sequence_mngr as ue_sequence
import Source.mfa_unreal_core.ue_content_mngr as ue_content
import Source.retarget.ue_retarget_mngr as ue_retarget

import Source.cfg.config_reader as cfg

EDITOR_ASSET_SYSTEM = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)


def get_models():
    model_dicts = utils.get_models_from_response(ai_requests.get_models())

    models = []
    for m in model_dicts:
        models.append({
            'id': utils.get_model_id(m),
            'name': utils.get_model_name(m)
        })

    return models


def get_model_id_by_name(name, models):
    for model in models:
        if model.get('name') == name:
            return model.get('id')


class ActionItem(QWidget):
    def __init__(self, index, root):
        super(ActionItem, self).__init__()

        self.setObjectName(u"action_item")
        self.horizontalLayout_2 = QHBoxLayout(self)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.number = QLabel(self)
        self.number.setObjectName(u"number")

        self.set_number(index)

        self.horizontalLayout_2.addWidget(self.number)

        self.action_le = QLineEdit(self)
        self.action_le.setObjectName(u"action_le")
        self.action_le.textEdited.connect(root.ui.update_action_items)

        self.horizontalLayout_2.addWidget(self.action_le)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

    def is_empty(self):
        return len(self.action_le.text().strip()) == 0

    def get_action_string(self):
        return self.action_le.text().strip()

    def set_number(self, number):
        self.number.setText(QCoreApplication.translate("Dialog", f"{number}.", None))


class Ui_Dialog(object):
    def __init__(self):
        self.Dialog = None

        self.models = []
        self.actions_items = []

    def setupUi(self, Dialog):

        self.Dialog = Dialog

        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(516, 380)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tab_widget = QTabWidget(Dialog)
        self.tab_widget.setObjectName(u"tab_widget")
        self.Home = QWidget()
        self.Home.setObjectName(u"Home")
        self.verticalLayout_2 = QVBoxLayout(self.Home)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.model_setup = QWidget(self.Home)
        self.model_setup.setObjectName(u"model_setup")
        self.horizontalLayout = QHBoxLayout(self.model_setup)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.model_label = QLabel(self.model_setup)
        self.model_label.setObjectName(u"model_label")
        font = QFont()
        font.setFamily(u"Arial")
        font.setPointSize(14)
        self.model_label.setFont(font)

        self.horizontalLayout.addWidget(self.model_label)

        self.comboBox = QComboBox(self.model_setup)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMinimumSize(QSize(200, 0))

        self.update_models_combo_box()

        self.horizontalLayout.addWidget(self.comboBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout_2.addWidget(self.model_setup)

        self.actions = QWidget(self.Home)
        self.actions.setObjectName(u"actions")
        self.verticalLayout_3 = QVBoxLayout(self.actions)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.actions_label = QLabel(self.actions)
        self.actions_label.setObjectName(u"actions_label")
        self.actions_label.setFont(font)

        self.verticalLayout_3.addWidget(self.actions_label)

        self.actions_widget = QFrame(self.actions)
        self.actions_widget.setObjectName(u"actions_widget")
        self.verticalLayout_4 = QVBoxLayout(self.actions_widget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")

        self.scrollArea = QScrollArea(self.actions_widget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.actions_scroll_area = QFrame()
        self.actions_scroll_area.setObjectName(u"actions_scroll_area")

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)

        # self.actions_scroll_area.setGeometry(QRect(0, 0, 436, 340))

        self.verticalLayout_5 = QVBoxLayout(self.actions_scroll_area)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")

        self.add_action_item(1)

        self.scrollArea.setWidget(self.actions_scroll_area)
        self.verticalLayout_4.addWidget(self.scrollArea)

        self.verticalLayout_3.addWidget(self.actions_widget)

        self.verticalLayout_2.addWidget(self.actions)

        # self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        #
        # self.verticalLayout_2.addItem(self.verticalSpacer)

        self.widget = QWidget(self.Home)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_3 = QHBoxLayout(self.widget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.generate_button = QPushButton(self.widget)
        self.generate_button.setObjectName(u"generate_button")
        self.generate_button.setFont(font)

        self.generate_button.clicked.connect(self.on_generate)

        self.horizontalLayout_3.addWidget(self.generate_button)

        self.verticalLayout_2.addWidget(self.widget)

        self.tab_widget.addTab(self.Home, "")
        self.Settings = QWidget()
        self.Settings.setObjectName(u"Settings")
        self.tab_widget.addTab(self.Settings, "")

        self.verticalLayout.addWidget(self.tab_widget)

        self.retranslateUi(Dialog)

        self.tab_widget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi
    def update_models_combo_box(self):
        for i in range(self.comboBox.count()):
            self.comboBox.removeItem(0)

        self.models = get_models()

        for i, model in enumerate(self.models):
            self.comboBox.addItem("")
            self.comboBox.setItemText(i, model.get('name'))

    def add_action_item(self, index):
        print('ADDED_ACTION')
        action_item = ActionItem(index, self.Dialog)

        self.actions_items.append(action_item)
        self.verticalLayout_5.addWidget(action_item)
        # self.validate_action_items()
        self.update_spacer_in_scroll_area()

    def remove_action_item(self, action_item):
        print('REMOVED_ACTION')

        self.verticalLayout_5.removeWidget(action_item)
        # action_item.setParent(None)
        self.actions_items.remove(action_item)
        self.update_numbers()

    def validate_action_items(self):
        for i in reversed(range(self.verticalLayout_5.count())):
            widget = self.verticalLayout_5.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for i, action_item in enumerate(self.actions_items):
            self.verticalLayout_5.addWidget(action_item)
            action_item.set_number(i + 1)
            print(action_item, 'added at', i + 1)

        self.update_spacer_in_scroll_area()

    def update_action_items(self):
        try:
            has_empty = False
            empty_item = None

            for item in self.actions_items:
                if has_empty:
                    if item.is_empty():
                        self.remove_action_item(empty_item)

                if item.is_empty():
                    has_empty = True
                    empty_item = item
                    continue

            if not has_empty:
                self.add_action_item(len(self.actions_items) + 1)
        except:
            print(traceback.format_exc())

    def update_spacer_in_scroll_area(self):
        for i in reversed(range(self.verticalLayout_5.count())):
            item = self.verticalLayout_5.itemAt(i)
            if item.spacerItem():
                self.verticalLayout_5.removeItem(item)

        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(verticalSpacer)

    def update_numbers(self):
        for i, item in enumerate(self.actions_items):
            item.set_number(i + 1)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"AnimAI", None))
        self.model_label.setText(QCoreApplication.translate("Dialog", u"Model", None))
        self.actions_label.setText(QCoreApplication.translate("Dialog", u"Actions", None))

        self.generate_button.setText(QCoreApplication.translate("Dialog", u"GENERATE", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.Home),
                                   QCoreApplication.translate("Dialog", u"Home", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.Settings),
                                   QCoreApplication.translate("Dialog", u"Settings", None))

    # retranslateUi

    def get_actions(self):
        actions = []

        for action_item in self.actions_items:
            if not action_item.is_empty():
                actions.append(action_item.get_action_string())

        return actions

    def on_generate(self):
        try:
            sequence = ue_sequence.get_focused_level_sequence()
            sequence_path = sequence.get_path_name()
            sequence_dir = os.path.dirname(sequence_path)

            bindings: list = ue_sequence.get_skm_bindings(sequence)
            number_of_samples = len(bindings)
            if not number_of_samples:
                return

            actions = self.get_actions()
            model_id = get_model_id_by_name(self.comboBox.currentText(), self.models)

            fbxs = make_batch_request(actions, model_id, number_of_samples)

            anim_dir = os.path.join(sequence_dir, 'Animation', 'Retargeted').replace('\\', '/')

            with unreal.ScopedSlowTask(len(fbxs), 'Applying...') as slow_task:
                slow_task.make_dialog(can_cancel=True, allow_in_pie=True)

                for fbx_path in fbxs:
                    binding = bindings.pop(0)
                    skm, skeleton = ue_sequence.get_skm_and_skeleton_of_binding(binding, sequence)

                    ik_rig = find_ik_rig_in_dir(os.path.dirname(skeleton.get_path_name()))

                    source_skeleton_path = cfg.get_source_skeleton_path()
                    source_anim_path = ue_content._import_animation(fbx_path,
                                                                    source_skeleton_path,
                                                                    os.path.join(sequence_dir, 'Animation',
                                                                                 'Generated').replace('\\', '/'))[0]

                    slow_task.enter_progress_frame(0.5)

                    rtg_asset_path = cfg.get_rtg_path()
                    source_ik_rig_path = cfg.get_source_ik_rig_path()

                    char_name = skm.get_name().split('_',1)[-1].rsplit('_',1)[0]
                    pose_name = char_name+f'_{cfg.get_default_source_pose_name()}'

                    animations = ue_retarget.retarget_animations([source_anim_path],
                                                                 rtg_asset_path=rtg_asset_path,
                                                                 source_ik_rig_path=source_ik_rig_path,
                                                                 target_ik_rig_path=ik_rig,
                                                                 target_pose_name=pose_name)

                    for anim_asset_data in animations:
                        anim_path = anim_asset_data.get_full_name().split(' ')[-1]
                        new_anim_path = os.path.join(anim_dir,
                                                     f'{str(binding.get_display_name())}_'+os.path.basename(anim_path).split('.')[0]).replace('\\', '/')

                        unreal.EditorAssetLibrary.rename_asset(anim_path,
                                                               new_anim_path)

                    ue_sequence.add_animation_to_binding(binding, new_anim_path)

                    slow_task.enter_progress_frame(0.5)
        except:
            print(traceback.format_exc())


def make_batch_request(actions, model_id, number_of_samples):
    gen_params = {
        'actions': actions,
        'modelId': str(model_id),
        'numberOfSamples': str(number_of_samples)
    }
    with unreal.ScopedSlowTask(100, 'Generating animations...') as slow_task:
        slow_task.make_dialog(can_cancel=True, allow_in_pie=True)
        r = ai_requests.request_generation(gen_params)
        task_id = utils.get_task_id_from_response(r)

        current_progress = 0
        while not ai_requests.is_task_done(task_id):
            progress = int(ai_requests.get_progress().json().get('progress'))
            slow_task.enter_progress_frame(progress - current_progress)
            current_progress = progress

        r = ai_requests.get_result(task_id)

        samples = utils.get_list_of_samples_from_response(r)

        r = ai_requests.get_fbx_from_list_of_bvh(samples).json()

        fbxs_s3 = utils.get_list_of_fbx_from_response(r)

        fbxs = []

        with unreal.ScopedSlowTask(len(fbxs_s3), 'Downloading...') as d_slow_task:
            for s3_url in fbxs_s3:
                temp_path = utils.get_temp_fbx_file_path()
                utils.download_fbx(s3_url, temp_path)

                d_slow_task.enter_progress_frame(1)

                fbxs.append(temp_path)
    return fbxs


def find_ik_rig_in_dir(directory_path):
    assets = EDITOR_ASSET_SYSTEM.list_assets(directory_path)

    for asset in assets:
        if unreal.load_asset(asset).get_class() == unreal.IKRigDefinition.static_class():
            return asset


class AnimAIDialog(QDialog):
    def __init__(self):
        super(AnimAIDialog, self).__init__()

        print(self, ' initialization')

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

    def closeEvent(self, event):
        if self.aboutToClose:
            self.aboutToClose(self)
        super().closeEvent(event)
        event.accept()

    def eventTick(self, delta_seconds):
        pass


def run():
    return window_spawner.show_window(AnimAIDialog)
