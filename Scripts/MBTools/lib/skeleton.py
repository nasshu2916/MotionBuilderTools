from pyfbsdk import FBModelSkeleton


def get_root_skeleton(pSkeleton):
    if is_skeleton(pSkeleton.Parent):
        return get_root_skeleton(pSkeleton.Parent)
    else:
        return pSkeleton


def is_skeleton(pModel):
    return type(pModel) == FBModelSkeleton
