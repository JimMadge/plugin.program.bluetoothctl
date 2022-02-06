import xbmc  # type: ignore


def logdebug(message: str) -> None:
    """Log a message at DEBUG level"""
    log(message, xbmc.LOGDEBUG)


def loginfo(message: str) -> None:
    """Log a message at INFO level"""
    log(message, xbmc.LOGINFO)


def logwarning(message: str) -> None:
    """Log a message at WARNING level"""
    log(message, xbmc.LOGWARNING)


def logerror(message: str) -> None:
    """Log a message at ERROR level"""
    log(message, xbmc.LOGERROR)


def logfatal(message: str) -> None:
    """Log a message at FATAL level"""
    log(message, xbmc.LOGFATAL)


def log(message: str, level: int) -> None:
    """Log a message"""
    xbmc.log(f'bluetoothctl: {message}', level)
