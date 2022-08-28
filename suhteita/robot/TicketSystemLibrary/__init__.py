from suhteita.robot.TicketSystemLibrary.ticket_system_bridge import TicketSystemBridge


class TicketSystemLibrary(TicketSystemBridge):
    """Library for robot framework keyword tests of ticket system services."""

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
