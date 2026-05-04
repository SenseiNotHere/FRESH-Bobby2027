from typing import TYPE_CHECKING

from commands2 import InstantCommand, RunCommand
from wpilib import XboxController

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
)


class ButtonBindings:
    def __init__(self, robot_container: "RobotContainer"):
        self.robot_container = robot_container

    def configureButtonBindings(self):
        self._driverButtonBindings()
        self._operatorButtonBindings()

    def _driverButtonBindings(self):
        rc = self.robot_container
        driver = rc.driver_controller
        drive = rc.drive_subsystem
        ss = rc.superstructure

        # Reset odometry to field starting position
        driver.pov(0).onTrue(ResetXY(0, 0, 0, drive, reason="DriverResetXY"))

        # Reset swerve heading (keeps position, re-zeros gyro heading)
        driver.pov(180).onTrue(ResetSwerveFront(drive))

        # X-break (lock wheels)
        driver.b().whileTrue(RunCommand(lambda: drive.setX(), drive))

        # Shoot (spin up + auto-feed when ready)
        driver.rightTrigger(0.5).whileTrue(PrepShot(ss))

        # Passing shot
        driver.leftTrigger(0.5).whileTrue(PassingFuel(ss))

        # Agitator reverse (unjam)
        driver.y().whileTrue(AgitatorReverse(ss))

        # Play song
        driver.back().whileTrue(PlaySong(ss))

        # Play championship song
        driver.start().whileTrue(PlayChampionshipSong(ss))

    def _operatorButtonBindings(self):
        rc = self.robot_container
        operator = rc.operator_controller
        ss = rc.superstructure

        # Intake rollers
        operator.rightTrigger(0.5).whileTrue(DoIntake(ss))

        # Reverse intake (unjam)
        operator.leftTrigger(0.5).whileTrue(ReverseIntake(ss))

        # Stow intake
        operator.leftBumper().onTrue(StowIntake(ss))

        # Deploy intake (hold position without running rollers)
        operator.rightBumper().whileTrue(DeployIntake(ss))
