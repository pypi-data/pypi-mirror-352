import platform

__version__ = "0.7.0"


def get_client_version() -> str:
    runtime = platform.python_implementation()
    (major, minor, _patch) = platform.python_version_tuple()
    runtime_version = f"{runtime} {major}.{minor}"

    return f"Yield-SDK-Python/{__version__} ({runtime_version})"
