import math
from dataclasses import dataclass
from typing import Dict

from commands2 import Subsystem
from wpilib import SmartDashboard, SendableChooser, DriverStation
from wpimath.geometry import Rotation2d, Translation3d, Pose2d, Translation2d
from pykit.logger import Logger

from .limelight_camera import LimelightCamera
from utils import log


U_TURN = Rotation2d.fromDegrees(180)
LEARNING_RATE = 0.3
TYPICAL_PERCENT_FRAME = 0.7  # when the tag is ~2m away
EMPHASIZE_TAGS_NEARBY = True


@dataclass
class CameraState:
    camera: LimelightCamera
    cameraPoseOnRobot: Translation3d
    cameraHeadingOnRobot: Rotation2d
    cameraPitchAngleDegrees: float
    minPercentFrame: float
    maxRotationSpeed: float


class LimelightLocalizer(Subsystem):
    _instance = None

    def __init__(self, drivetrain, flipIfRed=False):
        super().__init__()

        if LimelightLocalizer._instance is not None:
            raise RuntimeError("Only one instance of LimelightLocalizer is allowed.")
        LimelightLocalizer._instance = self

        assert hasattr(drivetrain, "getHeading"), "drivetrain must have getHeading() for localizer to work"
        assert hasattr(drivetrain, "adjustOdometry"), "drivetrain must have adjustOdometry() for localizer to work"
        assert hasattr(drivetrain, "getPose"), "drivetrain must have getPose() for localizer to work"
        self.drivetrain = drivetrain

        from getpass import getuser
        self.username = getuser()
        self.flipIfRed = flipIfRed

        # Learning rate chooser (kept — Elastic needs this as a NT widget)
        self.learningRateMult = SendableChooser()
        self.learningRateMult.addOption("300%", 3.0)
        self.learningRateMult.addOption("100%", 1.0)
        self.learningRateMult.addOption("50%", 0.5)
        self.learningRateMult.setDefaultOption("30%", 0.3)
        self.learningRateMult.addOption("10%", 0.1)
        self.learningRateMult.addOption("3%", 0.03)
        self.learningRateMult.addOption("1%", 0.01)
        self.learningRateMult.addOption("0.1%", 0.001)
        SmartDashboard.putData("LocaLearnRate", self.learningRateMult)

        self.enabled = None
        self.allowed = True
        self.cameras: Dict[str, CameraState] = dict()

    def addCamera(
        self,
        camera: LimelightCamera,
        cameraPoseOnRobot: Translation3d,
        cameraHeadingOnRobot: Rotation2d,
        cameraPitchAngleDegrees: float = 0.0,
        minPercentFrame: float = 0.07,
        maxRotationSpeed: float = 120,
    ) -> None:
        """
        :param camera: camera to add
        :param cameraPoseOnRobot: is camera x=0.3 meters to the front of the robot center and y=-0.2 meters to right?
        :param cameraHeadingOnRobot: is this camera looking straight forward (Rotation2d.fromDegrees(0)), or maybe right (Rotation2d.fromDegrees(-90)) ?
        :param cameraPitchAngleDegrees: if camera is pitched 10 degrees upwards, set to +10.0, if not pitched then set to 0.0
        :param minPercentFrame: if tags are too small (for example smaller than 0.07% of frame), do not use them
        :param maxRotationSpeed: when robot spins too fast (in degrees per second), camera will be ignored
        """
        assert isinstance(camera, LimelightCamera), "you can only add LimelightCamera(s) to LimelightLocalizer"
        assert camera.cameraName not in self.cameras, f"camera {camera.cameraName} already added to LimelightLocalizer"
        self.cameras[camera.cameraName] = CameraState(
            camera, cameraPoseOnRobot, cameraHeadingOnRobot, cameraPitchAngleDegrees, minPercentFrame, maxRotationSpeed
        )
        camera.addLocalizer()

    def setAllowed(self, value: bool):
        self.allowed = value

    def periodic(self) -> None:
        if len(self.cameras) == 0:
            return

        enabled, flipped = None, False
        if self.enabled is None:
            self.initEnabledChooser()
        if self.enabled is not None:
            enabled, flipped = self.enabled.getSelected()
        if not self.allowed:
            enabled = False

        Logger.recordOutput("Localizer/Enabled", bool(enabled))
        Logger.recordOutput("Localizer/Allowed", self.allowed)
        Logger.recordOutput("Localizer/Flipped", flipped)
        Logger.recordOutput("Localizer/CameraCount", len(self.cameras))
        Logger.recordOutput("Localizer/LearningRate",
            LEARNING_RATE * self.learningRateMult.getSelected())

        if not enabled:
            return

        learningRate: float = LEARNING_RATE * self.learningRateMult.getSelected()
        odometryPos: Pose2d = self.drivetrain.getPose()
        heading: Rotation2d = self.drivetrain.getHeading()
        rotationSpeed: float = self.drivetrain.getTurnRate()
        assert heading is not None

        Logger.recordOutput("Localizer/RotationSpeedDegPerSec", rotationSpeed)

        for c in self.cameras.values():
            camera = c.camera
            camKey = f"Localizer/{camera.cameraName}"

            if not camera.ticked or abs(rotationSpeed) > c.maxRotationSpeed:
                Logger.recordOutput(f"{camKey}/Skipped", True)
                continue

            Logger.recordOutput(f"{camKey}/Skipped", False)

            p = c.cameraPoseOnRobot
            camera.cameraPoseSetRequest.set(
                [p.x, p.y, p.z, c.cameraPitchAngleDegrees, 0.0, c.cameraHeadingOnRobot.degrees()]
            )

            # Limelight4-only (does nothing on Limelight 3)
            camera.imuModeRequest.set(0)
            # 0 - use external imu (the only option available on Limelight 3)
            # 1 - use external imu, seed internal imu
            # 2 - use internal
            # 3 - use internal with MT1 assisted convergence
            # 4 - use internal IMU with external IMU assisted convergence

            if flipped:
                yaw = (heading + U_TURN).degrees()
                camera.robotOrientationSetRequest.set([yaw, 0.0, 0.0, 0.0, 0.0, 0.0])
                botpose = camera.botPoseFlipped.get()
            else:
                yaw = heading.degrees()
                camera.robotOrientationSetRequest.set([yaw, 0.0, 0.0, 0.0, 0.0, 0.0])
                botpose = camera.botPose.get()

            if len(botpose) >= 11:
                # Translation (X,Y,Z), Rotation(Roll,Pitch,Yaw) in degrees,
                # total latency (cl+tl), tag count, tag span, average tag distance from camera,
                # average tag area (percentage of image)
                x, y, z, roll, pitch, yaw, latencyMillisec, count, span, distance, percentage = botpose[0:11]

                Logger.recordOutput(f"{camKey}/TagCount", count)
                Logger.recordOutput(f"{camKey}/TagDistance", distance)
                Logger.recordOutput(f"{camKey}/TagPercentFrame", percentage)
                Logger.recordOutput(f"{camKey}/LatencyMS", latencyMillisec)
                Logger.recordOutput(f"{camKey}/PoseUsed", False)

                if count > 0 and percentage > c.minPercentFrame and not (x == 0 and y == 0):
                    gain = percentage / TYPICAL_PERCENT_FRAME
                    if not EMPHASIZE_TAGS_NEARBY:
                        gain = math.sqrt(gain)
                    shift = Translation2d(x - odometryPos.x, y - odometryPos.y) * min(learningRate * gain, 0.5)
                    self.drivetrain.adjustOdometry(shift, Rotation2d.fromDegrees(0))

                    Logger.recordOutput(f"{camKey}/PoseUsed", True)
                    Logger.recordOutput(f"{camKey}/CorrectionX", shift.x)
                    Logger.recordOutput(f"{camKey}/CorrectionY", shift.y)
                    Logger.recordOutput(f"{camKey}/EstimatedX", x)
                    Logger.recordOutput(f"{camKey}/EstimatedY", y)

    def initEnabledChooser(self):
        flipped = None
        if self.username == "lvuser" and self.flipIfRed is not None:
            # if we are running on RoboRIO, wait until driver station gives us alliance color
            color = DriverStation.getAlliance()
            if color is None:
                return  # we cannot yet decide on whether the field should be flipped
            flipped = (color == DriverStation.Alliance.kRed) and self.flipIfRed
            log("Localizer", "color={}, flipped={}".format(color, flipped))
        log("Localizer", "Localizer will assume flipped={} (username={}, flipIfRed={})".format(
            flipped, self.username, self.flipIfRed))

        # Enabled chooser (kept — Elastic needs this as a NT widget)
        self.enabled = SendableChooser()
        self.enabled.addOption("off", (None, False))
        if flipped in (None, False):
            self.enabled.setDefaultOption("on", (True, False))
        if flipped in (None, True):
            self.enabled.setDefaultOption("on-flipped", (True, True))
        SmartDashboard.putData("Localizer", self.enabled)