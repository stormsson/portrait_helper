"""Image loading library for Portrait Helper."""

import logging
from pathlib import Path
from typing import Optional
from PIL import Image as PILImage

# Error handling infrastructure
logger = logging.getLogger(__name__)

# Custom exceptions for image loading
class ImageLoadError(Exception):
    """Base exception for image loading errors."""
    pass

class ImageFormatError(ImageLoadError):
    """Raised when image format is invalid or unsupported."""
    pass

class ImageCorruptionError(ImageLoadError):
    """Raised when image data is corrupted."""
    pass


class Image:
    """Represents a loaded image with its properties and current display state."""

    def __init__(
        self,
        width: int,
        height: int,
        format: str,
        source: str,
        pixel_data: Optional[PILImage.Image] = None,
        source_path: Optional[str] = None,
        source_url: Optional[str] = None,
    ):
        """Initialize Image entity.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            format: Image format (JPEG, PNG, GIF, BMP, WebP)
            source: Original source (file path or URL)
            pixel_data: Pillow Image object
            source_path: Local file path if loaded from file system
            source_url: Web URL if loaded from network
        """
        if source_path and source_url:
            raise ValueError("Cannot set both source_path and source_url")
        if not source_path and not source_url:
            raise ValueError("Either source_path or source_url must be set")

        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")

        self.width = width
        self.height = height
        self.aspect_ratio = width / height if height > 0 else 1.0
        self.format = format
        self.source = source
        self.pixel_data = pixel_data
        self.source_path = source_path
        self.source_url = source_url
        self.is_loaded = pixel_data is not None
        self.load_error: Optional[str] = None

        logger.debug(f"Image entity created: {width}x{height}, format={format}, source={source}")

    def get_pixel_data(self) -> PILImage.Image:
        """Returns Pillow Image object.

        Returns:
            PIL.Image object

        Raises:
            ValueError: If image data is not loaded
        """
        if not self.is_loaded or self.pixel_data is None:
            raise ValueError("Image data is not loaded")
        return self.pixel_data

    def is_valid(self) -> bool:
        """Checks if image data is valid.

        Returns:
            True if image is loaded and valid, False otherwise
        """
        if not self.is_loaded:
            return False
        if self.pixel_data is None:
            return False
        try:
            self.pixel_data.verify()
            return True
        except Exception:
            return False

    def get_metadata(self) -> dict:
        """Returns image metadata as dictionary.

        Returns:
            Dictionary with image metadata
        """
        return {
            "width": self.width,
            "height": self.height,
            "aspect_ratio": self.aspect_ratio,
            "format": self.format,
            "source": self.source,
            "is_loaded": self.is_loaded,
            "source_path": self.source_path,
            "source_url": self.source_url,
        }


def load_from_file(file_path: str) -> Image:
    """Load an image from a local file path.

    Args:
        file_path: Path to image file

    Returns:
        Image object with loaded pixel data and metadata

    Raises:
        FileNotFoundError: File does not exist
        ValueError: Invalid image format or corrupted data
        IOError: File cannot be read
    """
    path = Path(file_path)

    if not path.exists():
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        logger.error(f"Path is not a file: {file_path}")
        raise ValueError(f"Path is not a file: {file_path}")

    try:
        # Open and load image using Pillow
        pil_image = PILImage.open(path)
        # Convert to RGB if necessary (handles RGBA, P, etc.)
        if pil_image.mode not in ("RGB", "L"):
            pil_image = pil_image.convert("RGB")

        # Get image format
        image_format = pil_image.format or "UNKNOWN"
        if image_format == "UNKNOWN":
            # Try to detect from extension
            ext = path.suffix.lower()
            format_map = {
                ".jpg": "JPEG",
                ".jpeg": "JPEG",
                ".png": "PNG",
                ".gif": "GIF",
                ".bmp": "BMP",
                ".webp": "WebP",
            }
            image_format = format_map.get(ext, "UNKNOWN")
            if image_format == "UNKNOWN":
                raise ImageFormatError(f"Unsupported image format: {ext}")
        
        # Normalize format name (PIL may return "WEBP" but we want "WebP", "JFIF" -> "JPEG")
        format_normalization = {
            "JPEG": "JPEG",
            "JFIF": "JPEG",  # PIL sometimes reports JPEG as JFIF
            "PNG": "PNG",
            "GIF": "GIF",
            "BMP": "BMP",
            "WEBP": "WebP",
            "WebP": "WebP",
        }
        image_format = format_normalization.get(image_format, image_format)

        # Create Image entity
        image = Image(
            width=pil_image.width,
            height=pil_image.height,
            format=image_format,
            source=str(path.absolute()),
            pixel_data=pil_image,
            source_path=str(path.absolute()),
        )

        logger.info(f"Image loaded from file: {file_path}, {pil_image.width}x{pil_image.height}, format={image_format}")
        return image

    except PILImage.UnidentifiedImageError as e:
        logger.error(f"Invalid image format: {file_path}, error: {e}")
        raise ImageFormatError(f"Invalid image format: {file_path}") from e
    except Exception as e:
        logger.error(f"Error loading image from file: {file_path}, error: {e}")
        if isinstance(e, (ImageFormatError, ImageCorruptionError)):
            raise
        raise ValueError(f"Corrupted image data: {file_path}") from e


def load_from_url(url: str, timeout: int = 30) -> Image:
    """Load an image from a web URL.

    Args:
        url: HTTP/HTTPS URL to image
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Image object with loaded pixel data and metadata

    Raises:
        requests.RequestException: Network error or invalid URL
        ValueError: Invalid image format or corrupted data
        TimeoutError: Request timed out
    """
    import requests
    from io import BytesIO

    try:
        logger.info(f"Loading image from URL: {url}")
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        # Check content type
        content_type = response.headers.get("content-type", "").lower()
        if not content_type.startswith("image/"):
            logger.warning(f"URL does not appear to be an image: {content_type}")

        # Load image from response content
        image_data = BytesIO(response.content)
        pil_image = PILImage.open(image_data)

        # Convert to RGB if necessary
        if pil_image.mode not in ("RGB", "L"):
            pil_image = pil_image.convert("RGB")

        # Get image format
        image_format = pil_image.format or "UNKNOWN"
        if image_format == "UNKNOWN":
            # Try to detect from content-type or URL
            if "jpeg" in content_type or "jpg" in content_type:
                image_format = "JPEG"
            elif "png" in content_type:
                image_format = "PNG"
            elif "gif" in content_type:
                image_format = "GIF"
            elif "bmp" in content_type:
                image_format = "BMP"
            elif "webp" in content_type:
                image_format = "WebP"
            else:
                # Try URL extension
                from urllib.parse import urlparse
                parsed = urlparse(url)
                ext = Path(parsed.path).suffix.lower()
                format_map = {
                    ".jpg": "JPEG",
                    ".jpeg": "JPEG",
                    ".png": "PNG",
                    ".gif": "GIF",
                    ".bmp": "BMP",
                    ".webp": "WebP",
                }
                image_format = format_map.get(ext, "UNKNOWN")
                if image_format == "UNKNOWN":
                    raise ImageFormatError(f"Unsupported image format from URL: {url}")
        
        # Normalize format name (PIL may return "WEBP" but we want "WebP", "JFIF" -> "JPEG")
        format_normalization = {
            "JPEG": "JPEG",
            "JFIF": "JPEG",  # PIL sometimes reports JPEG as JFIF
            "PNG": "PNG",
            "GIF": "GIF",
            "BMP": "BMP",
            "WEBP": "WebP",
            "WebP": "WebP",
        }
        image_format = format_normalization.get(image_format, image_format)

        # Create Image entity
        image = Image(
            width=pil_image.width,
            height=pil_image.height,
            format=image_format,
            source=url,
            pixel_data=pil_image,
            source_url=url,
        )

        logger.info(f"Image loaded from URL: {url}, {pil_image.width}x{pil_image.height}, format={image_format}")
        return image

    except requests.Timeout as e:
        logger.error(f"Timeout loading image from URL: {url}")
        raise TimeoutError(f"Request timed out: {url}") from e
    except requests.RequestException as e:
        logger.error(f"Network error loading image from URL: {url}, error: {e}")
        raise
    except PILImage.UnidentifiedImageError as e:
        logger.error(f"Invalid image format from URL: {url}, error: {e}")
        raise ImageFormatError(f"Invalid image format from URL: {url}") from e
    except Exception as e:
        logger.error(f"Error loading image from URL: {url}, error: {e}")
        if isinstance(e, (ImageFormatError, ImageCorruptionError, TimeoutError)):
            raise
        raise ValueError(f"Corrupted image data from URL: {url}") from e

