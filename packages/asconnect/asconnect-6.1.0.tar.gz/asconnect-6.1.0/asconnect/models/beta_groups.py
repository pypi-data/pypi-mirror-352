"""Beta groups models for the API"""

import deserialize

from asconnect.models.common import BaseAttributes, Links, Relationship, Resource


@deserialize.key("identifier", "id")
class BetaGroup(Resource):
    """Represents a beta group."""

    @deserialize.key("is_internal_group", "isInternalGroup")
    @deserialize.key("public_link", "publicLink")
    @deserialize.key("public_link_enabled", "publicLinkEnabled")
    @deserialize.key("public_link_id", "publicLinkId")
    @deserialize.key("public_link_limit", "publicLinkLimit")
    @deserialize.key("public_link_limit_enabled", "publicLinkLimitEnabled")
    @deserialize.key("created_date", "createdDate")
    @deserialize.key("feedback_enabled", "feedbackEnabled")
    class Attributes(BaseAttributes):
        """Represents beta group attributes."""

        is_internal_group: bool
        name: str
        public_link: str | None
        public_link_enabled: bool | None
        public_link_id: str | None
        public_link_limit: int | None
        public_link_limit_enabled: bool | None
        created_date: str
        feedback_enabled: bool

    identifier: str
    attributes: Attributes
    relationships: dict[str, Relationship] | None
    links: Links
