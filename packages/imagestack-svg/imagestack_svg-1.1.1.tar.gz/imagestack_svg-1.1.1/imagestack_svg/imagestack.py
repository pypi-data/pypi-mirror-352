import io
import re
from typing import List, Tuple

try:
    from PySide2.QtCore import QByteArray, QBuffer, QIODevice
    from PySide2.QtGui import QImage, QPainter, QColor
    from PySide2.QtSvg import QSvgRenderer
except ModuleNotFoundError:
    from PySide6.QtCore import QByteArray, QBuffer, QIODevice
    from PySide6.QtGui import QImage, QPainter, QColor
    from PySide6.QtSvg import QSvgRenderer

from .imagecreator import ImageCreator, SVG_PREFIX, SVG_SUFFIX
import html
from defusedxml.lxml import fromstring, tostring


class ImageStack:
    @classmethod
    def create(cls, svg: str, replace_stack: list, last_kwargs: dict):
        o = cls(svg)
        o._replace_stack = replace_stack
        o._last_kwargs = last_kwargs
        return o

    def __init__(self, svg: str):
        self.svg = svg
        self._replace_stack = []
        self._last_kwargs = {}

    def __str__(self):
        return self.svg

    async def _create_bytes(self,
                            svg: str,
                            image_format: QImage.Format = QImage.Format_RGBA64,
                            max_size: tuple = None) -> io.BytesIO:
        svg_renderer = QSvgRenderer((await self._create_raw_svg(svg)).encode())
        orig_svg = QImage(svg_renderer.defaultSize(), image_format)

        orig_svg.fill(QColor(0, 0, 0, 0))

        painter = QPainter(orig_svg)

        svg_renderer.render(painter)

        painter.end()

        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.ReadWrite)

        orig_svg.save(buffer, 'PNG', -1)
        buffer.seek(0)

        bio = io.BytesIO(buffer.readAll())

        buffer.close()
        return bio

    async def create_bytes(self,
                           image_creator: ImageCreator,
                           image_format: QImage.Format = QImage.Format_RGBA64,
                           max_size: tuple = None):
        return await self._create_bytes(self._replace(self.svg), image_format, max_size)

    async def _create_raw_svg(self, svg: str) -> str:
        return f'{SVG_PREFIX}{svg}{SVG_SUFFIX}'

    async def create_raw_svg(self, image_creator: ImageCreator) -> str:
        return await self._create_raw_svg(self._replace(self.svg))

    async def _create_inner_svg(self, svg: str) -> str:
        return svg

    async def create_inner_svg(self, image_creator: ImageCreator) -> str:
        return await self._create_inner_svg(self._replace(self.svg))

    def _replace(self, svg) -> str:
        if not self._replace_stack:
            return svg

        parsed = fromstring(f"{SVG_PREFIX}{re.sub('({%.*%})', lambda x: html.escape(x.group()), svg)}{SVG_SUFFIX}")
        for replace_id, content in self._replace_stack:
            content_parsed = fromstring(f"{SVG_PREFIX}{content}{SVG_SUFFIX}")[0]
            elements = parsed.findall(f".//*[@id = '{replace_id}']")
            for el in elements:
                el.getparent().replace(el, content_parsed)

        return re.sub('({{.*}}|{%.*%})',
                      lambda x: html.unescape(x.group()),
                      tostring(parsed).decode()[len(SVG_PREFIX):-len(SVG_SUFFIX)])

    def replace(self, replace_id: str, content: str):
        return self.create(self.svg, self._replace_stack + [(replace_id, content)], self._last_kwargs)

    def replace_all(self, replaces: List[Tuple[str, str]]):
        return self.create(self.svg, self._replace_stack + replaces, self._last_kwargs)
