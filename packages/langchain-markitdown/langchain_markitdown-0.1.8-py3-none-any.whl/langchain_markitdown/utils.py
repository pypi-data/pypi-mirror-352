from typing import BinaryIO, Optional, Tuple, Union
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
import base64
import io
import mimetypes

def get_image_caption(
    llm: BaseChatModel, file_stream: BinaryIO, stream_info, prompt: Optional[str] = None,
) -> Optional[str]:
    """Generates a caption for an image using a Langchain chat model."""

    if prompt is None or prompt.strip() == "":
        prompt = "Write a detailed caption for this image. If you cannot, try and describe what you see. If this is not possible simply return 'no caption provided for this image'"

    # Get the content type
    content_type = stream_info.mimetype
    if not content_type:
        content_type, _ = mimetypes.guess_type("_dummy" + (stream_info.extension or ""))
    if not content_type:
        content_type = "application/octet-stream"

    # Convert to base64
    cur_pos = file_stream.tell()
    try:
        base64_image = base64.b64encode(file_stream.read()).decode("utf-8")
    except Exception as e:
        return None
    finally:
        file_stream.seek(cur_pos)

    # Prepare the data-uri
    data_uri = f"data:{content_type};base64,{base64_image}"

    # Create a HumanMessage with the image and prompt
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": data_uri},
            },
        ]
    )

    try:
        # Invoke the Langchain model
        response = llm.invoke([message])  # Assuming .invoke() method
        return response.content
    except Exception as e:
        print(f"Error during LLM captioning: {e}")
        return None

def get_image_format(image_data: bytes) -> Tuple[str, str]:
    """
    Identifies the image format and returns the MIME type and extension.
    Replaces deprecated imghdr module with PIL-based detection.
    """
    try:
        from PIL import Image
        image = Image.open(io.BytesIO(image_data))
        
        # Get format from PIL
        img_format = image.format.lower() if image.format else None
        
        if img_format == 'jpeg':
            return "image/jpeg", ".jpg"
        elif img_format == 'png':
            return "image/png", ".png"
        elif img_format == 'gif':
            return "image/gif", ".gif"
        elif img_format == 'webp':
            return "image/webp", ".webp"
        else:
            # Default fallback if format not specifically handled
            return "application/octet-stream", ".bin"
    except ImportError:
        # Fallback if Pillow is not installed
        print("Warning: Pillow not installed. Image format detection may be less accurate.")
        # Very basic signature detection
        if image_data.startswith(b'\xff\xd8\xff'):
            return "image/jpeg", ".jpg"
        elif image_data.startswith(b'\x89PNG\r\n\x1a\n'):
            return "image/png", ".png"
        elif image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a'):
            return "image/gif", ".gif"
        elif image_data.startswith(b'RIFF') and image_data[8:12] == b'WEBP':
            return "image/webp", ".webp"
        else:
            return "application/octet-stream", ".bin"
    except Exception:
        return "application/octet-stream", ".bin"

def langchain_caption_adapter(
    file_stream: BinaryIO, stream_info, client, model, prompt: Optional[str] = None
) -> Union[None, str]:
    if not stream_info.mimetype:
        stream_info.mimetype, stream_info.extension = get_image_format(file_stream.getvalue())
    return get_image_caption(
        llm=client, file_stream=file_stream, stream_info=stream_info, prompt=prompt
    )
