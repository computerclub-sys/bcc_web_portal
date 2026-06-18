import os

import cloudinary.uploader
from cloudinary_storage.storage import MediaCloudinaryStorage


class HighQualityCloudinaryStorage(MediaCloudinaryStorage):
    def _upload(self, name, content):
        options = {
            'use_filename': True,
            'resource_type': self._get_resource_type(name),
            'tags': self.TAG,
            'quality': 100,
            'colorspace': 'srgb',
        }
        folder = os.path.dirname(name)
        if folder:
            options['folder'] = folder
        return cloudinary.uploader.upload(content, **options)

    def url(self, name):
        url = super().url(name)
        parts = url.split('/upload/')
        if len(parts) == 2:
            return f"{parts[0]}/upload/q_100/{parts[1]}"
        return url
