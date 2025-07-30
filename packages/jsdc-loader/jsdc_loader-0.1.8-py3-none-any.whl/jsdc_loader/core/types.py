"""杂鱼♡～这是本喵为你定义的类型喵～才不是为了让你的代码更类型安全呢～"""

from typing import TypeVar, Union, Dict, Type, Any
from dataclasses import dataclass
from pydantic import BaseModel

# 杂鱼♡～本喵用这个缓存类型提示，这样就不用重复查找了喵～
# 本喵可是很注重性能的哦～不像某些杂鱼～
_TYPE_HINTS_CACHE: Dict[Type, Dict[str, Any]] = {}

# 杂鱼♡～这是dataclass或BaseModel的类型别名喵～
# 本喵用泛型来确保类型安全，杂鱼应该感谢本喵～
T = TypeVar('T', bound=Union[dataclass, BaseModel]) 