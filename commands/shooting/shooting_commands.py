from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from superstructure.superstructure import Superstructure

from superstructure.robot_state import RobotState


def PrepShot(superstructure: "Superstructure"):
    """
    Spin up shooters. Auto-transitions to SHOOTING once canFeed (at speed + 0.12s).
    Returns to IDLE when command ends.
    Use with whileTrue().
    """
    return superstructure.createStateCommand(RobotState.PREP_SHOT)


def AgitatorReverse(superstructure: "Superstructure"):
    """
    Run agitator in reverse to unjam.
    Returns to IDLE when command ends.
    Use with whileTrue().
    """
    return superstructure.createStateCommand(RobotState.AGITATOR_OPPOSITE)


def PassingFuel(superstructure: "Superstructure"):
    """
    Spin up shooters from dashboard percent and feed once at speed.
    Returns to IDLE when command ends.
    Use with whileTrue().
    """
    return superstructure.createStateCommand(RobotState.PASSING_FUEL)
