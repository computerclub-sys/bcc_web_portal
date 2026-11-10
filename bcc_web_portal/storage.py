import os

import cloudinary
import cloudinary.uploader
import cloudinary.utils
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.utils.deconstruct import deconstructible
from whitenoise.storage import CompressedManifestStaticFilesStorage


class SafeManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """Keep hashed static URLs but fall back instead of raising a 500.

    A stale ``staticfiles.json`` (for example, a newly added image that has not
    been collected yet) should serve the unhashed path, not break the page.
    """

    manifest_strict = False


@deconstructible
class NoCompressCloudinaryStorage(MediaCloudinaryStorage):
    def _upload(self, name, content):
        options = {
            'use_filename': True,
            'resource_type': self._get_resource_type(name),
            'tags': self.TAG,
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
        )
        return url
