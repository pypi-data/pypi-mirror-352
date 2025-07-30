<div align="center">
  <h1>yors_comfyui_node_setup</h1>
  <p>
    <strong>🤖 A python library for setup comfyui custom nodes for developers in development.</strong>
  </p>
  
  ![PyPI - Version](https://img.shields.io/pypi/v/yors_comfyui_node_setup)
  ![PyPI - License](https://img.shields.io/pypi/l/yors_comfyui_node_setup)

</div>

to setup comfyui custom nodes for developers in development:

- install requriements automatically for nodes
- entry - export comfyui node vars automatically

## Why

- setup your comfyui nodes easily
- install requirements automatically (easy and optional)
- set your comfyui nodes to right mouse menu as your likes (easy and optional)

## 1 - install python package

```bash
pip install yors_comfyui_node_setup
# yors_comfyui_node_util
```

## 2 - use it in your python code

- in some comfyui custom nodes project or module

- code in `__init__.py`

```py
# ucase 1.0:
# from yors_comfyui_node_setup import entry,node_install_requirements # global

# # install requirements
# node_install_requirements(__file__)

# # export comfyui node vars
# __all__,NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES = entry(__name__,__file__)

# ucase 2.0:
from yors_comfyui_node_setup import node_install_requirements,entry_pre_import,entry_import,get_all_classs_in_sys,register_node_list_local

# install requirements automatically
# if requrements.txt in here and deps in it not installed
node_install_requirements(__file__)

# gen __all__ and import moudle with __all__
# with this you can wirte your nodes in any py file in the same diretory
__all__ = entry_pre_import(__name__,__file__)
entry_import(__name__,__all__)

# get class after importing moudle with __all__
this_module_all_classes = get_all_classs_in_sys(__name__)

# register node with default category
# it will not register the same node if you/he/she register the same nodes in other custom repo. (save disk space)
NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES  = register_node_list_local(this_module_all_classes,False)

# addtional register node with custom category (no test)
# NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES  = register_node_list_local(this_module_all_classes,True,"YMC/as_x_type")
print("\n".join(NODE_MENU_NAMES))
```

## 3 - code yours nodes

- dirs map of your node may be:

```
.
└─__init__.py
└─nodes.py
```

- in any py file (no test in `__init__.py`)
- code nodes.py

```py
# 1. define yors comfyui nodes here
# ...
# ucase 1.0:
# class AnyType(str):
#   """A special class that is always equal in not equal comparisons. Credit to pythongosssss"""

#   def __ne__(self, __value: object) -> bool:
#     return False

# any_type = AnyType("*")


# CURRENT_CATEGORY="YMC/LINK" # set the right mouse button menu (custom for your comfyui nodes)
# CURRENT_FUNCTION="exec"

# class NodeSetItAsImage:
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {

#             },
#             "optional":{
#                 "a": (any_type),
#             },
#             # "hidden": {
#             #     "unique_id": "UNIQUE_ID",
#             #     "extra_pnginfo": "EXTRA_PNGINFO",
#             # },
#         }

#     # INPUT_IS_LIST = True
#     RETURN_TYPES = ("IMAGE",)
#     RETURN_NAMES = ("image",)

#     FUNCTION = CURRENT_FUNCTION
#     CATEGORY = CURRENT_CATEGORY
#     # set NODE_NAME and NODE_DESC for yors_comfyui_node_setup
#     NODE_NAME = "as image"
#     NODE_DESC = "set it as image type"
#     # OUTPUT_NODE = True
#     # OUTPUT_IS_LIST = (True,)
#     def exec(self, a=None):
#         return (a,)


# ucase 1.1:
from yors_comfyui_node_as_x_type import * # import all yors comfyui nodes from it

# ucase 1.2:
# from yors_comfyui_node_as_x_type import NodeSetItAsImage # import some yors comfyui nodes from it


# 2. reset yors comfyui nodes category (it will be used set rmb in yors_comfyui_node_setup)
# from yors_comfyui_node_reset_rmb import reset_rmb
# reset_rmb(__name__,"YMC/as_x_type") // danger!

# 3. set nodes category alias
# to set the right mouse menu as your likes.

# set nodes defined in yors_comfyui_node_as_x_type under the category YMC/as_x_type
import yors_comfyui_node_as_x_type as base
from yors_comfyui_node_setup import get_sys_module,set_node_class_category_alias
this_py_module = get_sys_module(__name__)
set_node_class_category_alias(base,this_py_module,"YMC/as_x_type",True)

```

## the dirs of your comfyui nodes repo

```
.
│  .gitignore
│  LICENSE
│  nodes.py
│  requirements.txt
│  __init__.py
└─link # some nodes to link nodes
    __init__.py
    xx.py
    ...
└─utils # some nodes for util process
    __init__.py
    xx.py
    ...
└─image # some nodes for image process
    __init__.py
    xx.py
    ...
```

## Author

ymc-github <ymc.github@gmail.com>

## License

MIT
