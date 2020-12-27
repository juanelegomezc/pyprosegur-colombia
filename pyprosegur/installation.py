"""Installation Representation."""
import enum
import logging

from pyprosegur.auth import Auth

LOGGER = logging.getLogger(__name__)


class Status(enum.Enum):
    """Alarm Panel Status."""

    ARMED = "AT"
    DISARMED = "DA"

    @staticmethod
    def from_str(code):
        """Convert Status Code to Enum."""
        if code == "AT":
            return Status.ARMED
        if code == "DA":
            return Status.DISARMED
        raise NotImplementedError(f"'{code}' not an implemented Installation.Status")


class Installation():
    """Alarm Panel Installation."""

    @classmethod
    async def retrieve(cls, auth: Auth, number: int = 0):
        """Retrieve an installation object."""
        self = Installation()
        self.number = number

        resp = await auth.request("GET", "/installation")

        resp_json = await resp.json()
        if resp_json["result"]["code"] != 200:
            LOGGER.error(resp_json["result"])
            return None

        self.data = resp_json["data"][self.number]

        self.installationId = self.data["installationId"]

        return self

    @property
    def contract(self):
        """Contract Identifier."""
        return self.data["contractId"]

    @property
    def status(self):
        """Alarm Panel Status."""
        return Status.from_str(self.data["status"])

    async def arm(self, auth: Auth):
        """Order Alarm Panel to Arm itself."""
        if self.status == Status.ARMED:
            return True

        data = {"statusCode": Status.ARMED.value}

        resp = await auth.request(
            "PUT", f"/installation/{self.installationId}/status", json=data
        )

        LOGGER.debug("ARM HTTP status: %s\t%s", resp.status, await resp.text())
        return resp.status == 200

    async def disarm(self, auth: Auth):
        """Order Alarm Panel to Disarm itself."""
        if self.status == Status.DISARMED:
            return True

        data = {"statusCode": Status.DISARMED.value}

        resp = await auth.request(
            "PUT", f"/installation/{self.installationId}/status", json=data
        )

        LOGGER.debug("DISARM HTTP status: %s\t%s", resp.status, await resp.text())
        return resp.status == 200