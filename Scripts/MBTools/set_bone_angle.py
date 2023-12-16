#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import re
import sys
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), "."))
import lib.skeleton as skeleton

from pyfbsdk import *
from pyfbsdk_additions import *

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "Config", "BoneAngle")
template_types = FBList()
template_paths = []
for file_path in glob.glob(os.path.join(CONFIG_DIR, "*.yml")):
    template_paths.append(file_path)


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)
    return yaml_data


def normalize_string(s):
    """
    文字列を正規化する
    アンダースコアを取り除き、単語の先頭を大文字のキャメルケースに変換する
    """
    s = s.replace("-", "_")
    return re.sub(r'_([a-z])', lambda m: m.group(1).upper(), s)


def execute(root_bone, target_config):
    bones = [root_bone]
    bones.extend(get_children(root_bone))
    FBSystem().Scene.Evaluate()
    items = target_config["items"]

    __do_execute(bones, items)

    for affix in ["Left", "Right"]:
        is_reverse = target_config.get("reverse_{}".format(affix.lower()), False)

        if is_reverse == False:
            # reverse が指定されていない場合は affix なしで回転済みなのでスキップする
            print("skip: {}".format(affix))
            continue

        # affix の頭文字も実行対象にする
        for execute_affix in [affix, affix[0]]:
            __do_execute(bones, items, is_reverse, execute_affix, "")
            __do_execute(bones, items, is_reverse, "", execute_affix)
    FBSystem().Scene.Evaluate()


def __do_execute(bones, items, is_reverse=False, prefix="", suffix=""):
    for item in items:
        search_name = prefix + item["key"] + suffix
        search_name = normalize_string(search_name)

        for bone in __search_bones(bones, search_name):
            value = item["value"]
            bone_rotation = FBVector3d()
            bone.GetVector(bone_rotation, FBModelTransformationType.kModelRotation, True)
            # value に x, y, z が指定されている場合はその値を設定する
            # null や指定されていない場合は現在の値を設定する
            rotation = FBVector3d(
                value["x"] if value.get("x") is not None else bone_rotation[0],
                value["y"] if value.get("y") is not None else bone_rotation[1],
                value["z"] if value.get("z") is not None else bone_rotation[2]
            )

            # is_reverse が True の場合は z 軸の回転を反転させる
            if is_reverse: rotation[2] *= -1
            bone.SetVector(rotation, FBModelTransformationType.kModelRotation, True)


def __search_bones(bones, search_name):
    "search_name に一致する bone を取得する"

    result = []
    for bone in bones:
        if normalize_string(bone.Name).endswith(search_name):
            result.append(bone)

    return result


def get_children(root):
    "再帰的に node の children を取得する"

    children = []
    for child in root.Children:
        children.append(child)
        children.extend(get_children(child))
    return children


def set_bone_angle(template_path):
    print("set_bone_angle, template_path: {}".format(template_path))
    models = FBModelList()
    FBGetSelectedModels(models)
    root_bones = []
    for m in models:
        root_bone = skeleton.get_root_skeleton(m)
        if root_bone: root_bones.append(root_bone)

    if len(set([id(s) for s in root_bones])) == 1:
        root_bone = root_bones[0]
        yaml_data = load_yaml(template_path)
        execute(root_bone, yaml_data["target"])

    else:
        FBMessageBox("Warning", "Please Select Actor's bone.", "OK")


def on_choose_template(control, event):
    dialog = FBFilePopup()
    dialog.Style = FBFilePopupStyle.kFBFilePopupOpen
    dialog.Filter = '*.yml'
    dialog.Path = CONFIG_DIR

    if dialog.Execute():
        file_path = dialog.FullFilename
        filename = os.path.basename(file_path)

        template_types.Items.removeAll()
        template_types.Items.append(filename)
        template_types.ItemIndex = 0
        template_paths.clear()
        template_paths.append(file_path)


def btn_callback(_control, _event):
    template_path = template_paths[template_types.ItemIndex]
    set_bone_angle(template_path)


def populate_layout(main_layout):
    main_layout_name = "main"
    x = FBAddRegionParam(10, FBAttachType.kFBAttachLeft, "")
    y = FBAddRegionParam(10, FBAttachType.kFBAttachTop, "")
    w = FBAddRegionParam(-10, FBAttachType.kFBAttachRight, "")
    h = FBAddRegionParam(-10, FBAttachType.kFBAttachBottom, "")
    main_layout.AddRegion(main_layout_name, main_layout_name, x, y, w, h)

    # template 選択
    layout = FBVBoxLayout(FBAttachType.kFBAttachTop)
    grid = FBGridLayout()
    label = FBLabel()
    label.Caption = "Template:"
    grid.AddRange(label, 0, 0, 0, 3)
    template_types.Style = FBListStyle.kFBDropDownList
    template_types.MultiSelect = False

    for file_path in template_paths:
        template_name = os.path.splitext(os.path.basename(file_path))[0]
        template_types.Items.append(str(template_name))
    grid.AddRange(template_types, 0, 0, 3, 9)

    # テンプレート選択ボタン
    button = FBButton()
    button.Caption = ".."
    button.Hint = "Choose template file"
    button.Justify = FBTextJustify.kFBTextJustifyCenter
    grid.Add(button, 0, 10)
    button.OnClick.Add(on_choose_template)

    layout.Add(grid, 30)

    # Execute ボタン
    button = FBButton()
    button.Caption = "Execute"
    button.Hint = ""
    button.Justify = FBTextJustify.kFBTextJustifyCenter
    button.Look = FBButtonLook.kFBLookColorChange
    layout.Add(button, 40, space=15)
    button.OnClick.Add(btn_callback)

    main_layout.SetControl(main_layout_name, layout)


def create_tool():
    t = FBCreateUniqueTool("Set Bone angle from template")
    t.StartSizeX = 350
    t.StartSizeY = 150
    populate_layout(t)
    ShowTool(t)


create_tool()
