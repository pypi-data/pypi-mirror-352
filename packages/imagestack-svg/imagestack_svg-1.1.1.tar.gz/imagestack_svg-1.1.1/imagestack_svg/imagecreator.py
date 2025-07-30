try:
    from PySide2.QtGui import QImage
    from PySide2.QtWidgets import QApplication
except ModuleNotFoundError:
    from PySide6.QtGui import QImage
    from PySide6.QtWidgets import QApplication

import asyncio
import threading
import jinja2.sandbox

from .loaders import FontLoader, WebImageLoader, EmojiLoader
from .helpers import AsyncEvent

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import io
    from .imagestack import ImageStack


SVG_PREFIX = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">'
SVG_SUFFIX = '</svg>'


class ImageCreator:
    def __init__(self,
                 font_loader: FontLoader = None,
                 web_image_loader: WebImageLoader = None,
                 emoji_loader: EmojiLoader = None,
                 ):

        try:
            QApplication([])
        except RuntimeError:
            pass

        if font_loader is None:
            font_loader = FontLoader()

        self.font_loader = font_loader
        self.font_loader.initialize()

        if web_image_loader is None:
            web_image_loader = WebImageLoader()

        self.web_image_loader = web_image_loader

        if emoji_loader is None:
            emoji_loader = EmojiLoader()

        self.emoji_loader = emoji_loader

        self.jinja2_create_bytes_env = jinja2.sandbox.ImmutableSandboxedEnvironment()
        self.jinja2_create_bytes_env.filters['emoji'] = self.emoji_loader.get_base64
        self.jinja2_create_bytes_env.filters['web_image'] = self.web_image_loader.get_base64

        self.jinja2_create_svg_env = jinja2.sandbox.ImmutableSandboxedEnvironment()
        self.jinja2_create_svg_env.filters['emoji'] = self.emoji_loader.get_base64
        self.jinja2_create_svg_env.filters['web_image'] = self.web_image_loader.get_url

    async def create_bytes(self,
                           stack: 'ImageStack',
                           image_format: QImage.Format = QImage.Format_RGBA64,
                           max_size=(-1, -1)) -> Optional['io.BytesIO']:
        if stack is None:
            return None

        class _CreateImage:
            def __init__(self, image_creator: ImageCreator, event: asyncio.Event):
                self.result = None
                self.error = None
                self.image_creator = image_creator
                self.event = event

            def create(self):
                loop = asyncio.new_event_loop()
                loop.run_until_complete(self._async_create())

            async def _async_create(self):
                try:
                    self.result = await stack.create_bytes(image_creator=self.image_creator,
                                                           image_format=image_format,
                                                           max_size=max_size)
                except Exception as err:
                    self.error = err
                self.event.set()

        e = AsyncEvent()
        ci = _CreateImage(self, e)

        threading.Thread(target=ci.create).start()
        await e.wait()
        if ci.error is not None:
            raise ci.error

        return ci.result

    async def create_raw_svg(self, stack: 'ImageStack') -> str:
        return await stack.create_raw_svg(image_creator=self)

    async def create_inner_svg(self, stack: 'ImageStack') -> str:
        return await stack.create_inner_svg(image_creator=self)

    async def create_style(self) -> str:
        return self.font_loader.get_style()

    async def create_full_svg(self, stack: 'ImageStack') -> str:
        return f'{SVG_PREFIX}<style>{await self.create_style()}</style>{await self.create_inner_svg(stack)}{SVG_SUFFIX}'
