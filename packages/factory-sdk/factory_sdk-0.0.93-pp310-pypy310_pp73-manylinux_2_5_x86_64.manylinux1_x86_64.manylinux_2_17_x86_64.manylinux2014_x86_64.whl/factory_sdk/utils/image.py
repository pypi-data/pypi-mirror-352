from PIL import Image
from io import BytesIO
import base64


def pil_to_datauri(image: Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
