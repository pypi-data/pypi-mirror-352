from __future__ import annotations

import pytest

import module_qc_data_tools


def test_serial_number_to_uid():
    assert (
        module_qc_data_tools.utils.chip_serial_number_to_uid("20UPGFC0087209")
        == "0x154a9"
    )


def test_uid_to_serial_number():
    assert (
        module_qc_data_tools.utils.chip_uid_to_serial_number("0x154a9")
        == "20UPGFC0087209"
    )


@pytest.mark.parametrize(
    ("serial_number", "chip_type"),
    [
        ("20UPIM11602031", "RD53B"),
        ("20UPIM12602031", "RD53B"),
        ("20UPIM13602031", "ITKPIXV2"),
        ("20UPIM14602031", "ITKPIXV2"),
        ("20UPIM15602031", "ITKPIXV2"),
    ],
)
def test_chip_type_from_module_serial_number(serial_number, chip_type):
    assert (
        module_qc_data_tools.utils.get_chip_type_from_serial_number(serial_number)
        == chip_type
    )
