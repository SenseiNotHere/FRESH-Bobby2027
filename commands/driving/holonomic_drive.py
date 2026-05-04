from __future__ import annotations
from wpimath import applyDeadband
import commands2

class HolonomicDrive(commands2.Command):
    def __init__(self, drivetrain, forwardSpeed, leftSpeed, rotationSpeed, deadband=0.1,
                 fieldRelative=True, rateLimit=True, square=False):
        super().__init__()

        self.forwardSpeed = forwardSpeed if callable(forwardSpeed) else lambda: forwardSpeed
        self.leftSpeed = leftSpeed if callable(leftSpeed) else lambda: leftSpeed
        self.rotationSpeed = rotationSpeed if callable(rotationSpeed) else lambda: rotationSpeed

        assert deadband >= 0, f"deadband={deadband} is not positive"
        self.deadband = deadband

        self.fieldRelative = fieldRelative
        self.rateLimit = rateLimit
        self.square = square

        self.drivetrain = drivetrain
        self.addRequirements(drivetrain)

    def initialize(self):
        pass

    def isFinished(self) -> bool:
        return False

    def execute(self):
        fwd = applyDeadband(self.forwardSpeed(), self.deadband) # type: ignore
        left = applyDeadband(self.leftSpeed(), self.deadband) # type: ignore
        rot = applyDeadband(self.rotationSpeed(), self.deadband) # type: ignore

        self.drivetrain.drive(
            xSpeed=fwd,
            ySpeed=left,
            rot=rot,
            fieldRelative=self.fieldRelative,
            rateLimit=self.rateLimit,
            square=self.square)

    def end(self, interrupted: bool):
        self.drivetrain.stop()