from dataclasses import dataclass


@dataclass
class P_CLI_100(Exception):
    """Check In Connection Failure while Stopping Agent"""

    codename: str = "P_CLI_100"
    message: str = "Check In Connection Failure while Stopping Agent"

    def __str__(self):
        return f"{self.codename}: {self.message}"
