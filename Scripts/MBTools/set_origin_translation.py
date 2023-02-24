#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "."))

import lib.skeleton as skeleton

from pyfbsdk import *
from pyfbsdk_additions import *


def set_origin_transform():
    models = FBModelList()
    FBGetSelectedModels(models)
    root_skeletons = [
        skeleton.get_root_skeleton(s)
        for s in filter(lambda m: skeleton.is_skeleton(m), models)
    ]
    if len(root_skeletons) != 1:
        FBMessageBox("Error", "Please select a model", "OK")
        return

    model = root_skeletons[0]
    reference = model.Parent
    if reference is None or reference.ClassName() != "FBModelNull":
        FBMessageBox("Error", "Require FBModelNull for root bone parent", "OK")
        return

    root_bone_translation = FBVector3d()
    model.GetVector(
        root_bone_translation, FBModelTransformationType.kModelTranslation, False
    )
    root_bone_translation[1] = 0

    print("set origin translation")
    reference.SetVector(
        root_bone_translation * -1, FBModelTransformationType.kModelTranslation, True
    )


if __name__ in ("__main__", "__builtin__"):
    set_origin_transform()
