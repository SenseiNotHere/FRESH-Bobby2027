from __future__ import annotations

import typing, wpilib
from commands2 import InstantCommand, Command
from commands2.button import CommandGenericHID, CommandXboxController
from wpilib import XboxController, SendableChooser, SmartDashboard
from wpimath.geometry import Rotation2d, Translation3d
from pathplannerlib.auto import AutoBuilder

from pykit.logger import Logger
from pykit.inputs.loggablepowerdistribution import LoggedPowerDistribution

from constants import OIConstants, SwerveConstants, ShooterConstants, AgitatorConstants, IndexerConstants, IntakeConstants
from constants.constants import RobotConstants, RobotModes
from subsystems import *
from commands import HolonomicDrive
from button_bindings import ButtonBindings
from superstructure.superstructure import Superstructure

from utils import log, print_banner

class RobotContainer:
    def __init__(self):
        print_banner("INITIALIZING ROBOT CONTAINER")

        # Controllers
        self.driver_controller = CommandXboxController(OIConstants.kDriverControllerPort)
        self.operator_controller = CommandXboxController(OIConstants.kOperatorControllerPort)

        # Power Distribution (logged)
        self.pdh = LoggedPowerDistribution(RobotConstants.kPDHCanID)

        # Subsystems
        log("RobotContainer", "Initializing subsystems...")
        self.drive_subsystem = DriveSubsystem(lambda: 1.0)
        self.autonomous_subsystem = AutonomousSubsystem(self.drive_subsystem)

        self.intake_subsystem = IntakeSubsystem(
            deployMotorCANID=IntakeConstants.kDeployMotorID,
            deployMotorInverted=IntakeConstants.kDeployMotorInverted,
            rollerMotorCANID=IntakeConstants.kRollerMotorID,
            rollerMotorInverted=IntakeConstants.kRollerMotorInverted
        )

        self.shooter_subsystem = ShooterSubsystem(
            ShooterConstants.kShooterMotorID,
            ShooterConstants.kShooterMotorInverted,
            name="Shooter"
        )

        self.shooter2_subsystem = ShooterSubsystem(
            ShooterConstants.kShooterMotor2ID,
            ShooterConstants.kShooterMotor2Inverted,
            name="Shooter2"
        )

        self.agitator_subsystem = AgitatorSubsystem(
            AgitatorConstants.kAgitatorMotorID,
            AgitatorConstants.kAgitatorMotorInverted
        )

        self.indexer_subsystem = IndexerSubsystem(
            IndexerConstants.kIndexerMotorID,
            IndexerConstants.kIndexerMotorInverted
        )

        self.shot_calculator_subsystem = ShotCalculator(self.drive_subsystem)

        self.front_limelight = LimelightCamera("limelight-front")
        self.back_limelight = LimelightCamera("limelight-back")

        self.localizer = LimelightLocalizer(
            drivetrain=self.drive_subsystem,
            flipIfRed=True
        )
        self.localizer.addCamera(
            camera=self.front_limelight,
            cameraPoseOnRobot=Translation3d(-0.051, -0.241, 0.533),
            cameraHeadingOnRobot=Rotation2d.fromDegrees(180),
            minPercentFrame=0.07,
            maxRotationSpeed=720,
        )
        self.localizer.addCamera(
            camera=self.back_limelight,
            cameraPoseOnRobot=Translation3d(0.305, 0.025, 0.459),
            cameraHeadingOnRobot=Rotation2d.fromDegrees(0),
            minPercentFrame=0.07,
            maxRotationSpeed=720,
        )

        self.orchestra_subsystem = OrchestraSubsystem(
            self.drive_subsystem,
            self.shooter_subsystem,
            self.intake_subsystem
        )

        # Superstructure
        self.superstructure = Superstructure(
            drivetrain=self.drive_subsystem,
            intake=self.intake_subsystem,
            shooter=self.shooter_subsystem,
            shooter2=self.shooter2_subsystem,
            indexer=self.indexer_subsystem,
            agitator=self.agitator_subsystem,
            shotCalculator=self.shot_calculator_subsystem,
            vision=self.front_limelight,
            orchestra=self.orchestra_subsystem,
            driverController=self.driver_controller,
            operatorController=self.operator_controller,
        )

        log("RobotContainer", "Subsystems initialized")
        log("RobotContainer", "Configuring rest of robot...")

        # Button Bindings
        self.buttonBindings = ButtonBindings(self)
        self.buttonBindings.configureButtonBindings()

        # Drive command
        self.drive_subsystem.setDefaultCommand(
            HolonomicDrive(
                drivetrain=self.drive_subsystem,
                forwardSpeed=lambda: -self.driver_controller.getRawAxis(XboxController.Axis.kLeftY),
                leftSpeed=lambda: self.driver_controller.getRawAxis(XboxController.Axis.kLeftX),
                rotationSpeed=lambda: self.driver_controller.getRawAxis(XboxController.Axis.kRightX),
                fieldRelative=True,
                rateLimit=True,
                square=True
            )
        )

        # Auto and Test Choosers
        self.auto_chooser = AutoBuilder.buildAutoChooser()
        SmartDashboard.putData("Auto Chooser", self.auto_chooser)
        self._lastPreviewedAuto = None
        self.test_chooser = SendableChooser()

        log("RobotContainer", "Robot ready for action!")
        print_banner("ROBOT CONTAINER INITIALIZATION COMPLETE")
        log("RobotContainer", "Have fun, drive safe, and make sure to leave the robot better than you found it!")

    def update(self):
        """Called every loop in robotPeriodic. Logs high-level robot state."""
        Logger.recordOutput("Robot/MatchTime", wpilib.Timer.getMatchTime())
        Logger.recordOutput("Robot/BatteryVoltage", wpilib.RobotController.getBatteryVoltage())
        Logger.recordOutput("Robot/RobotMode", RobotConstants.kRobotMode.value)
        Logger.recordOutput("Robot/Enabled", wpilib.DriverStation.isEnabled())
        Logger.recordOutput("Robot/Autonomous", wpilib.DriverStation.isAutonomous())
        Logger.recordOutput("Robot/Teleop", wpilib.DriverStation.isTeleop())
        Logger.recordOutput("Robot/ActiveAuto", str(self._lastPreviewedAuto))

    def updateAutoPreview(self):
        selected = self.auto_chooser.getSelected()
        if selected != self._lastPreviewedAuto:
            self.autonomous_subsystem.drawAuto(selected)
            self._lastPreviewedAuto = selected

    def getAutonomousCommand(self) -> InstantCommand:
        command = self.auto_chooser.getSelected()
        return command if command is not None else InstantCommand()

    def getTestCommand(self) -> InstantCommand:
        command = self.test_chooser.getSelected()
        return command if command is not None else InstantCommand()