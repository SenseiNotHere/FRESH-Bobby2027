from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from superstructure.superstructure import Superstructure

from superstructure.robot_state import RobotState


def PlaySong(superstructure: "Superstructure"):
    """
    Play the selected song via orchestra.
    Returns to IDLE when command ends.
    Use with whileTrue().
    """
    return superstructure.createStateCommand(RobotState.PLAYING_SONG)


def PlayChampionshipSong(superstructure: "Superstructure"):
    """
    Play the championship song via orchestra.
    Returns to IDLE when command ends.
    Use with whileTrue().
    """
    return superstructure.createStateCommand(RobotState.PLAYING_CHAMPIONSHIP_SONG)
