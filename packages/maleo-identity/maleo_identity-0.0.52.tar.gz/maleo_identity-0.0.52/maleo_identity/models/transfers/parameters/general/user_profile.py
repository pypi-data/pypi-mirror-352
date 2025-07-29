from __future__ import annotations
from maleo_foundation.models.schemas.parameter import BaseParameterSchemas
from maleo_metadata.models.expanded_schemas.blood_type import MaleoMetadataBloodTypeExpandedSchemas
from maleo_metadata.models.expanded_schemas.gender import MaleoMetadataGenderExpandedSchemas
from maleo_identity.models.schemas.general import MaleoIdentityGeneralSchemas
from maleo_identity.models.schemas.user_profile import MaleoIdentityUserProfileSchemas

class MaleoIdentityUserProfileGeneralParametersTransfers:
    class GetSingleQuery(
        MaleoIdentityUserProfileSchemas.Expand,
        BaseParameterSchemas.OptionalListOfStatuses
    ): pass

    class GetSingle(
        MaleoIdentityUserProfileSchemas.Expand,
        BaseParameterSchemas.OptionalListOfStatuses,
        BaseParameterSchemas.IdentifierValue,
        MaleoIdentityUserProfileSchemas.IdentifierType
    ): pass

    class CreateOrUpdateQuery(MaleoIdentityUserProfileSchemas.Expand): pass

    class AvatarData(
        MaleoIdentityUserProfileSchemas.OptionalAvatarContentType,
        MaleoIdentityUserProfileSchemas.OptionalAvatar
    ): pass

    class CreateOrUpdateData(
        MaleoIdentityUserProfileSchemas.OptionalAvatarName,
        MaleoMetadataGenderExpandedSchemas.OptionalSimpleGender,
        MaleoMetadataBloodTypeExpandedSchemas.OptionalSimpleBloodType,
        MaleoIdentityUserProfileSchemas.BirthDate,
        MaleoIdentityUserProfileSchemas.BirthPlace,
        MaleoIdentityUserProfileSchemas.EndingTitle,
        MaleoIdentityUserProfileSchemas.LastName,
        MaleoIdentityUserProfileSchemas.MiddleName,
        MaleoIdentityUserProfileSchemas.FirstName,
        MaleoIdentityUserProfileSchemas.LeadingTitle,
        MaleoIdentityUserProfileSchemas.OptionalIdCard,
        MaleoIdentityGeneralSchemas.UserId
    ): pass

    class Create(
        AvatarData,
        CreateOrUpdateData,
        CreateOrUpdateQuery
    ): pass

    class Update(
        AvatarData,
        CreateOrUpdateData,
        CreateOrUpdateQuery,
        BaseParameterSchemas.IdentifierValue,
        MaleoIdentityUserProfileSchemas.IdentifierType
    ): pass