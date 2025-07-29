"""
Description
===========

Web-camera based watermeter classes with leak detector

"""

from .webcamera import WebCamera
from .watermeter_ocr import WaterMeterOCR
from .watermeter_imgdiff import WaterMeterImgDiff
from .watermeter_ts import WaterMeterTs
from .leakdetector import LeakDetector

__all__ = [
    "WebCamera",
    "WaterMeterOCR",
    "WaterMeterImgDiff",
    "WaterMeterTs",
    "LeakDetector",
]
