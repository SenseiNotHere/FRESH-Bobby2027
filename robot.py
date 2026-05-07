import typing
from commands2 import CommandScheduler, Command
from pykit.loggedrobot import LoggedRobot
from pykit.logger import Logger
from pykit.wpilog.wpilogwriter import WPILOGWriter
from pykit.inputs.loggablepowerdistribution import LoggedPowerDistribution

from robot_container import RobotContainer
from constants.constants import RobotConstants

class FRCRobot(LoggedRobot):
    autonomousCommand: typing.Optional[Command] = None
    testCommand: typing.Optional[Command] = None

    # Robot General
    def robotInit(self):
        LoggedPowerDistribution.instance = LoggedPowerDistribution(moduleId=RobotConstants.kPDHCanID)
        Logger.addDataReciever(WPILOGWriter())
        Logger.start()
        self.robot_container = RobotContainer()

    def robotPeriodic(self):
        CommandScheduler.getInstance().run()
        self.robot_container.superstructure.update()
    
    def disabledPeriodic(self):
        self.robot_container.updateAutoPreview()

    # Robot Autonomous
    def autonomousInit(self) -> None:
        self.autonomousCommand = self.robot_container.getAutonomousCommand()
        if self.autonomousCommand:
            self.autonomousCommand.schedule()

    # Robot Teleop
    def teleopInit(self) -> None:
        if self.autonomousCommand:
            self.autonomousCommand.cancel()
        self.robot_container.autonomous_subsystem.clearAutoPreview()

    # Robot Test
    def testInit(self) -> None:
        CommandScheduler.getInstance().cancelAll()
        self.testCommand = self.robot_container.getTestCommand()
        if self.testCommand is not None:
            self.testCommand.schedule()