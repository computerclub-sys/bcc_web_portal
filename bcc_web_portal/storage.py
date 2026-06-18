import os

import cloudinary
import cloudinary.uploader
import cloudinary.utils
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class NoCompressCloudinaryStorage(MediaCloudinaryStorage):
    def _upload(self, name, content):
        options = {
            'use_filename': True,
            'resource_type': self._get_resource_type(name),
            'tags': self.TAG,
            'quality': 100,
            'fetch_format': '',
        }
        folder = os.path.dirname(name)
        if folder:
            options['folder'] = folder
        return cloudinary.uploader.upload(content, **options)

    def _get_url(self, name):
        name = self._prepend_prefix(name)
        url, _ = cloudinary.utils.cloudinary_url(
            name,
            resource_type=self._get_resource_type(name),
            secure=True,
            quality=100,
            fetch_format='',
        )
        return url
