from validators import *


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
