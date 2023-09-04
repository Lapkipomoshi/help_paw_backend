import io
from PIL import Image as PIL_Image


def get_image_data(target_size_bytes=1000):
    size = 10000
    while True:
        image = PIL_Image.new("RGB", (size, size))
        image_data = io.BytesIO()
        image.save(image_data, format="JPEG")

        if len(image_data.getvalue()) > target_size_bytes:
            break
        size += 10000
    return image_data.getvalue()
