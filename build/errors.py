"""
Single exception type used across the build.

Single responsibility: define BuildError. Every loader/validator in build/
raises this, naming the offending file and key/field, so build.py can catch
one exception type and exit loudly with a clear message. No other exception
handling happens anywhere in the build -- this is the only escape hatch.
"""


class BuildError(Exception):
    """Raised when the build cannot proceed because of invalid or missing input."""
