from suhteita.robot.TicketSystemLibrary.ticket_system_bridge import TicketSystemBridge


class TicketSystemLibrary(TicketSystemBridge):
    """Library for robot framework keyword tests."""

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
