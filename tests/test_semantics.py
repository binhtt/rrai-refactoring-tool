from semantics import delta


def test_move_forward():

    state = {}

    result = delta(
        state,
        "moveForward"
    )

    assert result["moving"] is True


def test_emergency_stop():

    state = {
        "moving": True
    }

    result = delta(
        state,
        "emergencyStop"
    )

    assert result["moving"] is False

    assert result["emergency"] is True


def test_turn_left():

    state = {}

    result = delta(
        state,
        "turnLeft"
    )

    assert result["direction"] == "left"
