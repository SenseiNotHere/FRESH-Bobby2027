from typing import TYPE_CHECKING

from .robot_state import RobotState

if TYPE_CHECKING:
    from .superstructure import Superstructure


class SuperstructureStates:

    def _handle_idle(self: "Superstructure"):
        # Velocity mechanisms: stop immediately
        self._stop_shooter()
        self._stop_indexer()
        self._stop_agitator()
        self._stop_orchestra()
        self._stop_intake_rollers()
        # Position mechanism: command to stow (keeps PID running until target is reached,
        # then holds — never calls stop() which would kill the controller mid-move)
        self._stow_intake_pivot()

    def _handle_intaking(self: "Superstructure"):
        self._deploy_intake_pivot()
        self._start_intake_rollers()

    def _handle_intake_reverse(self: "Superstructure"):
        self._stow_intake_pivot()
        self._reverse_intake_rollers()

    def _handle_intake_deployed(self: "Superstructure"):
        self._deploy_intake_pivot()
        self._stop_intake_rollers()

    def _handle_intake_stowed(self: "Superstructure"):
        self._stow_intake_pivot()
        self._stop_intake_rollers()

    def _handle_prep_shot(self: "Superstructure"):
        self._spin_up_shooters()
        self._stop_feeders()
        if self.robot_readiness.canFeed:
            self.setState(RobotState.SHOOTING)

    def _handle_shooting(self: "Superstructure"):
        self._spin_up_shooters()
        self._pulse_intake()
        if self.robot_readiness.canFeed:
            self._feed_shooters()
        else:
            self._stop_feeders()

    def _handle_passing_fuel(self: "Superstructure"):
        self._spin_up_shooters_dashboard()
        if self.robot_readiness.shooterReady:
            self._feed_shooters()
        else:
            self._stop_feeders()

    def _handle_agitator_reverse(self: "Superstructure"):
        if self.hasAgitator:
            self.agitator.reverse()

    def _handle_playing_song(self: "Superstructure"):
        if self.hasOrchestra:
            self.orchestra.play_selected_song()

    def _handle_playing_championship_song(self: "Superstructure"):
        if self.hasOrchestra:
            self.orchestra.play_championship_song()
