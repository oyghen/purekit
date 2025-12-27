import purekit as pk


def test_invalid_choice_error():
    x = 0
    choices = [1, 2, 3]
    expected = "invalid choice 0; expected a value from [1, 2, 3]"

    exc = pk.exceptions.InvalidChoiceError(x, choices)
    result = exc.message

    assert result == expected
