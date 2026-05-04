from typing import TYPE_CHECKING
from wpilib import Timer, XboxController
from commands2.button import CommandGenericHID

from .robot_state import RobotState

if TYPE_CHECKING:
    from .superstructure import Superstructure


class SuperstructureHelpers:

    #  Intake 

    def _stow_intake_pivot(self: "Superstructure"):
        """Send pivot to stow via position controller. Safe to call every loop, never kills the PID."""
        if self.hasIntake and self.intake.is_homed():
            self.intake.stow()

    def _deploy_intake_pivot(self: "Superstructure"):
        if self.hasIntake:
            self.intake.deploy()

    def _start_intake_rollers(self: "Superstructure"):
        if self.hasIntake:
            self.intake.intake()

    def _stop_intake_rollers(self: "Superstructure"):
        if self.hasIntake:
            self.intake.stop_intake()

    def _reverse_intake_rollers(self: "Superstructure"):
        if self.hasIntake:
            self.intake.intake_reverse()

    def _pulse_intake(self: "Superstructure"):
        """Oscillate pivot between pulse and deploy position with rollers, tied to state start time."""
        if not self.hasIntake:
            return
        t = Timer.getFPGATimestamp() - self._state_start_time
        if (t % 3.0) > 1.5:
            self.intake.go_to_pulse_position()
            self.intake.intake()
        else:
            self.intake.deploy()
            self.intake.stop_intake()

    #  Shooter 

    def _stop_shooter(self: "Superstructure"):
        if self.hasShooter:
            self.shooter.stop()
        if self.hasShooter2:
            self.shooter2.stop()

    def _spin_up_shooters(self: "Superstructure"):
        target_rps = None
        if self.hasShotCalc:
            target_rps = self.shotCalculator.getTargetSpeedRPS()

        if self.hasShooter:
            if target_rps is not None:
                self.shooter.setTargetRPS(target_rps)
            else:
                self.shooter.useDashboardPercent()

        if self.hasShooter2:
            if target_rps is not None:
                self.shooter2.setTargetRPS(target_rps)
            else:
                self.shooter2.useDashboardPercent()

    def _spin_up_shooters_dashboard(self: "Superstructure"):
        if self.hasShooter:
            self.shooter.useDashboardPercent()
        if self.hasShooter2:
            self.shooter2.useDashboardPercent()

    #  Feeders 

    def _feed_shooters(self: "Superstructure"):
        if self.hasIndexer:
            self.indexer.feed()
        if self.hasAgitator:
            self.agitator.feed()

    def _stop_feeders(self: "Superstructure"):
        if self.hasIndexer:
            self.indexer.stop()
        if self.hasAgitator:
            self.agitator.stop()

    #  Indexer / Agitator 

    def _stop_indexer(self: "Superstructure"):
        if self.hasIndexer:
            self.indexer.stop()

    def _stop_agitator(self: "Superstructure"):
        if self.hasAgitator:
            self.agitator.stop()

    #  Orchestra 

    def _stop_orchestra(self: "Superstructure"):
        if self.hasOrchestra:
            self.orchestra.stop()

    def _handle_music_cleanup(self: "Superstructure"):
        if self.robot_state != RobotState.PLAYING_SONG and self.hasOrchestra:
            self.orchestra.stop()

    #  Controller Rumble 

    @staticmethod
    def _rumble_controller(
            controller: CommandGenericHID | None,
            rumble_type: XboxController.RumbleType,
            rumble_value: float,
    ):
        if controller is None:
            return
        controller.getHID().setRumble(rumble_type, rumble_value)

    def _handle_rumble_timeout(self: "Superstructure"):
        if not self._rumble_end_time:
            return
        if Timer.getFPGATimestamp() >= self._rumble_end_time:
            if self.hasDriverController:
                self._rumble_controller(
                    self.driverController,
                    XboxController.RumbleType.kBothRumble,
                    0.0,
                )
            self._rumble_end_time = None
