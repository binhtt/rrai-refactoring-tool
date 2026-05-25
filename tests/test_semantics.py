from semantics import delta


def test_move():

    state = {}

    result = delta(state, "moveForward")

    assert result["moving"] is True
