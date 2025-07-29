from typing import Dict
from maleo_identity.enums.user_profile import MaleoIdentityUserProfileEnums

class MaleoIdentityUserProfileConstants:
    IDENTIFIER_TYPE_VALUE_TYPE_MAP:Dict[
        MaleoIdentityUserProfileEnums.IdentifierType,
        object
    ] = {
        MaleoIdentityUserProfileEnums.IdentifierType.USER_ID: int,
        MaleoIdentityUserProfileEnums.IdentifierType.ID_CARD: str,
    }

    MIME_TYPE_EXTENSION_MAP:Dict[
        MaleoIdentityUserProfileEnums.ValidImageMimeType,
        str
    ] = {
        MaleoIdentityUserProfileEnums.ValidImageMimeType.JPEG: ".jpeg",
        MaleoIdentityUserProfileEnums.ValidImageMimeType.JPG: ".jpg",
        MaleoIdentityUserProfileEnums.ValidImageMimeType.PNG: ".png",
    }