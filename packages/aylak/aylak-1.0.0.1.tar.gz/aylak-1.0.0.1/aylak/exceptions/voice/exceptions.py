from ..erros import Error


class FfmpegError(Error):
    """Raised when an error occurs while using ffmpeg."""

    CODE = 500
    NAME = "FfmpegError"
    MESSAGE = "An error occurred while using ffmpeg: {value}"
