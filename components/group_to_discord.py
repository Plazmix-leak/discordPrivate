from enum import Enum

from avocato.client.enum.groups import PermissionGroup


class _DiscoGroup:
    def __init__(self, group: PermissionGroup, discord_id: int):
        self._group = group
        self._discord_role_id = discord_id

    @property
    def plazmix_group(self) -> PermissionGroup:
        return self._group

    @property
    def discord_role_id(self):
        return self._discord_role_id


class _DiscoBadge:
    def __init__(self, technical_name: str, discord_id: int):
        self._discord_role_id = discord_id
        self._technical_name = technical_name

    @property
    def discord_role_id(self):
        return self._discord_role_id

    @property
    def technical_name(self):
        return self._technical_name


class BadgeCollection(Enum):
    LEGEND = _DiscoBadge("legend", 892668679437840394)
    TOP_WORKER = _DiscoBadge("top_worker", 892669689308807178)
    WORKER = _DiscoBadge("worker", 892669133769027585)
    VERIFICATION = _DiscoBadge("verification", 892669872742498326)
    PARTNER = _DiscoBadge("partner", 894341757859414066)
    PARTNER_DEVELOPER = _DiscoBadge("partner_developer", 892669458982780958)
    PLUS_SUB = _DiscoBadge("plus_sub", 892669997074231306)

    @classmethod
    def get_from_discord_id(cls, role_id: int):
        for group in cls:
            if group.value.discord_role_id == role_id:
                return group
        raise ValueError("Unknown badge")

    @classmethod
    def get_from_technical_name(cls, technical_name: str):
        for badge in cls:
            if badge.value.technical_name == technical_name:
                return badge
        raise ValueError("Unknown badge")


class GroupCollection(Enum):
    # EXAMPLE = _DiscoGroup("PLAZMIX_GROUP", 123)

    DEFAULT = _DiscoGroup(PermissionGroup.DEFAULT, 893623124183121970)

    # Донат
    STAR = _DiscoGroup(PermissionGroup.STAR, 893616857616121948)
    COSMO = _DiscoGroup(PermissionGroup.COSMO, 888177021635686460)
    GALAXY = _DiscoGroup(PermissionGroup.GALAXY, 893616870878498836)
    UNIVERSE = _DiscoGroup(PermissionGroup.UNIVERSE, 893616876742123530)
    LUXURY = _DiscoGroup(PermissionGroup.LUXURY, 894332621369274408)

    # Медиа
    YOUTUBE = _DiscoGroup(PermissionGroup.YOUTUBE, 893623581609693214)
    YOUTUBE_PLUS = _DiscoGroup(PermissionGroup.YOUTUBE_PLUS, 875905369069744159)

    # Специальные
    TESTER = _DiscoGroup(PermissionGroup.TESTER, 893623882496495626)

    # Персонал
    ART = _DiscoGroup(PermissionGroup.ART, 893624155054948412)
    BUILDER = _DiscoGroup(PermissionGroup.BUILDER, 876167084009193524)
    BUILDER_PLUS = _DiscoGroup(PermissionGroup.BUILDER_PLUS, 875909243071512576)
    JUNIOR = _DiscoGroup(PermissionGroup.JUNIOR, 893624484261666857)
    MODERATOR = _DiscoGroup(PermissionGroup.MODERATOR, 875490511530643597)
    MODERATOR_PLUS = _DiscoGroup(PermissionGroup.MODERATOR_PLUS, 876040232213045249)

    ASSISTANT = _DiscoGroup(PermissionGroup.ASSISTANT, 894575727498887198)
    DEVELOPER = _DiscoGroup(PermissionGroup.DEVELOPER, 875485931338096691)
    ADMINISTRATOR = _DiscoGroup(PermissionGroup.ADMINISTRATOR, 875489517002432562)
    OWN = _DiscoGroup(PermissionGroup.OWN, 875485650244210789)

    @classmethod
    def get_from_discord_id(cls, role_id: int):
        for group in cls:
            if group.value.discord_role_id == role_id:
                return group
        raise ValueError("Unknown group")

    @classmethod
    def get_from_plazmix_group(cls, plazmix_group: PermissionGroup):
        for group in cls:
            if group.value.plazmix_group.value == plazmix_group:
                return group
        raise ValueError("Unknown group")
