import re
from typing import Tuple, List


def integers_serializer(value: List[int]) -> str:
    return ", ".join([str(n) for n in value])


def integers_deserializer(value: str) -> List[int]:
    return [int(n) for n in value.replace(" ", "").split(",")]


def strings_serializer(value: List[str]) -> str:
    return ", ".join([s for s in value])


def strings_deserializer(value: str) -> List[str]:
    return [s for s in value.replace(" ", "").split(",")]


def shape_serializer(value: Tuple[int]) -> str:
    return ", ".join([str(n) for n in value])


def shape_deserializer(value: str) -> List[int]:
    return tuple(int(n) for n in value.replace(" ", "").split(","))


def rois_serializer(value: List[List[int]]) -> str:
    rois = [f"[{','.join([str(n) for n in tpl])}]" for tpl in value]
    return ", ".join(rois)


def rois_deserializer(value: str) -> List[List[int]]:
    pattern = r"\[[0-9,]+\]"
    itrois = re.finditer(pattern, value.replace(" ", ""))
    return [[int(n) for n in roi[1:-1].split(",")] for roi in itrois]
