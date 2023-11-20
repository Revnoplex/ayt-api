from enum import Enum


class LongUploadsStatus(Enum):
    """The eligibility status of the channel to upload videos longer than 15 minutes"""

    allowed = "allowed"
    disallowed = "disallowed"
    eligible = "eligible"
    long_uploads_unspecified = "long_uploads_unspecified"

    def __str__(self):
        return self.value


class LiveBroadcastContent(Enum):
    live = "live"
    upcoming = "upcoming"
    none = "none"

    def __str__(self):
        return self.value


class VideoDefinition(Enum):
    hd = "hd"
    sd = "sd"

    def __str__(self):
        return self.value


class AcbRating(Enum):
    acb_c = "acb_c"
    acb_e = "acb_e"
    acb_g = "acb_g"
    acb_m = "acb_m"
    acb_ma15plus = "acb_ma15plus"
    acb_p = "acb_p"
    acb_pg = "acb_pg"
    acb_r18plus = "acb_r18plus"
    acb_unrated = "acb_unrated"

    def __str__(self):
        return self.value


class VideoProjection(Enum):
    _360 = "360"
    rectangular = "rectangular"

    def __str__(self):
        return self.value


class UploadStatus(Enum):
    deleted = "deleted"
    failed = "failed"
    processed = "processed"
    rejected = "rejected"
    uploaded = "uploaded"

    def __str__(self):
        return self.value


class UploadFailureReason(Enum):
    codec = "codec"
    conversion = "conversion"
    empty_file = "empty_file"
    invalid_file = "invalid_file"
    too_small = "too_small"
    upload_aborted = "upload_aborted"

    def __str__(self):
        return self.value


class UploadRejectionReason(Enum):
    claim = "claim"
    copyright = "copyright"
    duplicate = "duplicate"
    inappropriate = "inappropriate"
    legal = "legal"
    length = "length"
    terms_of_use = "terms_of_use"
    trademark = "trademark"
    uploader_account_closed = "uploader_account_closed"
    uploader_account_suspended = "uploader_account_suspended"

    def __str__(self):
        return self.value


class PrivacyStatus(Enum):
    private = "private"
    public = "public"
    unlisted = "unlisted"

    def __str__(self):
        return self.value


class License(Enum):
    creative_common = "creative_common"
    youtube = "youtube"

    def __str__(self):
        return self.value
