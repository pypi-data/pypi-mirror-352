import struct
import sys
from pathlib import Path
from pprint import pprint
from typing import BinaryIO

TAG_LENGTH = 4
WEBP_TAG = b"RIFF"

INT_DATA = 0xFFFFFFFE
KNOWN_TAGS = [
    b"PGD_CO",
    b"PGD_CB",
    b"PGD_CT",
    b"SHFTPROP",
    b"SHFTPPRO",
    b"source",
    b"creator",
    b"PPTY",
    b"PPTX",
    b"image_width_px",
    b"image_height_px",
    b"PGD_RASTER_OSF",
    b"import_time",
    b"lat-0",
    b"lon-0",
    b"lat-1",
    b"lon-1",
    b"lat-2",
    b"lon-2",
    b"lat-3",
    b"lon-3",
    b"PGD_RASTER_USF",
]


def get_tag_at_offset(
    data: bytes, offset: int
) -> tuple[bytes | None, int | str | None, int]:
    for tag in KNOWN_TAGS:
        # Convert the tag to bytes
        tag_len = len(tag)

        # Check if the tag is found at the current offset
        if data[offset : offset + tag_len] == tag:
            # Move offset past the tag
            offset += tag_len

            # Read the number of bytes following the tag
            if offset + TAG_LENGTH > len(data):
                raise ValueError("Unexpected end of file while reading length.")

            data_length = struct.unpack(">I", data[offset : offset + TAG_LENGTH])[0]
            offset += TAG_LENGTH

            if data_length == INT_DATA:
                data_length = 8
                tag_data = data[offset : offset + data_length]
                tag_data = int.from_bytes(tag_data, "big")

            else:
                tag_data = data[offset : offset + data_length]
                tag_data = tag_data.decode("utf-8")

            offset += data_length

            # Read the next `length` bytes for the tag's data
            if offset > len(data):
                print("Unexpected end of file while reading data.")
                print(f"Tag: {tag}")
                break

            return tag, tag_data, offset

    return None, None, offset + 1


def get_metadata(file: BinaryIO) -> list[dict[bytes, int | str]]:
    result = [dict()]
    level = 0

    # TODO avoid reading the whole file into memory
    file.seek(0)
    data = file.read()

    max_offset = data.find(WEBP_TAG) or len(data)
    offset = 0

    while offset < max_offset:
        try:
            tag, tag_data, offset = get_tag_at_offset(data, offset)

        except Exception as e:
            print(f"Error at offset {offset}: {e}")
            tag, tag_data, offset = None, None, offset + 1

        if tag is not None:
            # Convert the data to a readable string and append to results
            if tag == b"PGD_CO" and tag in result[level]:
                level += 1
                result.append(dict())

            result[level][tag] = tag_data

    return result


if __name__ == "__main__":
    file_path = Path(sys.argv[1])

    with open(file_path, "rb") as file:
        parsed_data = get_metadata(file)

        for level, data in enumerate(parsed_data):
            print(f"Level {level}:")
            pprint(data)
            print()
