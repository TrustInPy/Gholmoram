import aiofiles
import io
from hachoir.parser import createParser


async def determine_mime_type(input) -> str | None:
    """
    input: 'path' or 'bytes' or 'bytearray' or 'io.BytesIO' of a file
    """
    if isinstance(input, str):
        try:
            async with aiofiles.open(input, "rb") as file:
                data = await file.read(2048)
            input = io.BytesIO(data)
        except:
            return None

    if isinstance(input, (bytes, bytearray)):
        try:
            input = io.BytesIO(input)
        except:
            return None

    if isinstance(input, io.BytesIO):
        try:
            parser = createParser(input)
            if not parser:
                return None
            return parser.mime_type
        except:
            return None

    return None


async def determine_file_extension(input) -> str | None:
    """
    input: 'path' or 'bytes' or 'bytearray' or 'io.BytesIO' of a file
    """
    mime_type = await determine_mime_type(input)
    return _mime_to_extension.get(mime_type)


_mime_to_extension = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
    "image/tiff": ".tiff",
    "image/webp": ".webp",
    "text/plain": ".txt",
    "text/html": ".html",
    "text/css": ".css",
    "text/javascript": ".js",
    "application/pdf": ".pdf",
    "application/zip": ".zip",
    "application/x-tar": ".tar",
    "application/x-gzip": ".gz",
    "application/x-rar-compressed": ".rar",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.ms-powerpoint": ".ppt",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/vnd.word": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/json": ".json",
    "application/xml": ".xml",
    "video/mp4": ".mp4",
    "video/x-msvideo": ".avi",
    "video/x-matroska": ".mkv",
    "video/quicktime": ".mov",
    "video/x-flv": ".flv",
    "video/x-ms-wmv": ".wmv",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/ogg": ".ogg",
    "audio/x-flac": ".flac",
    "audio/x-ms-wma": ".wma",
    "audio/aac": ".aac",
    "application/octet-stream": ".bin",
}
