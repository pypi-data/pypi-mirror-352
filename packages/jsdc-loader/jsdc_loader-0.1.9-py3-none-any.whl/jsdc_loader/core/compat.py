"""杂鱼♡～这是本喵为你设计的兼容性模块喵～用来处理可选依赖～"""

from typing import Any, Optional, Type
import warnings

# 杂鱼♡～本喵尝试导入 pydantic，如果失败就设置为 None 喵～
try:
    from pydantic import BaseModel
    HAS_PYDANTIC = True
    # 杂鱼♡～本喵顺便检查一下 pydantic 的版本喵～
    try:
        from pydantic import VERSION
        PYDANTIC_V2 = int(VERSION.split('.')[0]) >= 2
    except ImportError:
        # 杂鱼♡～老版本的 pydantic 没有 VERSION 属性喵～
        PYDANTIC_V2 = False
except ImportError:
    BaseModel = None
    HAS_PYDANTIC = False
    PYDANTIC_V2 = False


def is_pydantic_model(obj: Any) -> bool:
    """杂鱼♡～本喵帮你检查对象是否是 Pydantic 模型喵～"""
    if not HAS_PYDANTIC:
        return False
    return isinstance(obj, type) and issubclass(obj, BaseModel)


def is_pydantic_instance(obj: Any) -> bool:
    """杂鱼♡～本喵帮你检查对象是否是 Pydantic 模型实例喵～"""
    if not HAS_PYDANTIC:
        return False
    return isinstance(obj, BaseModel)


def validate_pydantic_available(operation: str = "此操作") -> None:
    """杂鱼♡～本喵检查 pydantic 是否可用喵～如果不可用就报错～"""
    if not HAS_PYDANTIC:
        raise ImportError(
            f"杂鱼♡～{operation}需要 pydantic 支持喵！～\n"
            f"请运行: pip install jsdc_loader[pydantic] 来安装 pydantic 支持喵～\n"
            f"或者运行: pip install pydantic>=1.8.0\n"
            f"本喵才不是故意为难杂鱼的呢～～"
        )


def create_pydantic_from_dict(model_cls: Type, data: dict) -> Any:
    """杂鱼♡～本喵帮你从字典创建 Pydantic 模型实例喵～"""
    validate_pydantic_available("从字典创建 Pydantic 模型")
    
    if PYDANTIC_V2:
        # 杂鱼♡～Pydantic V2 使用 model_validate 喵～
        return model_cls.model_validate(data)
    else:
        # 杂鱼♡～Pydantic V1 使用 parse_obj 喵～
        return model_cls.parse_obj(data)


def pydantic_to_dict(instance: Any) -> dict:
    """杂鱼♡～本喵帮你把 Pydantic 模型实例转换为字典喵～"""
    validate_pydantic_available("Pydantic 模型转字典")
    
    if PYDANTIC_V2:
        # 杂鱼♡～Pydantic V2 使用 model_dump 喵～
        return instance.model_dump()
    else:
        # 杂鱼♡～Pydantic V1 使用 dict 方法喵～
        return instance.dict()


def get_pydantic_basemodel() -> Optional[Type]:
    """杂鱼♡～本喵返回 BaseModel 类，如果没有安装 pydantic 就返回 None 喵～"""
    return BaseModel if HAS_PYDANTIC else None


def warn_pydantic_feature(feature_name: str) -> None:
    """杂鱼♡～本喵在杂鱼使用 pydantic 功能但没安装时给出警告喵～"""
    if not HAS_PYDANTIC:
        warnings.warn(
            f"杂鱼♡～检测到你想使用 {feature_name} 功能但没有安装 pydantic 喵～\n"
            f"请运行 pip install jsdc_loader[pydantic] 来获得完整功能支持喵～\n"
            f"本喵现在只能使用 dataclass 功能了～～",
            UserWarning,
            stacklevel=3
        ) 