import pytest
from robot import FRCRobot


@pytest.fixture
def robot():
    return FRCRobot()


def test_teleop(robot):
    with robot.teleop():
        pass


def test_autonomous(robot):
    with robot.autonomous():
        pass


def test_disabled(robot):
    with robot.disabled():
        pass
