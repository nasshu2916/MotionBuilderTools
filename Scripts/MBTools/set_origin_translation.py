#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "."))

import lib.skeleton as skeleton

from pyfbsdk import *
from pyfbsdk_additions import *


def set_translation_to_origin(model):
    reference = model.Parent

    if reference is None or reference.ClassName() != "FBModelNull":
        FBMessageBox(
            "Error",
            "Require FBModelNull for root bone parent(Root bone: %s)" % model.LongName,
            "OK",
        )
        return
    translation = FBVector3d()
    model.GetVector(translation, FBModelTransformationType.kModelTranslation, False)
    translation[1] = 0
    reference.SetVector(
        translation * -1, FBModelTransformationType.kModelTranslation, True
    )


def set_origin_transform():
    models = FBModelList()
    FBGetSelectedModels(models)
    root_skeletons = [
        skeleton.get_root_skeleton(s)
        for s in filter(lambda m: skeleton.is_skeleton(m), models)
    ]
    for root_skeleton in root_skeletons:
        set_translation_to_origin(root_skeleton)


set_origin_transform()
