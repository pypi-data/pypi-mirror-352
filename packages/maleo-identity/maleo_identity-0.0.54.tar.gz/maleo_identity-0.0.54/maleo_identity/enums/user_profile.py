from enum import StrEnum

class MaleoIdentityUserProfileEnums:
    class IdentifierType(StrEnum):
        USER_ID = "user_id"
        ID_CARD = "id_card"

    class ValidImageMimeType(StrEnum):
        JPEG = "image/jpeg"
        JPG = "image/jpg"
        PNG = "image/png"

    class ExpandableFields(StrEnum):
        GENDER = "gender"
        BLOOD_TYPE = "blood_type"