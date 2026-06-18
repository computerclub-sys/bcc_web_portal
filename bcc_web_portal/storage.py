from cloudinary_storage.storage import MediaCloudinaryStorage


class HighQualityCloudinaryStorage(MediaCloudinaryStorage):
    def url(self, name):
        url = super().url(name)
        parts = url.split('/upload/')
        if len(parts) == 2:
            return f"{parts[0]}/upload/q_50/{parts[1]}"
        return url
