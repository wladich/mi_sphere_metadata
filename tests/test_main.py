from pathlib import Path
from unittest.mock import patch

import pytest

from mi_sphere_metadata import PoseDegrees, get_angles_degrees, main


@pytest.fixture(name="image_filename")
def fixture_image_filename() -> str:
    return str(Path(__file__).parent / "img.jpg")


@pytest.fixture(name="invalid_image_filename")
def fixture_invalid_image_filename() -> str:
    return str(Path(__file__).parent / "invalid.jpg")


@pytest.mark.parametrize(
    "fmt,output",
    [
        (None, "Yaw: -179.53\nPitch: 6.69\nRoll: 3.66\n"),
        (
            "json",
            '{"yaw": -179.5305064389227, "pitch": 6.693635141483578, '
            '"roll": 3.657116846804307}\n',
        ),
        ("short", "-179.53,6.69,3.66\n"),
    ],
)
def test_formats(
    image_filename: str, capsys: pytest.CaptureFixture[str], fmt: str, output: str
) -> None:
    args = ["", image_filename]
    if fmt is not None:
        args.extend(["--format", fmt])
    with patch("sys.argv", args):
        main()
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == output


def test_cli_invalid_image(invalid_image_filename: str) -> None:
    args = ["", invalid_image_filename]
    with patch("sys.argv", args), pytest.raises(
        SystemExit, match="Mi Sphere rotation matrix not found"
    ):
        main()


def test_get_angles(image_filename: str) -> None:
    expected = PoseDegrees(
        pitch=6.693635141483578, roll=3.657116846804307, yaw=-179.5305064389227
    )
    assert get_angles_degrees(image_filename) == expected


def test_get_angles_from_invalid_image(invalid_image_filename: str) -> None:
    assert get_angles_degrees(invalid_image_filename) is None
