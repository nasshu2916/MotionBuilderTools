from pyfbsdk import FBModelSkeleton

def get_root_bone(bone):
    "再帰的に親をたどって root bone を取得する"

    if is_skeleton(bone):
        return __do_root_bone(bone)
    else:
        return None

def __do_root_bone(bone):
    parent = bone.Parent
    if is_skeleton(parent):
        return __do_root_bone(parent)
    else:
        return bone

def is_skeleton(model):
    return type(model) == FBModelSkeleton
