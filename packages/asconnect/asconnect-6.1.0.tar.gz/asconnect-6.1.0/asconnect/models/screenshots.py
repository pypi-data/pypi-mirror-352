"""App Models for the API"""

import enum

import deserialize

from asconnect.models.common import BaseAttributes, Resource, Links, Relationship, Reprable


class ScreenshotDisplayType(enum.Enum):
    """Screenshot display type."""

    APP_IPHONE_67 = "APP_IPHONE_67"
    APP_IPHONE_65 = "APP_IPHONE_65"
    APP_IPHONE_61 = "APP_IPHONE_61"
    APP_IPHONE_58 = "APP_IPHONE_58"
    APP_IPHONE_55 = "APP_IPHONE_55"
    APP_IPHONE_47 = "APP_IPHONE_47"
    APP_IPHONE_40 = "APP_IPHONE_40"
    APP_IPHONE_35 = "APP_IPHONE_35"
    APP_IPAD_PRO_3GEN_129 = "APP_IPAD_PRO_3GEN_129"
    APP_IPAD_PRO_3GEN_11 = "APP_IPAD_PRO_3GEN_11"
    APP_IPAD_PRO_129 = "APP_IPAD_PRO_129"
    APP_IPAD_105 = "APP_IPAD_105"
    APP_IPAD_97 = "APP_IPAD_97"
    APP_WATCH_ULTRA = "APP_WATCH_ULTRA"
    APP_WATCH_SERIES_7 = "APP_WATCH_SERIES_7"
    APP_WATCH_SERIES_4 = "APP_WATCH_SERIES_4"
    APP_WATCH_SERIES_3 = "APP_WATCH_SERIES_3"
    APP_DESKTOP = "APP_DESKTOP"
    APP_APPLE_TV = "APP_APPLE_TV"
    IMESSAGE_APP_IPHONE_67 = "IMESSAGE_APP_IPHONE_67"
    IMESSAGE_APP_IPHONE_65 = "IMESSAGE_APP_IPHONE_65"
    IMESSAGE_APP_IPHONE_61 = "IMESSAGE_APP_IPHONE_61"
    IMESSAGE_APP_IPHONE_58 = "IMESSAGE_APP_IPHONE_58"
    IMESSAGE_APP_IPHONE_55 = "IMESSAGE_APP_IPHONE_55"
    IMESSAGE_APP_IPHONE_47 = "IMESSAGE_APP_IPHONE_47"
    IMESSAGE_APP_IPHONE_40 = "IMESSAGE_APP_IPHONE_40"
    IMESSAGE_APP_IPAD_PRO_3GEN_129 = "IMESSAGE_APP_IPAD_PRO_3GEN_129"
    IMESSAGE_APP_IPAD_PRO_3GEN_11 = "IMESSAGE_APP_IPAD_PRO_3GEN_11"
    IMESSAGE_APP_IPAD_PRO_129 = "IMESSAGE_APP_IPAD_PRO_129"
    IMESSAGE_APP_IPAD_105 = "IMESSAGE_APP_IPAD_105"
    IMESSAGE_APP_IPAD_97 = "IMESSAGE_APP_IPAD_97"

    @staticmethod
    def from_name(name: str) -> "ScreenshotDisplayType":
        """Generate the display type from an image name.

        :param name: The name to convert

        :returns: The corresponding display type
        """
        identifier = name.split("-")[0]
        return ScreenshotDisplayType(identifier)


@deserialize.key("identifier", "id")
class AppScreenshotSet(Resource):
    """Represents an app store screenshot set."""

    @deserialize.key("screenshot_display_type", "screenshotDisplayType")
    class Attributes(BaseAttributes):
        """Attributes."""

        screenshot_display_type: ScreenshotDisplayType

    identifier: str
    attributes: Attributes
    relationships: dict[str, Relationship] | None
    links: Links


class AppMediaStateError(Reprable):
    """An app media state error."""

    code: str
    description: str


class AppMediaAssetStateState(enum.Enum):
    """The state value for and app media asset state."""

    AWAITING_UPLOAD = "AWAITING_UPLOAD"
    UPLOAD_COMPLETE = "UPLOAD_COMPLETE"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class AppMediaAssetState(Reprable):
    """An app media asset state."""

    errors: list[AppMediaStateError]
    state: AppMediaAssetStateState
    warnings: list[AppMediaStateError] | None


@deserialize.key("template_url", "templateUrl")
class ImageAsset(Reprable):
    """An image asset."""

    template_url: str
    height: int
    width: int


class UploadOperationHeader(Reprable):
    """An upload operation header."""

    name: str
    value: str


@deserialize.key("request_headers", "requestHeaders")
class UploadOperation(Reprable):
    """An upload operation."""

    length: int
    method: str
    offset: int
    request_headers: list[UploadOperationHeader]
    url: str


@deserialize.key("identifier", "id")
class AppScreenshot(Resource):
    """Represents an app store screenshot."""

    @deserialize.key("asset_delivery_state", "assetDeliveryState")
    @deserialize.key("asset_token", "assetToken")
    @deserialize.key("asset_type", "assetType")
    @deserialize.key("file_name", "fileName")
    @deserialize.key("file_size", "fileSize")
    @deserialize.key("image_asset", "imageAsset")
    @deserialize.key("source_file_checksum", "sourceFileChecksum")
    @deserialize.key("upload_operations", "uploadOperations")
    class Attributes(BaseAttributes):
        """Attributes."""

        asset_delivery_state: AppMediaAssetState
        asset_token: str
        asset_type: str
        file_name: str
        file_size: int | None
        image_asset: ImageAsset | None
        source_file_checksum: str | None
        uploaded: bool | None
        upload_operations: list[UploadOperation] | None

    identifier: str
    attributes: Attributes
    relationships: dict[str, Relationship] | None
    links: Links
