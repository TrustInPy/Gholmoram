import io
from hachoir.parser import createParser
from .. import _mime_to_extension


def determine_mime_type(input) -> str | None:
    """
    Args:
        input: 'path' or 'bytes' or 'bytearray' or 'io.BytesIO' of a file
    Returns:
        str: mime type
        None: not detected
    """
    if isinstance(input, str):
        try:
            with open(input, "rb") as file:
                data = file.read(2048)
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


def determine_file_extension(input) -> str | None:
    """
    Args:
        input: 'path' or 'bytes' or 'bytearray' or 'io.BytesIO' of a file
    Returns:
        str: file extension e.g. .pdf .jpg
        None: not detected
    """
    mime_type = determine_mime_type(input)
    return _mime_to_extension.get(mime_type)
