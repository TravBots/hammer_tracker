from utils.validators import *
from bot.test.conftest import build_mock_message


class TestValidators:
    def test_coordinates_are_valid(self):
        assert coordinates_are_valid("55/55")
        assert coordinates_are_valid("55|55")
        assert coordinates_are_valid("50 / 50")
        assert coordinates_are_valid("200/-200")

        assert not coordinates_are_valid("400/-400")
        assert not coordinates_are_valid("200/-201")
        assert not coordinates_are_valid("ab|cd")
        assert not coordinates_are_valid("55/ab")
        assert not coordinates_are_valid("ab/cd")
        assert not coordinates_are_valid("555/55")
        assert not coordinates_are_valid("55/-555")
        assert not coordinates_are_valid("55/55/55")
        assert not coordinates_are_valid("///")

        assert not coordinates_are_valid("−‭44‬‬|‭84")
        assert coordinates_are_valid(preprocess_coordinates("−‭44‬‬|‭84"))

    def test_url_is_valid(self):
        assert url_is_valid("https://www.example.com")
        # Any Discord link will include https
        assert not url_is_valid("www.example.com")
        # assert url_is_valid("https://www") is False
        assert not url_is_valid("not a url")

    def test_is_dev(self):
        MESSAGE_1 = build_mock_message(
            content="!boink keyword some text here", id=177473204011401216
        )
        MESSAGE_2 = build_mock_message(
            content="!tracker keyword some text here", id=322602660555653151
        )
        MESSAGE_3 = build_mock_message(content="!def keyword some text here")
        MESSAGE_3.author.id = 1

        assert is_dev(MESSAGE_1)
        assert is_dev(MESSAGE_2)
        assert not is_dev(MESSAGE_3)
