# 设置日志处理器（建议保留，防止日志警告）
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())

# 可选：版本信息
from .__version__ import __version__

# __init__.py
# 导入并重新导出FormatConvertFilter
from .pyorbbecsdk import *  # 如果这行报错，尝试下面的方式

# 或者使用__all__列表
__all__ = [
    'FormatConvertFilter', 'VideoFrame',
    'OBFormat', 'OBConvertFormat', 'OBSensorType',
    'Config', 'Pipeline' # 确保需要的类被公开
]