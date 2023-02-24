#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import re
import xml.etree.ElementTree as ET

from pyfbsdk import *
from pyfbsdk_additions import *

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "Config")
template_types = FBList()
template_paths = []
config = FBConfigFile(
    str(os.path.join(os.path.dirname(__file__), "MBTools_config.txt"))
)
prefix_regex = config.Get("SetBoneAngle", "prefix_regex") or r"^(.*_)[\w-]+$"


def execute(root_bone, bone_rotation_map, prefix=""):
    skeletons = [root_bone]
    skeletons.extend(get_children(root_bone))
    FBSystem().Scene.Evaluate()

    for skeleton in skeletons:
        bone_name = skeleton.Name.lstrip(prefix)
        if bone_name in bone_rotation_map:
            bone_rotation = bone_rotation_map[bone_name]
            current_rotation = FBVector3d()
            skeleton.GetVector(
                current_rotation, FBModelTransformationType.kModelRotation
            )

            rotation = FBVector3d(
                bone_rotation.get("x", current_rotation[0]),
                bone_rotation.get("y", current_rotation[1]),
                bone_rotation.get("z", current_rotation[2]),
            )
            is_local = bone_rotation.get("local") or False

            skeleton.SetVector(
                rotation,
                FBModelTransformationType.kModelRotation,
                not is_local,
            )
            FBSystem().Scene.Evaluate()


def get_children(root):
    children = []
    for child in root.Children:
        children.append(child)
        children.extend(get_children(child))
    return children


def get_bone_rotation_map(path):
    bone_rotation_map = {}
    parsed_xml_file = ET.parse(path)
    for item in parsed_xml_file.iter("item"):
        bone_name = item.attrib.get("key")

        rotation = {}
        for key in ["x", "y", "z"]:
            value = item.attrib.get(key)
            if value:
                rotation[key] = float(value)

        if any(rotation):
            if item.attrib.get("local"):
                rotation["local"] = True
            bone_rotation_map[bone_name] = rotation

    return bone_rotation_map


def is_skeleton(model):
    return type(model) == FBModelSkeleton


def get_root_skeleton(skeleton):
    if is_skeleton(skeleton.Parent):
        return get_root_skeleton(skeleton.Parent)
    else:
        return skeleton


def get_bone_prefix(skeleton):
    result = re.match(prefix_regex, skeleton.Name)
    return result.group(1) if result else ""


def set_bone_angle(template_path):
    models = FBModelList()
    FBGetSelectedModels(models)
    root_skeletons = [
        get_root_skeleton(s) for s in filter(lambda m: is_skeleton(m), models)
    ]

    if len(set([id(s) for s in root_skeletons])) == 1:
        root_bone = root_skeletons[0]
        bone_rotation_map = get_bone_rotation_map(template_path)
        bone_prefix = get_bone_prefix(root_bone)
        execute(root_bone, bone_rotation_map, bone_prefix)

    else:
        FBMessageBox("Warning", "Please Select Actor's bone.", "OK")


def prefix_regex_on_change(control, _event):
    global prefix_regex
    prefix = control.Text
    prefix_regex = r"{}".format(prefix)


def btn_callback(_control, _event):
    template_path = template_paths[template_types.ItemIndex]
    config.Set(
        "SetBoneAngle",
        "last_execute_template_name",
        template_types.Items[template_types.ItemIndex],
    )
    set_bone_angle(template_path)


def populate_layout(main_layout):
    main_layout_name = "main"
    x = FBAddRegionParam(10, FBAttachType.kFBAttachLeft, "")
    y = FBAddRegionParam(10, FBAttachType.kFBAttachTop, "")
    w = FBAddRegionParam(-10, FBAttachType.kFBAttachRight, "")
    h = FBAddRegionParam(-10, FBAttachType.kFBAttachBottom, "")
    main_layout.AddRegion(main_layout_name, main_layout_name, x, y, w, h)

    layout = FBVBoxLayout(FBAttachType.kFBAttachTop)
    grid = FBGridLayout()
    label = FBLabel()
    label.Caption = "Template:"
    grid.Add(label, 0, 0)
    template_types.Style = FBListStyle.kFBDropDownList
    template_types.MultiSelect = False

    last_execute_template_name = config.Get(
        "SetBoneAngle", "last_execute_template_name"
    )
    for file_path in glob.glob(os.path.join(CONFIG_DIR, "*.xml")):
        template_name = os.path.splitext(os.path.basename(file_path))[0]
        template_paths.append(file_path)
        template_types.Items.append(str(template_name))
        if template_name == last_execute_template_name:
            template_types.ItemIndex = len(template_paths) - 1
    grid.AddRange(template_types, 0, 0, 1, 2)

    label = FBLabel()
    label.Caption = "Prefix Regex:"
    grid.Add(label, 1, 0)
    bone_prefix = FBEdit()
    bone_prefix.Text = prefix_regex
    bone_prefix.OnChange.Add(prefix_regex_on_change)
    grid.AddRange(bone_prefix, 1, 1, 1, 2)
    layout.Add(grid, 60)

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
    t.StartSizeY = 180
    populate_layout(t)
    ShowTool(t)


if __name__ in ("__main__", "__builtin__"):
    create_tool()
