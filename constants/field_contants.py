from wpimath.geometry import Pose2d, Rotation2d, Pose3d, Rotation3d
from wpimath.units import inchesToMeters
from wpilib import DriverStation
from wpimath.geometry import Translation2d

# Field dimensions (meters)

FIELD_LENGTH = inchesToMeters(651.22)
FIELD_WIDTH = inchesToMeters(317.69)


# Alliance-based pose flipping

def rotateBluePoseIfNecessary(original: Pose2d) -> Pose2d:
    """
    Rotates a blue-alliance pose to red alliance if needed.
    You must implement shouldFlipValueToRed() yourself.
    """
    if shouldFlipValueToRed():
        return rotatePoseAcrossField(original, FIELD_LENGTH, FIELD_WIDTH)
    return original


def shouldFlipValueToRed() -> bool:
    """
    Replace this with DriverStation alliance logic.
    """

    alliance = DriverStation.getAlliance()
    return alliance == DriverStation.Alliance.kRed


def rotatePoseAcrossField(
    pose: Pose2d, field_length: float, field_width: float
) -> Pose2d:
    """
    Mirrors a pose across the field (blue to red).
    """
    return Pose2d(
        field_length - pose.x,
        field_width - pose.y,
        pose.rotation().rotateBy(
            Rotation3d(0.0, 0.0, 3.141592653589793).toRotation2d()
        ),
    )


# Ball constants (simple container)

class BallConstants:
    def __init__(
        self,
        mass_kg: float,
        radius_m: float,
        drag_coeff: float,
        lift_coeff: float,
        magnus_coeff: float,
        spin_decay: float,
        gravity: float,
        max_iter: int,
    ):
        self.mass_kg = mass_kg
        self.radius_m = radius_m
        self.drag_coeff = drag_coeff
        self.lift_coeff = lift_coeff
        self.magnus_coeff = magnus_coeff
        self.spin_decay = spin_decay
        self.gravity = gravity
        self.max_iter = max_iter


BALL_CONSTANTS = BallConstants(
    mass_kg=0.210,                      # 210 grams
    radius_m=inchesToMeters(3.0),       # 3 inch radius
    drag_coeff=1.2,
    lift_coeff=0.30,
    magnus_coeff=1.2,
    spin_decay=0.35,
    gravity=9.81,
    max_iter=20,
)

# Hub locations

class Hub:
    CENTER = Pose3d(
        inchesToMeters(182.11),
        inchesToMeters(158.84),
        inchesToMeters(72.0),
        Rotation3d(),
    )

    BLUE_HUB = Translation2d(4.619, 4.035)
    RED_HUB = Translation2d(11.921, 4.035)

def getHubPose() -> Pose2d:
    alliance = DriverStation.getAlliance()

    if alliance == DriverStation.Alliance.kRed:
        return Pose2d(Hub.RED_HUB, Rotation2d())
    else:
        return Pose2d(Hub.BLUE_HUB, Rotation2d())

class Tower:
    BLUE_TOWER_CLIMB_TOP = Pose2d(1.066, 4.800, Rotation2d.fromDegrees(270))
    RED_TOWER_CLIMB_TOP = Pose2d(15.460, 5.353, Rotation2d.fromDegrees(270))

    BLUE_TOWER_CLIMB_BOTTOM = Pose2d(1.066, 2.720, Rotation2d.fromDegrees(90))
    RED_TOWER_CLIMB_BOTTOM = Pose2d(15.460, 3.273, Rotation2d.fromDegrees(90))

class AprilTags:
    APRIL_TAG_POSITIONS = {
        1: Translation2d(3.6074798, 3.3902756),
        2: Translation2d(3.6449194, 0.6035400),
        3: Translation2d(3.0413646, 0.3557376),
        4: Translation2d(3.0413646, 0.0001376),
        5: Translation2d(3.6449194, -0.6032648),
        6: Translation2d(3.6074798, -3.3900004),
        7: Translation2d(3.6823844, -3.3900004),
        8: Translation2d(4.0005194, -0.6032648),

        9: Translation2d(4.2486774, -0.3554624),
        10: Translation2d(4.2486774, 0.0001376),
        11: Translation2d(4.0005194, 0.6035400),
        12: Translation2d(3.6823844, 3.3902756),
        13: Translation2d(8.2628172, 3.3688126),
        14: Translation2d(8.2628172, 2.9370126),
        15: Translation2d(8.2624616, 0.2890626),
        16: Translation2d(8.2624616, -0.1427374),

        17: Translation2d(-3.6074156, -3.3900004),
        18: Translation2d(-3.6448806, -0.6032648),
        19: Translation2d(-3.0413258, -0.3554624),
        20: Translation2d(-3.0413258, 0.0001376),
        21: Translation2d(-3.6448806, 0.6035400),
        22: Translation2d(-3.6074156, 3.3902756),
        23: Translation2d(-3.6823202, 3.3902756),
        24: Translation2d(-4.0004806, 0.6035400),

        25: Translation2d(-4.2486386, 0.3557376),
        26: Translation2d(-4.2486386, 0.0001376),
        27: Translation2d(-4.0004806, -0.6032648),
        28: Translation2d(-3.6823202, -3.3900004),
        29: Translation2d(-8.2627530, -3.3685374),
        30: Translation2d(-8.2627530, -2.9367374),
        31: Translation2d(-8.2624228, -0.2887874),
        32: Translation2d(-8.2624228, 0.1430126)
    }

class Trench:
    FIELD_TYPE = 'Welded'

    WELDED_BLUE_TRENCH_BOTTOM_CENTER = Pose3d(
        inchesToMeters(182.115),
        inchesToMeters(25.37),
        inchesToMeters(35.00),
        Rotation3d(),
    )

    WELDED_BLUE_TRENCH_TOP_CENTER = Pose3d(
        inchesToMeters(182.115),
        inchesToMeters(292.31),
        inchesToMeters(35.00),
        Rotation3d(),
    )

    WELDED_RED_TRENCH_BOTTOM_CENTER = Pose3d(
        inchesToMeters(469.115),
        inchesToMeters(25.37),
        inchesToMeters(35.00),
        Rotation3d(),
    )

    WELDED_RED_TRENCH_TOP_CENTER = Pose3d(
        inchesToMeters(469.115),
        inchesToMeters(292.31),
        inchesToMeters(35.00),
        Rotation3d(),
    )

    ANDYMARK_BLUE_TRENCH_BOTTOM_CENTER = Pose3d(
        inchesToMeters(181.555),
        inchesToMeters(24.85),
        inchesToMeters(35.00),
        Rotation3d(),
    )

    ANDYMARK_BLUE_TRENCH_TOP_CENTER = Pose3d(
        inchesToMeters(181.555),
        inchesToMeters(291.79),
        inchesToMeters(35.00),
        Rotation3d(),
    )

    ANDYMARK_RED_TRENCH_BOTTOM_CENTER = Pose3d(
        inchesToMeters(468.555),
        inchesToMeters(24.85),
        inchesToMeters(35.00),
        Rotation3d(),
    )

    ANDYMARK_RED_TRENCH_TOP_CENTER = Pose3d(
        inchesToMeters(468.555),
        inchesToMeters(291.79),
        inchesToMeters(35.00),
        Rotation3d(),
    )