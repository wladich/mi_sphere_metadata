#!/usr/bin/env python3
import argparse
import json
import math
import struct
import sys
from typing import Literal, NamedTuple, TypeAlias, cast

Matrix: TypeAlias = tuple[float, float, float, float, float, float, float, float, float]


class PoseBase(NamedTuple):
    yaw: float
    pitch: float
    roll: float


class PoseDegrees(PoseBase):
    pass


class PoseRadians(PoseBase):
    pass


def read_matrix_data(filename: str) -> bytes | None:
    with open(filename, "rb") as f:
        buf = f.read(100000)
        tag_start = bytes([0x86, 0x92, 0x07, 0, 0x24, 0, 0, 0])
        tag_pos = buf.find(tag_start)
        if tag_pos == -1:
            return None
        tag_data_offset_position = tag_pos + len(tag_start)
        offset: int
        [offset] = cast(
            tuple[int],
            struct.unpack(
                "<I", buf[tag_data_offset_position : tag_data_offset_position + 4]
            ),
        )
        return buf[offset + 12 : offset + 12 + 36]


def decode_matrix(data: bytes) -> Matrix:
    return cast(Matrix, struct.unpack("f" * 9, data))


def matrix_to_angles(ar: Matrix) -> PoseRadians:
    """Calculates angles in radians
     rz * ry * rx
    ⎡cos(y)⋅cos(z)  sin(x)⋅sin(y)⋅cos(z) - sin(z)⋅cos(x)  sin(x)⋅sin(z) + sin(y)⋅cos(x)⋅cos(z) ⎤
    ⎢                                                                                          ⎥
    ⎢sin(z)⋅cos(y)  sin(x)⋅sin(y)⋅sin(z) + cos(x)⋅cos(z)  -sin(x)⋅cos(z) + sin(y)⋅sin(z)⋅cos(x)⎥
    ⎢                                                                                          ⎥
    ⎣   -sin(y)                sin(x)⋅cos(y)                          cos(x)⋅cos(y)            ⎦
    """
    # pylint: disable=C0103
    r11, _r12, _r13, r21, r22, r23, r31, r32, r33 = ar
    cy = math.sqrt(r11 * r11 + r21 * r21)
    if cy > 1e-6:
        x = math.atan2(r32, r33)
        y = math.atan2(-r31, cy)
        z = math.atan2(r21, r11)
    else:
        x = math.atan2(-r23, r22)
        y = math.atan2(-r31, cy)
        z = 0
    return PoseRadians(z, x, y)


def get_angles_radians(filename: str) -> PoseRadians | None:
    matrix_data = read_matrix_data(filename)
    if matrix_data is None:
        return None
    matrix_values = decode_matrix(matrix_data)
    return matrix_to_angles(matrix_values)


def get_angles_degrees(filename: str) -> PoseDegrees | None:
    angles_radians = get_angles_radians(filename)
    if angles_radians is None:
        return None
    return PoseDegrees(*map(math.degrees, angles_radians))


def show_pose(angles: PoseDegrees, fmt: str | None) -> None:
    if fmt == "json":
        data = {"yaw": angles.yaw, "pitch": angles.pitch, "roll": angles.roll}
        print(json.dumps(data))
    elif fmt == "short":
        print("%.2f,%.2f,%.2f" % (angles.yaw, angles.pitch, angles.roll))
    else:
        print(
            "Yaw: %.2f\nPitch: %.2f\nRoll: %.2f"
            % (angles.yaw, angles.pitch, angles.roll)
        )


def write_sidecar_file(image_filename: str, pose: PoseDegrees) -> None:
    sidecar_filename = image_filename + ".pose.json"
    sidecar_data = {"yaw": pose.yaw, "pitch": pose.pitch, "roll": pose.roll}
    serialized = json.dumps(sidecar_data)
    with open(sidecar_filename, "w", encoding="ascii") as f:
        f.write(serialized)


class Args(argparse.Namespace):
    image: str
    format: Literal["json", "short"] | None
    sidecar: str | Literal[True] | None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Display yaw, pitch, roll angles in degrees, extracted from EXIF"
    )
    parser.add_argument("image", metavar="IMAGE")
    parser.add_argument("--format", "-f", choices=["json", "short"])
    parser.add_argument(
        "--sidecar",
        nargs="?",
        const=True,
        help=(
            "Write pose to sidecar file. "
            "Provide image name to write sidecar with angles from IMAGE"
        ),
    )
    conf = parser.parse_args(namespace=Args())
    angles = get_angles_degrees(conf.image)
    if angles is None:
        sys.exit("Mi Sphere rotation matrix not found in file %s" % conf.image)
    show_pose(angles, fmt=conf.format)
    if conf.sidecar is not None:
        if conf.sidecar is True:
            sidecar_for_file = conf.image
        else:
            sidecar_for_file = conf.sidecar
        write_sidecar_file(sidecar_for_file, angles)


if __name__ == "__main__":
    main()
