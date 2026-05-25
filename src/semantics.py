from typing import Dict


def delta(state: Dict, action: str) -> Dict:

    new_state = state.copy()

    if action == "moveForward":
        new_state["moving"] = True

    elif action == "turnLeft":
        new_state["direction"] = "left"

    elif action == "emergencyStop":
        new_state["moving"] = False
        new_state["emergency"] = True

    elif action == "returnToCharge":
        new_state["charging"] = True

    elif action == "dock":
        new_state["docked"] = True

    elif action == "reroute":
        new_state["rerouting"] = True

    elif action == "reduceSpeed":
        new_state["speed"] = "low"

    elif action == "safeMode":
        new_state["safe"] = True

    elif action == "restartSensor":
        new_state["sensor_restart"] = True

    elif action == "relocalize":
        new_state["localized"] = True

    elif action == "evade":
        new_state["evading"] = True

    elif action == "shutdown":
        new_state["shutdown"] = True

    elif action == "stop":
        new_state["moving"] = False

    elif action == "hazardFlag":
        new_state["hazard"] = True

    return new_state
