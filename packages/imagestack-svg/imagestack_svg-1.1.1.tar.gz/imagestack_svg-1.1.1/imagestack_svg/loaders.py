import base64
import os
import re
import warnings
from typing import List

import http.client
import requests

try:
    from PySide2.QtGui import QFontDatabase
except ModuleNotFoundError:
    from PySide6.QtGui import QFontDatabase

from .helpers import http_emoji_encode, from_char, is_emoji, to_char, CacheDict


class WebImageLoader:
    def __init__(self,
                 max_cache_images: int = 20,
                 ):
        self.cached_images = CacheDict(max_size=max_cache_images)

    def get_image_bytes(self, url):
        if url in self.cached_images:
            return self.cached_images[url]
        return requests.get(url).content

    def get_base64(self, url):
        return f"data:image/jpeg;base64,{base64.b64encode(self.get_image_bytes(url)).decode('utf-8')}"

    def get_url(self, url):
        return url


class EmojiLoader:
    emoji_search_url = 'http://emojipedia.org/{}'
    emoji_search_regex = r'"source/microsoft/(.*?)"'
    emoji_match_url = 'https://em-content.zobj.net/source/microsoft/{}'

    def __init__(self,
                 emoji_path: str = None,
                 emoji_fallback: str = '🆘',
                 download_emojis: bool = False,
                 max_cache_images: int = 20,
                 save_downloaded_emojis: bool = False,
                 max_cache_links: int = 20,
                 ):
        self.save_downloaded_emojis = save_downloaded_emojis
        if emoji_path is None:
            self.save_downloaded_emojis = False
        self.emoji_path = emoji_path

        self.emoji_fallback = emoji_fallback

        self.download_emojis = download_emojis

        self.cached_links = CacheDict(max_size=max_cache_links)
        self.cached_images = CacheDict(max_size=max_cache_images)

    def get_downloaded_emojis(self):
        if not self.save_downloaded_emojis:
            return []
        emojis = []
        for e in os.listdir(self.emoji_path):
            try:
                emoji = to_char(os.path.splitext(e)[0])
                if is_emoji(emoji):
                    emojis.append({'emoji': emoji, 'path': e})
            except ValueError:
                pass
        return emojis

    def get_emoji_image_url(self, emoji: str):
        if emoji in self.cached_links:
            return self.cached_links[emoji]
        
        conn = http.client.HTTPSConnection('emojipedia.org')
        payload = ''
        headers = {}
        conn.request('GET', '/' + http_emoji_encode('🌸'), payload, headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        conn.request('GET', data, payload, headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        conn.close()
        
        match = re.search(self.emoji_search_regex, data)
        if not match:
            return None
        source = re.sub(r'\\$', '', match.group(1))
        
        return self.emoji_match_url.format(source)
    
    def get_image_bytes(self, emoji: str, do_fallback=True):
        if do_fallback and not is_emoji(emoji):
            emoji = self.emoji_fallback
        emoji_id = from_char(emoji)

        if emoji in self.cached_images:
            return self.cached_images[emoji]

        file = None
        if self.emoji_path is not None:
            file = os.path.join(self.emoji_path, emoji_id + '.png')
        if file is not None and os.path.exists(file):
            with open(file, 'rb') as f:
                img_bytes = f.read()
                self.cached_images[emoji] = img_bytes
                return img_bytes
        elif self.download_emojis:
            url = self.get_emoji_image_url(emoji)
            if url is None:
                warnings.warn('Emoji "{}" was not found on "{}"!'.format(emoji, self.emoji_search_url))
            else:
                img_bytes = requests.get(url).content
                if self.save_downloaded_emojis and file is not None:
                    with open(file, 'wb') as f:
                        f.write(img_bytes)
                self.cached_images[emoji] = img_bytes
                return img_bytes
        if do_fallback:
            return self.get_image_bytes(self.emoji_fallback, do_fallback= False)
        return b''

    def get_base64(self, emoji: str):
        image_bytes = self.get_image_bytes(emoji)

        if len(image_bytes) == 0:
            return 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='

        return f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"


class FontLoader:
    def __init__(self, fonts: List[str] = None):
        self.loaded_fonts = {}
        self.font_db = None
        self.fonts = fonts

    def initialize(self):
        self.font_db = QFontDatabase()

        if self.fonts is not None:
            for font_path in self.fonts:
                with open(font_path, 'rb') as f:
                    font_bytes = f.read()

                idx = self.font_db.addApplicationFontFromData(font_bytes)
                font_names = self.font_db.applicationFontFamilies(idx)

                if len(font_names) != 1:
                    raise ValueError('Multiple ttf fonts not supported currently')

                idx = self.font_db.addApplicationFontFromData(font_bytes)
                base64_font = base64.b64encode(font_bytes).decode('ascii')
                font_style = '@font-face {{font-family:\'{}\';' \
                             'src:url(data:application/x-font-woff;charset=utf-8;base64,{})' \
                             ' format(\'woff\');}}'.format(font_names[0], base64_font)

                self.loaded_fonts[font_names[0]] = [font_style, font_path, idx]

    def get_style(self):
        return ' '.join(map(lambda x: x[0], self.loaded_fonts.values()))
