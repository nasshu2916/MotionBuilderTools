from pyfbsdk import FBModelSkeleton


def get_root_skeleton(pSkeleton):
    if is_skeleton(pSkeleton):
        return __do_root_skeleton(pSkeleton)
    else:
        return None

def __do_root_skeleton(pSkeleton):
    parent = pSkeleton.Parent
    if is_skeleton(parent):
        return __do_root_skeleton(parent)
    else:
        return pSkeleton

def is_skeleton(pModel):
    return type(pModel) == FBModelSkeleton
