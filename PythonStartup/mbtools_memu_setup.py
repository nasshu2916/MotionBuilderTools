import glob
import os

from pyfbsdk import FBApplication, FBMenuManager

MENU_NAME = "Tools"
SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "Scripts", "MBTools")


def event_menu(_control, event):
    script_file = script_dic[event.Name]
    FBApplication().ExecuteScript(script_file)


def add_menu(root_menu, script_dir):
    script_files = glob.glob(os.path.join(script_dir, "*.py"))

    i = 0
    for file_path in script_files:
        file_path = str(file_path)
        i += 1
        basename = os.path.basename(file_path).strip(".py")
        root_menu.InsertLast(basename, i)
        script_dic[basename] = file_path
    root_menu.OnMenuActivate.Add(event_menu)


menu_manager = FBMenuManager()
menu_manager.InsertAfter("", "PythonTools", MENU_NAME)
menu = menu_manager.GetMenu(MENU_NAME)

script_dic = {}
add_menu(menu, SCRIPT_DIR)
