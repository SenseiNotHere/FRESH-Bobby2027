from typing import TYPE_CHECKING

from commands2 import InstantCommand, RunCommand, ParallelCommandGroup
from wpilib import XboxController, drive

if TYPE_CHECKING:
    from robot_container import RobotContainer

from commands import (
    DoIntake,
    ReverseIntake,
    DeployIntake,
    StowIntake,
    PrepShot,
    AgitatorReverse,
    PassingFuel,
    PlaySong,
    PlayChampionshipSong,
    ResetXY,
    ResetSwerveFront,
    PointTowardsLocation,
)
from constants import Hub


class ButtonBindings:
    def __init__(self, robot_container: "RobotContainer"):
        self.robot_container = robot_container

    def configureButtonBindings(self):
        self._driverButtonBindings()
        self._operatorButtonBindings()

    def _driverButtonBindings(self):
        robot_container = self.robot_container
        driver_controller = robot_container.driver_controller
        drive_subsystem = robot_container.drive_subsystem
        superstructure = robot_container.superstructure

        # Reset odometry to field starting position
        driver_controller.pov(0).onTrue(ResetXY(0, 0, 0, drive_subsystem, reason="DriverResetXY"))

        # Reset swerve heading (keeps position, re-zeros gyro heading)
        driver_controller.pov(180).onTrue(ResetSwerveFront(drive_subsystem))

        # X-break (lock wheels)
        driver_controller.b().whileTrue(RunCommand(lambda: drive_subsystem.setX(), drive_subsystem))

        # Shoot (spin up + auto-feed when ready)
        driver_controller.rightTrigger(0.5).whileTrue(PrepShot(superstructure))

        # Point toward hub (Right Bumper)
        point_hub = PointTowardsLocation(
            drivetrain=drive_subsystem,
            location=Hub.BLUE_HUB,
            locationIfRed=Hub.RED_HUB
        )
        driver_controller.rightBumper().whileTrue(point_hub)

        # Agitator reverse (unjam)
        driver_controller.y().whileTrue(AgitatorReverse(superstructure))

        # Play song
        driver_controller.back().whileTrue(PlaySong(superstructure))

        # Play championship song
        driver_controller.start().whileTrue(PlayChampionshipSong(superstructure))

    def _operatorButtonBindings(self):
        robot_container = self.robot_container
        operator_controller = robot_container.operator_controller
        superstructure = robot_container.superstructure
        intake_subsystem = robot_container.intake_subsystem

        # Intake rollers (Right Trigger)
        operator_controller.rightTrigger(0.5).whileTrue(DoIntake(superstructure))

        # Reverse intake (Left Trigger)
        operator_controller.leftTrigger(0.5).whileTrue(ReverseIntake(superstructure))

        # Stow intake (Left Bumper)
        operator_controller.leftBumper().whileTrue(StowIntake(superstructure))

        # Deploy intake (Right Bumper)
        operator_controller.rightBumper().whileTrue(DeployIntake(superstructure))
