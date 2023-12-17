# MotionBuilderTools

## SetBoneAngle

![SetBoneAngle](Docs/set_bone_angle.gif)

Sets the bones of the selected skeleton to the angles defined in the Template.

### Function

- Set Bones of the selected skeleton to the angles defined in any template.
  - Bone angles set global.
- Set bone angles for both left and right bones at the same time.

### Usage

1. Select the skeleton whose bones you want to rotate.
2. Select the template file (drop-down list or file selection button).
3. Click the execute button.

### Template File

The template file is a yaml file that defines the bone angles.

```yml
target:
  items: # rotation target bones (required)
      - key: "BoneName" # bone name (Left or Right is not required)
        value: {x: 0, y: 0, z: 0} # if null or not defined, the bone is not rotated.
  reverse_right: true # default: false (optional)
  reverse_left: false # default: false (optional)
```

## Install

- Copy `PythonStartup` and `Scripts` to MotionBuilder's `config` directory(eg. `C:\Program Files\Autodesk\MotionBuilder ${version}\config`).
- Install the requirements.txt package.
  - `setup.bat` is provided for convenience.
