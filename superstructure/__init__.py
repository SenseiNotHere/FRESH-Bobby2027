"""Superstructure subsystem for the FRC robot. This subsystem is responsible for coordinating the various subsystems
of the robot to achieve the desired behavior. It contains the state machine for the robot's superstructure."""

from .superstructure import Superstructure
from .superstructure_states import SuperstructureStates
from .superstructure_helpers import SuperstructureHelpers
from .robot_state import RobotState, RobotReadiness, ReadinessList
from .auxiliary_actions import AuxiliaryActions