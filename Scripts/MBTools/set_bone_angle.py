#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import sys
import yaml

from pydantic import BaseModel
from typing import List

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


def execute(root_bone, target_config, prefix=""):
    bones = [root_bone]
    bones.extend(get_children(root_bone))
    FBSystem().Scene.Evaluate()

    items = target_config["items"]
    for prefix in ["", "Left", "Right"]:
        is_reverse = False
        if prefix != "":
            is_reverse = target_config.get("reverse_{}".format(prefix.lower()), False)

        __do_execute(bones, items, is_reverse, prefix, "")
        FBSystem().Scene.Evaluate()

def __do_execute(bones, items, is_reverse, prefix = "", suffix = ""):
    for item in items:
        search_name = prefix + item["key"].strip(prefix).strip(suffix) + suffix
        bone = None

        for bone in bones:
            bone_name = bone.Name
            if bone.Name.endswith(search_name):
                bone = bone
                break
        if bone:
            value = item["value"]
            rotation = FBVector3d(
                value["x"] if value.get("x") is not None else bone.Rotation[0],
                value["y"] if value.get("y") is not None else bone.Rotation[1],
                value["z"] if value.get("z") is not None else bone.Rotation[2]
            )

            # is_reverse が True の場合は z 軸の回転を反転させる
            if is_reverse: rotation[2] *= -1

            bone.SetVector(rotation, FBModelTransformationType.kModelRotation, True)

# 再帰的に node の children を取得する
def get_children(root):
    children = []
    for child in root.Children:
        children.append(child)
        children.extend(get_children(child))
    return children


def set_bone_angle(template_path):
    models = FBModelList()
    FBGetSelectedModels(models)
    root_bones = []
    for m in models:
        root_bone = skeleton.get_root_skeleton(m)
        if root_bone: root_bones.append(root_bone)

    if len(set([id(s) for s in root_bones])) == 1:
        root_bone = root_bones[0]
        yaml_data = load_yaml(template_path)
        execute(root_bone, yaml_data["target"], "")

    else:
        FBMessageBox("Warning", "Please Select Actor's bone.", "OK")


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

    # template 選択の layout
    layout = FBVBoxLayout(FBAttachType.kFBAttachTop)
    grid = FBGridLayout()
    label = FBLabel()
    label.Caption = "Template:"
    grid.Add(label, 0, 0)
    template_types.Style = FBListStyle.kFBDropDownList
    template_types.MultiSelect = False

    for file_path in template_paths:
        template_name = os.path.splitext(os.path.basename(file_path))[0]
        template_types.Items.append(str(template_name))
    grid.AddRange(template_types, 0, 0, 1, 2)

    layout.Add(grid, 30)

    # Execute ボタンの layout
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
