from __future__ import annotations
import typing
import wpimath.geometry._geometry
import wpimath.units
__all__ = ['angleModulus', 'applyDeadband', 'floorDiv', 'floorMod', 'inputModulus', 'objectToRobotPose', 'slewRateLimit']
def angleModulus(angle: wpimath.units.radians) -> wpimath.units.radians:
    ...
def applyDeadband(value: typing.SupportsFloat, deadband: typing.SupportsFloat, maxMagnitude: typing.SupportsFloat = 1.0) -> float:
    """
    Returns 0.0 if the given value is within the specified range around zero. The
    remaining range between the deadband and the maximum magnitude is scaled from
    0.0 to the maximum magnitude.
    
    :param value:        Value to clip.
    :param deadband:     Range around zero.
    :param maxMagnitude: The maximum magnitude of the input (defaults to 1). Can
                         be infinite.
    
    :returns: The value after the deadband is applied.
    """
def floorDiv(x: typing.SupportsInt, y: typing.SupportsInt) -> int:
    """
    Returns the largest (closest to positive infinity)
    ``int`` value that is less than or equal to the algebraic quotient.
    
    :param x: the dividend
    :param y: the divisor
    
    :returns: the largest (closest to positive infinity)
              ``int`` value that is less than or equal to the algebraic quotient.
    """
def floorMod(x: typing.SupportsInt, y: typing.SupportsInt) -> int:
    """
    Returns the floor modulus of the ``int`` arguments.
    
    The floor modulus is ``r = x - (floorDiv(x, y) * y)``,
    has the same sign as the divisor ``y`` or is zero, and
    is in the range of ``-std::abs(y) < r < +std::abs(y)``.
    
    :param x: the dividend
    :param y: the divisor
    
    :returns: the floor modulus ``x - (floorDiv(x, y) * y)``
    """
def inputModulus(input: typing.SupportsFloat, minimumInput: typing.SupportsFloat, maximumInput: typing.SupportsFloat) -> float:
    """
    Returns modulus of input.
    
    :param input:        Input value to wrap.
    :param minimumInput: The minimum value expected from the input.
    :param maximumInput: The maximum value expected from the input.
    """
def objectToRobotPose(objectInField: wpimath.geometry._geometry.Pose3d, cameraToObject: wpimath.geometry._geometry.Transform3d, robotToCamera: wpimath.geometry._geometry.Transform3d) -> wpimath.geometry._geometry.Pose3d:
    ...
@typing.overload
def slewRateLimit(current: wpimath.geometry._geometry.Translation2d, next: wpimath.geometry._geometry.Translation2d, dt: wpimath.units.seconds, maxVelocity: wpimath.units.meters_per_second) -> wpimath.geometry._geometry.Translation2d:
    """
    Limits translation velocity.
    
    :param current:     Translation at current timestep.
    :param next:        Translation at next timestep.
    :param dt:          Timestep duration.
    :param maxVelocity: Maximum translation velocity.
    
    :returns: Returns the next Translation2d limited to maxVelocity
    """
@typing.overload
def slewRateLimit(current: wpimath.geometry._geometry.Translation3d, next: wpimath.geometry._geometry.Translation3d, dt: wpimath.units.seconds, maxVelocity: wpimath.units.meters_per_second) -> wpimath.geometry._geometry.Translation3d:
    """
    Limits translation velocity.
    
    :param current:     Translation at current timestep.
    :param next:        Translation at next timestep.
    :param dt:          Timestep duration.
    :param maxVelocity: Maximum translation velocity.
    
    :returns: Returns the next Translation3d limited to maxVelocity
    """
