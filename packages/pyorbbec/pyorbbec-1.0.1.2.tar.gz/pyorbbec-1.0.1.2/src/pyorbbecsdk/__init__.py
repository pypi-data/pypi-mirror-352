# 设置日志处理器（建议保留，防止日志警告）
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())

# 可选：版本信息
from .__version__ import __version__

import pyorbbecsdk
from pyorbbecsdk import FormatConvertFilter, VideoFrame
