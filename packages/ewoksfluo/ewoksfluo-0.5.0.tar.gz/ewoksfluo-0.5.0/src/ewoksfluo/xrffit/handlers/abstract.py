from typing import Optional
import numpy


class AbstractDataHandler:
    def add_points(self, value: numpy.ndarray) -> None:
        raise NotImplementedError


class AbstractOutputHandler:
    def __enter__(self) -> "AbstractOutputHandler":
        raise NotImplementedError

    def __exit__(self, *args) -> None:
        raise NotImplementedError

    def create_group(self, name: str, data: dict) -> None:
        raise NotImplementedError

    def create_nxdata_handler(
        self,
        group: str,
        name: str,
        npoints: int,
        attrs: Optional[dict] = None,
    ) -> AbstractDataHandler:
        raise NotImplementedError
