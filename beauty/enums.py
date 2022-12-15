from enum import Enum


class Origin(str, Enum):
    netbian = "www.netbian.com"
    win3000 = "www.win3000.com"
    bcoderss = "m.bcoderss.com"
    cnmo = "m.cnmo.com"


class PictureCategory(str, Enum):
    beauty = "美女"
    scenery = "风景"
