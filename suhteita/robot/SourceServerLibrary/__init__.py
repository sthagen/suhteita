from suhteita.robot.SourceServerLibrary.source_server_bridge import SourceServerBridge


class SourceServerLibrary(SourceServerBridge):
    """Library for robot framework keyword tests of source server services."""

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
