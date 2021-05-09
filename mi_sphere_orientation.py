#!/usr/bin/env python3
import argparse
import struct
import math
import binascii
import subprocess
import json


def read_matrix_data(filename):
    res = subprocess.check_output(['exiftool', '-b', '-j', '-UserComment', filename])
    data = json.loads(res)[0]['UserComment']
    prefix = 'base64:'
    assert data.startswith(prefix)
    data = data[len(prefix):]
    data = binascii.a2b_base64(data)
    assert len(data) == 36
    return data


def decode_matrix(data):
    return list(struct.unpack('f' * 9, data))


def matrix_to_angles(ar):
    """Calculates angles in radians"""
    # rz * ry * rx
    # ⎡cos(y)⋅cos(z)  sin(x)⋅sin(y)⋅cos(z) - sin(z)⋅cos(x)  sin(x)⋅sin(z) + sin(y)⋅cos(x)⋅cos(z) ⎤
    # ⎢                                                                                          ⎥
    # ⎢sin(z)⋅cos(y)  sin(x)⋅sin(y)⋅sin(z) + cos(x)⋅cos(z)  -sin(x)⋅cos(z) + sin(y)⋅sin(z)⋅cos(x)⎥
    # ⎢                                                                                          ⎥
    # ⎣   -sin(y)                sin(x)⋅cos(y)                          cos(x)⋅cos(y)            ⎦
    r11, r12, r13, r21, r22, r23, r31, r32, r33 = ar
    cy = math.sqrt(r11 * r11 + r21 * r21)
    if cy > 1e-6:
        x = math.atan2(r32, r33)
        y = math.atan2(-r31, cy)
        z = math.atan2(r21, r11)
    else:
        x = math.atan2(-r23, r22)
        y = math.atan2(-r31, cy)
        z = 0
    return z, x, y


def get_angles_radians(filename):
    matrix_data = read_matrix_data(filename)
    matrix_values = decode_matrix(matrix_data)
    yaw, pitch, roll = matrix_to_angles(matrix_values)
    return yaw, pitch, roll


def get_angles_degrees(filename):
    return list(map(math.degrees, get_angles_radians(filename)))


def show_pose(filename, format):
    yaw, pitch, roll = get_angles_degrees(filename)
    if format == 'json':
        print(json.dumps({'yaw': yaw, 'pitch': pitch, 'roll': roll}))
    elif format == 'short':
        print('%.2f,%.2f,%.2f' % (yaw, pitch, roll))
    else:
        print('Yaw: %.2f\nPitch: %.2f\nRoll: %.2f' % (yaw, pitch, roll))


def main():
    parser = argparse.ArgumentParser(description='Display yaw, pitch, roll angles in degrees, extracted from EXIF')
    parser.add_argument('image', metavar='IMAGE')
    parser.add_argument('--format', '-f', choices=['json', 'short'])
    conf = parser.parse_args()
    show_pose(conf.image, format=conf.format)

if __name__ == '__main__':
    main()
