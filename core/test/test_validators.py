from validators import *

from mocks import *


def test_coordinates_are_valid():
    assert coordinates_are_valid("55/55")
    assert coordinates_are_valid("55|55")
    assert coordinates_are_valid("400/-400")

    assert not coordinates_are_valid("ab|cd")
    assert not coordinates_are_valid("55/ab")
    assert not coordinates_are_valid("ab/cd")
    assert not coordinates_are_valid("555/55")
    assert not coordinates_are_valid("55/-555")
    assert not coordinates_are_valid("55/55/55")
    assert not coordinates_are_valid("///")


def test_url_is_valid():
    assert url_is_valid("https://www.example.com")
    # Any Discord link will include https
    assert not url_is_valid("www.example.com")
    # assert url_is_valid("https://www") is False
    assert not url_is_valid("not a url")


def test_validate_add_input():
    valid_params = ["praxis", "https://www.example.com", "55/55"]
    multi_part_ign = ["Here", "We", "Go", "Again", "https://www.example.com", "55/55"]
    invalid_url_multi_part_ign = ["Here", "We", "Go", "Again", "not a url", "55/55"]
    invalid_url = ["praxis", "not a url", "55/55"]
    invalid_coordinates = ["praxis", "https://www.example.com", "ab/cd"]

    assert validate_add_input(valid_params)
    assert validate_add_input(multi_part_ign)
    assert not validate_add_input(invalid_url)
    assert not validate_add_input(invalid_coordinates)
    assert not validate_add_input(invalid_url_multi_part_ign)


def test_is_dev():
    MESSAGE_1 = MockMessage(
        content="!boink keyword some text here", id=177473204011401216
    )
    MESSAGE_2 = MockMessage(
        content="!tracker keyword some text here", id=322602660555653151
    )
    MESSAGE_3 = MockMessage(content="!def keyword some text here")

    assert is_dev(MESSAGE_1)
    assert is_dev(MESSAGE_2)
    assert not is_dev(MESSAGE_3)
