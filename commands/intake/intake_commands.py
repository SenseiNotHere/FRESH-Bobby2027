from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from superstructure.superstructure import Superstructure

from superstructure.robot_state import RobotState


def DoIntake(superstructure: "Superstructure"):
    """
    Deploy the intake and run rollers.
    Stows automatically when the command ends (via IDLE).
    Use with whileTrue().
    """
    return superstructure.createStateCommand(RobotState.INTAKING)


def ReverseIntake(superstructure: "Superstructure"):
    """
    Stow the pivot and run rollers in reverse (eject / unjam).
    Use with whileTrue().
    """
    return superstructure.createStateCommand(RobotState.INTAKE_REVERSE)


def DeployIntake(superstructure: "Superstructure"):
    """
    Deploy the pivot without running rollers.
    """
    return superstructure.createStateCommand(RobotState.INTAKE_DEPLOYED)


def StowIntake(superstructure: "Superstructure"):
    """
    Stows the pivot without running rollers.
    """
    return superstructure.createStateCommand(RobotState.INTAKE_STOWED)
