from commands2 import Subsystem
from wpilib import SmartDashboard, DriverStation, Timer, SendableChooser
from pykit.logger import Logger

from phoenix6.hardware import TalonFX
from phoenix6.controls import VelocityTorqueCurrentFOC
from phoenix6.configs import TalonFXConfiguration, Slot0Configs, CurrentLimitsConfigs
from phoenix6.signals import NeutralModeValue, InvertedValue

from rev import (
    SparkMax,
    SparkMaxConfig,
    SparkBaseConfig,
    SparkBase,
    LimitSwitchConfig,
    ClosedLoopSlot,
    PersistMode,
    ResetMode,
    FeedbackSensor
)

from constants import IntakeConstants


class IntakeSubsystem(Subsystem):
    def __init__(
            self,
            deployMotorCANID: int,
            deployMotorInverted: bool,
            rollerMotorCANID: int,
            rollerMotorInverted: bool
    ):
        """
        Intake Subsystem.
 
        Composes IntakePivot and IntakeRollers into a single Commands2 Subsystem.
 
        Hardware:
        - Spark MAX (IntakePivot): Controls the deploy position using built-in limit switches.
        - TalonFX / Kraken X60 (IntakeRollers): Drives the intake roller.
 
        :param deployMotorCANID: CAN ID of the Spark MAX controlling the deploy mechanism.
        :param deployMotorInverted: Whether the deploy motor (Spark MAX) is inverted.
        :param intakeMotorCANID: CAN ID of the TalonFX controlling the intake roller.
        :param intakeMotorInverted: Whether the intake roller motor (TalonFX) is inverted.
        """
        super().__init__()
 
        self.pivot = IntakePivot(deployMotorCANID, deployMotorInverted)
        self.rollers = IntakeRollers(rollerMotorCANID, rollerMotorInverted)
 
    # Periodic
 
    def periodic(self):
        self.pivot.update()
        self.rollers.update()
 
    # Pivot passthrough
 
    def forward_limit_pressed(self) -> bool:
        return self.pivot.forward_limit_pressed()
 
    def reverse_limit_pressed(self) -> bool:
        return self.pivot.reverse_limit_pressed()
 
    def driveDeployMotor(self, speed: float):
        self.pivot.drive(speed)
 
    def stopDeployMotor(self):
        self.pivot.stop()
 
    def deploy(self):
        self.pivot.deploy()
 
    def stow(self):
        self.pivot.stow()
 
    def go_to_pulse_position(self):
        self.pivot.go_to_pulse_position()
 
    def toggle_position(self):
        self.pivot.toggle_position()
 
    def stop_deploy(self):
        self.pivot.stop()
 
    def is_homed(self) -> bool:
        return self.pivot.is_homed()

    def is_deployed(self) -> bool:
        return self.pivot.is_deployed()

    def is_at_stow(self, tolerance: float = 1.0) -> bool:
        return self.pivot.is_at_stow(tolerance)

    def is_at_deploy(self, tolerance: float = 1.0) -> bool:
        return self.pivot.is_at_deploy(tolerance)
 
    # Rollers passthrough
 
    def intake(self):
        self.rollers.intake()
 
    def intake_reverse(self):
        self.rollers.intake_reverse()
 
    def stop_intake(self):
        self.rollers.stop()
 
    def stop(self):
        self.rollers.stop()
        self.pivot.stop()
 
    def getMotors(self):
        yield self.rollers.getMotor()

class IntakeRollers:
    def __init__(self, rollerMotorCANID: int, rollerMotorInverted: bool):
        """
        Controls the intake roller using a TalonFX (Kraken X60) motor.
 
        :param rollerMotorCANID: CAN ID of the TalonFX controlling the intake roller.
        :param rollerMotorInverted: Whether the intake roller motor (TalonFX) is inverted.
        """
        self.intakeMotor = TalonFX(rollerMotorCANID)
 
        intakeConfig = TalonFXConfiguration()
        intakeConfig.motor_output.neutral_mode = NeutralModeValue.COAST
        intakeConfig.motor_output.inverted = (
            InvertedValue.CLOCKWISE_POSITIVE
            if rollerMotorInverted
            else InvertedValue.COUNTER_CLOCKWISE_POSITIVE
        )
        self.intakeMotor.configurator.apply(intakeConfig)
 
        slot0Intake = Slot0Configs()
        (
            slot0Intake
            .with_k_p(IntakeConstants.kIntakeP)
            .with_k_i(IntakeConstants.kIntakeI)
            .with_k_d(IntakeConstants.kIntakeD)
            .with_k_v(IntakeConstants.kIntakeFF)
        )
        self.intakeMotor.configurator.apply(slot0Intake)
 
        currentConfig = CurrentLimitsConfigs()
        (
            currentConfig
            .with_supply_current_limit(20)
            .with_stator_current_limit(20)
            .with_supply_current_limit_enable(True)
            .with_stator_current_limit_enable(True)
        )
        self.intakeMotor.configurator.apply(currentConfig)
 
        self.intakeRequest = VelocityTorqueCurrentFOC(0)
        self.velocity = 0
 
        # Speed Chooser (percent of kIntakeSpeed)
        self.speedChooser = SendableChooser()
        self.speedChooser.addOption("5%", 5)
        self.speedChooser.addOption("1%", 1)
        self.speedChooser.addOption("10%", 10)
        self.speedChooser.addOption("15%", 15)
        self.speedChooser.addOption("20%", 20)
        self.speedChooser.addOption("25%", 25)
        self.speedChooser.addOption("30%", 30)
        self.speedChooser.addOption("35%", 35)
        self.speedChooser.addOption("40%", 40)
        self.speedChooser.addOption("45%", 45)
        self.speedChooser.addOption("50%", 50)
        self.speedChooser.addOption("55%", 55)
        self.speedChooser.addOption("60%", 60)
        self.speedChooser.addOption("65%", 65)
        self.speedChooser.setDefaultOption("70%", 70)
        self.speedChooser.addOption("75%", 75)
        self.speedChooser.addOption("80%", 80)
        self.speedChooser.addOption("85%", 85)
        self.speedChooser.addOption("90%", 90)
        self.speedChooser.addOption("95%", 95)
        self.speedChooser.addOption("100%", 100)
        SmartDashboard.putData("Intake Speed", self.speedChooser)
 
    def update(self):
        """
        Called every loop. Publishes roller telemetry to SmartDashboard.
        Must be called from IntakeSubsystem.periodic().
        """
        actual_speed = self.intakeMotor.get_velocity().value
        supply_current = self.intakeMotor.get_supply_current().value
        SmartDashboard.putNumber("Intake/Intake Actual Speed", actual_speed)
        SmartDashboard.putNumber("Intake/Intake Motor Supply Current", supply_current)
        Logger.recordOutput("Intake/Rollers/ActualSpeed", actual_speed)
        Logger.recordOutput("Intake/Rollers/SupplyCurrent", supply_current)
 
    # Roller Control
 
    def intake(self):
        self.velocity = self.speedChooser.getSelected()
        self.intakeMotor.set_control(self.intakeRequest.with_velocity(self.velocity))
        SmartDashboard.putNumber("Intake/Intake Velocity", self.velocity)
 
    def intake_reverse(self):
        self.intakeMotor.set_control(
            self.intakeRequest.with_velocity(-IntakeConstants.kIntakeSpeed)
        )
 
    def stop(self):
        self.intakeMotor.set_control(self.intakeRequest.with_velocity(0))
        SmartDashboard.putNumber("Intake/Intake Velocity", 0)
 
    def getMotor(self):
        return self.intakeMotor
 
class IntakePivot:
    def __init__(self, deployMotorCANID: int, deployMotorInverted: bool):
        """
        Controls the intake deploy mechanism using a Spark MAX motor with built-in limit switches.
 
        :param deployMotorCANID: CAN ID of the Spark MAX controlling the intake deploy mechanism.
        :param deployMotorInverted: Whether the deploy motor (Spark MAX) is inverted.
        """
        self.deployMotor = SparkMax(deployMotorCANID, SparkMax.MotorType.kBrushless)
 
        deployConfig = SparkMaxConfig()
        deployConfig.setIdleMode(SparkBaseConfig.IdleMode.kBrake)
        deployConfig.inverted(deployMotorInverted)
 
        deployConfig.limitSwitch.forwardLimitSwitchEnabled(True)
        deployConfig.limitSwitch.reverseLimitSwitchEnabled(True)
        deployConfig.limitSwitch.forwardLimitSwitchType(LimitSwitchConfig.Type.kNormallyOpen)
        deployConfig.limitSwitch.reverseLimitSwitchType(LimitSwitchConfig.Type.kNormallyOpen)
 
        deployConfig.closedLoop.pid(
            IntakeConstants.kDeployP,
            IntakeConstants.kDeployI,
            IntakeConstants.kDeployD,
        )
        deployConfig.closedLoop.outputRange(
            IntakeConstants.kDeployMinOutput,
            IntakeConstants.kDeployMaxOutput,
            ClosedLoopSlot.kSlot0
        )
        deployConfig.closedLoop.setFeedbackSensor(FeedbackSensor.kPrimaryEncoder)
 
        self.deployMotor.configure(
            deployConfig,
            ResetMode.kResetSafeParameters,
            PersistMode.kPersistParameters
        )
        self.deployMotor.clearFaults()
 
        self.deployEncoder = self.deployMotor.getEncoder()
        self.deployController = self.deployMotor.getClosedLoopController()
 
        self.forwardLimit = self.deployMotor.getForwardLimitSwitch()
        self.reverseLimit = self.deployMotor.getReverseLimitSwitch()
 
        self._homed = False
        self._isDeployed = False
        self._setpoint = IntakeConstants.kStowPosition
 
    # Limit Switch Helpers
 
    def forward_limit_pressed(self) -> bool:
        return self.forwardLimit.get()
 
    def reverse_limit_pressed(self) -> bool:
        return self.reverseLimit.get()
 
    # Encoder Sync
 
    def _sync_encoders(self, target_position: float):
        self.deployEncoder.setPosition(target_position)
 
    def _sync_to_stow(self):
        if not self._homed:
            self._sync_encoders(IntakeConstants.kStowPosition)
        self._homed = True
        self._isDeployed = False
 
    # Homing
 
    def _run_homing(self):
        self.deployMotor.set(-IntakeConstants.kHomeSpeed)
 
    def update(self):
        """
        Called every loop. Handles homing logic and limit switch syncing.
        Must be called from IntakeSubsystem.periodic().
        """
        position = self.deployEncoder.getPosition()
        current = self.deployMotor.getOutputCurrent()
        fwd_limit = self.forward_limit_pressed()
        rev_limit = self.reverse_limit_pressed()
        SmartDashboard.putBoolean("Intake/Intake Homed", self._homed)
        SmartDashboard.putBoolean("Intake/Intake Deployed", self._isDeployed)
        SmartDashboard.putBoolean("Intake/Forward Limit", fwd_limit)
        SmartDashboard.putBoolean("Intake/Reverse Limit", rev_limit)
        SmartDashboard.putNumber("Pivot Motor/Pivot Motor Position", position)
        SmartDashboard.putNumber("Pivot Motor/Current", current)
        Logger.recordOutput("Intake/Pivot/Homed", self._homed)
        Logger.recordOutput("Intake/Pivot/Deployed", self._isDeployed)
        Logger.recordOutput("Intake/Pivot/ForwardLimit", fwd_limit)
        Logger.recordOutput("Intake/Pivot/ReverseLimit", rev_limit)
        Logger.recordOutput("Intake/Pivot/Position", position)
        Logger.recordOutput("Intake/Pivot/Setpoint", self._setpoint)
        Logger.recordOutput("Intake/Pivot/Current", current)
 
        if self.reverse_limit_pressed():
            self._sync_to_stow()
            return
 
        if not self._homed:
            self._run_homing()
            return
 
    # Deploy Control
 
    def drive(self, speed: float):
        self.deployMotor.set(speed)
 
    def stop(self):
        self.deployMotor.set(0)
 
    def deploy(self):
        if not self._homed:
            return
        self._setpoint = IntakeConstants.kDeployPosition
        self.deployController.setReference(
            IntakeConstants.kDeployPosition,
            SparkBase.ControlType.kPosition,
            ClosedLoopSlot.kSlot0
        )
        self._isDeployed = True

    def stow(self):
        if not self._homed:
            return
        self._setpoint = IntakeConstants.kStowPosition
        self.deployController.setReference(
            IntakeConstants.kStowPosition,
            SparkBase.ControlType.kPosition,
            ClosedLoopSlot.kSlot0
        )
        self._isDeployed = False

    def go_to_pulse_position(self):
        if not self._homed:
            return
        self._setpoint = IntakeConstants.kPulsePosition
        self.deployController.setReference(
            IntakeConstants.kPulsePosition,
            SparkBase.ControlType.kPosition,
            ClosedLoopSlot.kSlot0
        )
        self._isDeployed = False

    def at_position(self, target: float, tolerance: float = 1.0) -> bool:
        return abs(self.deployEncoder.getPosition() - target) <= tolerance

    def is_at_stow(self, tolerance: float = 1.0) -> bool:
        return self.at_position(IntakeConstants.kStowPosition, tolerance)

    def is_at_deploy(self, tolerance: float = 1.0) -> bool:
        return self.at_position(IntakeConstants.kDeployPosition, tolerance)

    def toggle_position(self):
        if self._isDeployed:
            self.stow()
        else:
            self.deploy()
 
    # State
 
    def is_homed(self) -> bool:
        return self._homed
 
    def is_deployed(self) -> bool:
        return self._isDeployed