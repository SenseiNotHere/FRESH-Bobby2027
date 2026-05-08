import typing
from commands2 import CommandScheduler, Command
from pykit.loggedrobot import LoggedRobot
from pykit.logger import Logger
from pykit.wpilog.wpilogwriter import WPILOGWriter
from pykit.wpilog.wpilogreader import WPILOGReader
from pykit.networktables.nt4Publisher import NT4Publisher

from robot_container import RobotContainer
from constants import RobotModes, RobotConstants

class FRCRobot(LoggedRobot):
    autonomousCommand: typing.Optional[Command] = None
    testCommand: typing.Optional[Command] = None

    def __init__(self):
        super().__init__()
        Logger.recordMetadata("Robot", "FRCRobot")

        match RobotConstants.kRobotMode:
            case RobotModes.REAL:
                Logger.addDataReciever(WPILOGWriter())
                Logger.addDataReciever(NT4Publisher(True))
            case RobotModes.SIM:
                Logger.addDataReciever(NT4Publisher(True))
            case RobotModes.REPLAY:
                Logger.setUseTiming(False)
                # logPath = LogFileUtil.findReplayLog()
                # Logger.setReplaySource(WPILOGReader(logPath))
                # Logger.addDataReciever(WPILOGWriter(logPath + "_sim"))
                pass

        Logger.start()

    # Robot General
    def robotInit(self):
        self.robot_container = RobotContainer()

    def robotPeriodic(self):
        Logger.periodicBeforeUser()
        CommandScheduler.getInstance().run()
        self.robot_container.update()
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