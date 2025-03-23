import platform

def is_raspberry_pi():
    return platform.system() == "Linux" and platform.machine() == "aarch64"
