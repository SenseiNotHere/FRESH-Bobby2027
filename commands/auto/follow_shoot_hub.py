from commands2 import ParallelCommandGroup
from commands.driving.point_torwards_location import PointTowardsLocation
from superstructure import RobotState
from superstructure import Superstructure
from subsystems import DriveSubsystem
from constants import Hub


class FollowShootHub(ParallelCommandGroup):

    def __init__(
        self,
        superstructure: Superstructure,
        drivetrain: DriveSubsystem,
    ):

        point_cmd = PointTowardsLocation(
            drivetrain=drivetrain,
            location=Hub.BLUE_HUB,
            locationIfRed=Hub.RED_HUB
        )
        state_cmd = superstructure.createStateCommand(RobotState.PREP_SHOT)

        super().__init__(point_cmd, state_cmd)

        self.superstructure = superstructure
        self.drivetrain = drivetrain
