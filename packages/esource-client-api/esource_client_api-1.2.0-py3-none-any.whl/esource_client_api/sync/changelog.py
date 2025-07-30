from typing import List

from .base_resource import BaseResource
from .session import Session
from ..models.models import ChangeLog


class Changelog(BaseResource):
    """Handles operations related to the /changelog endpoint."""
    def __init__(self, session: Session):
        super().__init__(session)
        self.base_url = "v1/changelog"

    def list_changelogs(self, timestamp) -> List[ChangeLog]:
        """
        Fetches changelog entries since a specific timestamp.

        Args:
            timestamp (str): ISO 8601 formatted date-time string.
                             Only changes occurring after this time will be returned.

        Returns:
            list: A list of changelog entries.
        """
        if not timestamp:
            raise ValueError("The 'timestamp' parameter is required.")

        params = {"timestamp": timestamp}
        data = self.session.get(self.base_url, params=params)

        return [ChangeLog(**item) for item in data]
