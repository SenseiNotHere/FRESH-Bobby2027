from commands2 import FunctionalCommand
from commands2.button import CommandGenericHID
from wpilib import SmartDashboard, Timer, XboxController
from pykit.logger import Logger

from subsystems import (
    DriveSubsystem,
    IntakeSubsystem,
    ShooterSubsystem,
    ShotCalculator,
    IndexerSubsystem,
    AgitatorSubsystem,
    LimelightCamera,
    OrchestraSubsystem,
)

from .robot_state import RobotState, RobotReadiness, ReadinessList
from .auxiliary_actions import AuxiliaryActions
from .superstructure_helpers import SuperstructureHelpers
from .superstructure_states import SuperstructureStates

from utils import log


class Superstructure(SuperstructureStates, SuperstructureHelpers):
    _instance = None

    def __init__(
            self,
            drivetrain: DriveSubsystem | None = None,
            intake: IntakeSubsystem | None = None,
            shooter: ShooterSubsystem | None = None,
            shooter2: ShooterSubsystem | None = None,
            indexer: IndexerSubsystem | None = None,
            agitator: AgitatorSubsystem | None = None,
            shotCalculator: ShotCalculator | None = None,
            vision: LimelightCamera | None = None,
            orchestra: OrchestraSubsystem | None = None,
            driverController: CommandGenericHID | None = None,
            operatorController: CommandGenericHID | None = None,
    ):
        """
        Superstructure.

        The Superstructure is the central coordination layer of the robot. It manages
        high-level robot states and orchestrates interactions between subsystems such
        as the drivetrain, intake, shooter, indexer, and agitator.

        Instead of subsystems directly controlling each other, the Superstructure
        defines robot-wide states (RobotState) and executes the appropriate subsystem
        logic for each state. This keeps subsystem logic isolated while allowing the
        robot to perform coordinated actions such as intaking, preparing a shot, and
        shooting.

        The Superstructure also tracks robot readiness conditions (RobotReadiness)
        which are used to determine when actions such as feeding or shooting are safe.

        :param drivetrain: Drivetrain subsystem.
        :param intake: Intake subsystem (pivot + rollers).
        :param shooter: Primary shooter subsystem.
        :param shooter2: Secondary shooter subsystem.
        :param indexer: Indexer subsystem.
        :param agitator: Agitator subsystem.
        :param shotCalculator: Shot calculation subsystem.
        :param vision: Limelight vision subsystem.
        :param orchestra: Orchestra subsystem for music playback.
        :param driverController: Driver controller.
        :param operatorController: Operator controller.
        """
        if Superstructure._instance is not None:
            raise RuntimeError("Only one instance of Superstructure is allowed.")
        Superstructure._instance = self

        # Subsystems
        self.drivetrain = drivetrain
        self.intake = intake
        self.shooter = shooter
        self.shooter2 = shooter2
        self.indexer = indexer
        self.agitator = agitator
        self.shotCalculator = shotCalculator
        self.vision = vision
        self.orchestra = orchestra
        self.driverController = driverController
        self.operatorController = operatorController

        # Availability flags
        self.hasIntake = self.intake is not None
        self.hasShooter = self.shooter is not None
        self.hasShooter2 = self.shooter2 is not None
        self.hasIndexer = self.indexer is not None
        self.hasAgitator = self.agitator is not None
        self.hasShotCalc = self.shotCalculator is not None
        self.hasVision = self.vision is not None
        self.hasOrchestra = self.orchestra is not None
        self.hasDriverController = self.driverController is not None
        self.hasOperatorController = self.operatorController is not None

        # State tracking
        self.robot_state = RobotState.IDLE
        self.robot_readiness = RobotReadiness()

        # State handlers — called every loop while in the given state
        self._state_handlers = {
            RobotState.IDLE: self._handle_idle,

            # Intake
            RobotState.INTAKING: self._handle_intaking,
            RobotState.INTAKING_AUTONOMOUS: self._handle_intaking,
            RobotState.INTAKE_DEPLOYED: self._handle_intake_deployed,
            RobotState.INTAKE_STOWED: self._handle_intake_stowed,
            RobotState.INTAKE_REVERSE: self._handle_intake_reverse,

            # Shooter
            RobotState.PREP_SHOT: self._handle_prep_shot,
            RobotState.PREP_SHOT_AUTONOMOUS: self._handle_prep_shot,
            RobotState.SHOOTING: self._handle_shooting,
            RobotState.SHOOTING_AUTONOMOUS: self._handle_shooting,

            # Misc
            RobotState.PASSING_FUEL: self._handle_passing_fuel,
            RobotState.AGITATOR_OPPOSITE: self._handle_agitator_reverse,

            # Music
            RobotState.PLAYING_SONG: self._handle_playing_song,
            RobotState.PLAYING_CHAMPIONSHIP_SONG: self._handle_playing_championship_song,
        }

        # Internal timing / debounce
        self._can_feed_since: float | None = None
        self._state_start_time = Timer.getFPGATimestamp()
        self._rumble_end_time: float | None = None

        # Auxiliary actions
        self.auxiliary_actions = AuxiliaryActions(self.driverController)

    def update(self):
        """
        Superstructure update loop. Call from robotPeriodic().
        """
        SmartDashboard.putString("Superstructure/State", self.robot_state.name)
        Logger.recordOutput("Superstructure/State", self.robot_state.name)

        self._update_readiness()

        handler = self._state_handlers.get(self.robot_state)
        if handler:
            handler()

        self._handle_music_cleanup()
        self._handle_rumble_timeout()
        self.auxiliary_actions.update()

    def _update_readiness(self):
        # Shooter readiness
        shooter_ready = False
        if self.hasShooter:
            shooter_ready = self.shooter.atSpeed(tolerance_rpm=50)
        self.robot_readiness.shooterReady = shooter_ready

        # canFeed: shooter at speed + 0.12s debounce
        now = Timer.getFPGATimestamp()
        if shooter_ready:
            if self._can_feed_since is None:
                self._can_feed_since = now
            can_feed = (now - self._can_feed_since) >= 0.12
        else:
            self._can_feed_since = None
            can_feed = False
        self.robot_readiness.canFeed = can_feed

        # Intake deployed readiness
        intake_deployed = False
        if self.hasIntake:
            intake_deployed = self.intake.is_deployed()
        self.robot_readiness.intakeDeployed = intake_deployed

        SmartDashboard.putBoolean("Superstructure/ShooterReady", shooter_ready)
        SmartDashboard.putBoolean("Superstructure/CanFeed", can_feed)
        SmartDashboard.putBoolean("Superstructure/IntakeDeployed", intake_deployed)
        Logger.recordOutput("Superstructure/ShooterReady", shooter_ready)
        Logger.recordOutput("Superstructure/CanFeed", can_feed)
        Logger.recordOutput("Superstructure/IntakeDeployed", intake_deployed)

    def createStateCommand(self, state: RobotState, finishImmediately: bool = False):
        """
        Creates a command that sets the robot to the given state and returns to IDLE when it ends.
        Only transitions to IDLE if this command's state is still active, so it won't stomp a
        state that was changed by another command before this one finished.
        """
        def on_end(interrupted):
            if self.robot_state == state:
                self.setState(RobotState.IDLE)

        return FunctionalCommand(
            onInit=lambda: self.setState(state),
            onExecute=lambda: None,
            onEnd=on_end,
            isFinished=lambda: finishImmediately,
        )

    def autoCreateStateCommand(self, state: RobotState):
        def on_init():
            log("Superstructure", f"AUTO COMMAND TRIGGERED -> {state}")
            self.setState(state)

        return FunctionalCommand(
            onInit=on_init,
            onExecute=lambda: None,
            onEnd=lambda interrupted: None,
            isFinished=lambda: True,
        )

    def setState(self, newState: RobotState, force: bool = False):
        """
        Transitions to a new state.

        :param newState: The new state to transition to.
        :param force: If True, re-enter the state even if it's already active (resets timers).
        """
        if not force and newState == self.robot_state:
            return

        oldState = self.robot_state
        self.robot_state = newState
        self._state_start_time = Timer.getFPGATimestamp()

        log("Superstructure", f"{oldState.name} -> {newState.name}")
        SmartDashboard.putString("Superstructure/State", newState.name)

    def getState(self) -> RobotState:
        return self.robot_state
