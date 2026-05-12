from typing import Optional, TYPE_CHECKING

from commands2 import Subsystem
from phoenix6.orchestra import Orchestra
from wpilib import SendableChooser, SmartDashboard
from pykit.logger import Logger

from utils import log

if TYPE_CHECKING:
    from subsystems.driving.drive_subsystem import DriveSubsystem
    from subsystems.intaking.intake_subsystem import IntakeSubsystem
    from subsystems.shooting.shooter_subsystem import ShooterSubsystem

_INSTANCE = None

class OrchestraSubsystem(Subsystem):
    def __init__(
        self,
        driveSubsystem: "DriveSubsystem",
        shooterSubsystem: "ShooterSubsystem",
        intakeSubsystem: "IntakeSubsystem",
    ):
        """
        Orchestra Subsystem.

        This subsystem manages music playback on the robot's Kraken motors using the
        Phoenix 6 Orchestra library. It gathers Kraken motors from other subsystems
        and registers them as instruments for the orchestra.

        This subsystem is intended to be a single instance.

        Any subsystem containing Kraken motors can optionally be provided so their
        motors can be included in the orchestra.

        :param driveSubsystem: Drivetrain subsystem containing Kraken motors (optional).
        :param shooterSubsystem: Shooter subsystem containing Kraken motors (optional).
        :param intakeSubsystem: Intake subsystem containing Kraken motors (optional).
        """
        super().__init__()

        if _INSTANCE is not None:
            raise RuntimeError("Only one instance of OrchestraSubsystem is allowed.")
        _INSTANCE = self

        self._orchestra = Orchestra()
        self._current_song: Optional[str] = None
        self._championship_mode = False
        self._championship_song_path = (
            "/home/lvuser/py/deploy/files/WinnerSong.chrp"
        )

        # Register motors
        for subsystem in (driveSubsystem, shooterSubsystem, intakeSubsystem):
            if subsystem is None:
                continue
            for motor in subsystem.getMotors():
                self._orchestra.add_instrument(motor)

        # Song Chooser (kept — Elastic needs this as a NT widget)
        self._song_chooser = SendableChooser()
        self._song_chooser.setDefaultOption(
            "Yes And? - Ariana Grande",
            "/home/lvuser/py/deploy/files/Yesand.chrp"
        )
        self._song_chooser.addOption(
            "Espresso - Sabrina Carpenter",
            "/home/lvuser/py/deploy/files/Espresso.chrp"
        )
        self._song_chooser.addOption(
            "Needy - Ariana Grande",
            "/home/lvuser/py/deploy/files/Needy.chrp"
        )
        self._song_chooser.addOption(
            "Dandelion - Ariana Grande",
            "/home/lvuser/py/deploy/files/Dandelion.chrp"
        )
        self._song_chooser.addOption(
            "When Did You Get Hot - Sabrina Carpenter",
            "/home/lvuser/py/deploy/files/WhenDidYouGetHot.chrp"
        )
        self._song_chooser.addOption(
            "Tití Me Preguntó - Bad Bunny",
            "/home/lvuser/py/deploy/files/TitiMePregunto.chrp"
        )
        self._song_chooser.addOption(
            "Stateside - PinkPantheress",
            "/home/lvuser/py/deploy/files/Stateside.chrp"
        )
        self._song_chooser.addOption(
            "Despacito - Luis Fonsi",
            "/home/lvuser/py/deploy/files/Despacito.chrp"
        )
        SmartDashboard.putData("Song Selection", self._song_chooser)

    def periodic(self):
        Logger.recordOutput("Orchestra/IsPlaying", self._orchestra.is_playing())
        Logger.recordOutput("Orchestra/CurrentSong", self._current_song or "")
        Logger.recordOutput("Orchestra/ChampionshipMode", self._championship_mode)

    # Public API

    def play_selected_song(self):
        path = self._song_chooser.getSelected()

        if path is None:
            return

        if self._current_song != path:
            self._orchestra.load_music(path)
            self._current_song = path

        if not self._orchestra.is_playing():
            self._orchestra.play()

    def play_championship_song(self):
        if not self._championship_mode:
            log("Orchestra", "Championship mode not enabled.")
            return

        path = self._championship_song_path

        if self._current_song != path:
            self._orchestra.load_music(path)
            self._current_song = path

        if not self._orchestra.is_playing():
            self._orchestra.play()

    def stop(self):
        self._orchestra.stop()

    def is_playing(self) -> bool:
        return self._orchestra.is_playing()