import json
from PIL import Image
import base64
from io import BytesIO

MAX_IMAGE_SIZE = 1024


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Image.Image):  # Check if the object is a PIL Image
            return self.image_to_datauri(obj)
        elif hasattr(obj, "__dict__"):  # If the object has a dictionary (attributes)
            return obj.__dict__
        elif isinstance(obj, (set, frozenset)):  # Convert sets to lists
            return list(obj)
        elif hasattr(obj, "__str__"):  # If the object has a string representation
            return str(obj)
        else:
            return self.unsupported_to_string(obj)

    @staticmethod
    def image_to_datauri(image: Image.Image) -> str:
        """Convert a PIL Image to a Data URI in Base64 PNG format."""

        # Resize the image if it's too large
        if image.width > MAX_IMAGE_SIZE or image.height > MAX_IMAGE_SIZE:
            image.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE))

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_base64}"

    @staticmethod
    def unsupported_to_string(obj) -> dict:
        """Convert unsupported types to a type string representation."""
        return f"<{type(obj).__name__}>"
