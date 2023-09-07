from validators import *


def test_coordinates_are_valid():
    assert coordinates_are_valid("55/55") is True
    assert coordinates_are_valid("55|55") is True
    assert coordinates_are_valid("400/-400") is True

    assert coordinates_are_valid("ab/cd") is False
    assert coordinates_are_valid("ab|cd") is False
    assert coordinates_are_valid("55/ab") is False
    assert coordinates_are_valid("555/55") is False
    assert coordinates_are_valid("55/-555") is False
    assert coordinates_are_valid("55/55/55") is False
    assert coordinates_are_valid("///") is False


def test_url_is_valid():
    assert url_is_valid("https://www.example.com") is True
    # Any Discord link will include https
    assert url_is_valid("www.example.com") is False
    # assert url_is_valid("https://www") is False
    assert url_is_valid("not a url") is False


def test_validate_add_input():
    valid_params = ["praxis", "https://www.example.com", "55/55"]
    multi_part_ign = ["Here", "We", "Go", "Again", "https://www.example.com", "55/55"]
    invalid_url_multi_part_ign = ["Here", "We", "Go", "Again", "not a url", "55/55"]
    invalid_url = ["praxis", "not a url", "55/55"]
    invalid_coordinates = ["praxis", "https://www.example.com", "ab/cd"]

    assert validate_add_input(valid_params) is True
    assert validate_add_input(multi_part_ign) is True
    assert validate_add_input(invalid_url) is False
    assert validate_add_input(invalid_coordinates) is False
    assert validate_add_input(invalid_url_multi_part_ign) is False
