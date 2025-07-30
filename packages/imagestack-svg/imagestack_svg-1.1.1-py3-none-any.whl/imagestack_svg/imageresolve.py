try:
    from PySide2.QtGui import QImage
except ModuleNotFoundError:
    from PySide6.QtGui import QImage

from .imagestack import ImageStack
from .imagecreator import ImageCreator


class ImageStackResolveString(ImageStack):
    async def create_bytes(self,
                           image_creator: ImageCreator,
                           image_format: QImage.Format = QImage.Format_RGBA64,
                           max_size: tuple = None):

        template = image_creator.jinja2_create_bytes_env.from_string(self._replace(self.svg))
        return await super()._create_bytes(template.render(**self._last_kwargs),
                                           image_format,
                                           max_size)

    async def create_raw_svg(self, image_creator: ImageCreator):
        template = image_creator.jinja2_create_svg_env.from_string(self._replace(self.svg))
        return await super()._create_raw_svg(template.render(**self._last_kwargs))

    async def create_inner_svg(self, image_creator: ImageCreator):
        template = image_creator.jinja2_create_svg_env.from_string(self._replace(self.svg))
        return await super()._create_inner_svg(template.render(**self._last_kwargs))

    def __call__(self, **kwargs):
        self._last_kwargs = kwargs
        return self
