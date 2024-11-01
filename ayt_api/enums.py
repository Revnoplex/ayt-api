from enum import Enum


class LongUploadsStatus(Enum):
    """The eligibility status of the channel to upload videos longer than 15 minutes."""

    allowed = "allowed"
    disallowed = "disallowed"
    eligible = "eligible"
    long_uploads_unspecified = "long_uploads_unspecified"

    def __str__(self):
        return self.value


class LiveBroadcastContent(Enum):
    """Indicates if the video is a livestream and if it is live."""

    live = "live"
    upcoming = "upcoming"
    none = "none"

    def __str__(self):
        return self.value


class VideoDefinition(Enum):
    """Indicates whether the video is available in high definition (HD) or only in standard definition."""

    hd = "hd"
    sd = "sd"

    def __str__(self):
        return self.value


class AcbRating(Enum):
    """
    The video's Australian Classification Board (ACB) or Australian Communications andMedia Authority (ACMA) rating.
    ACMA ratings are used to classify children's television programming.
    """

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
    """Specifies the projection format of the video (example: 360 or rectangular)."""

    _360 = "360"
    rectangular = "rectangular"

    def __str__(self):
        return self.value


class UploadStatus(Enum):
    """The status of the uploaded video."""

    deleted = "deleted"
    failed = "failed"
    processed = "processed"
    rejected = "rejected"
    uploaded = "uploaded"

    def __str__(self):
        return self.value


class UploadFailureReason(Enum):
    """Explains why a video failed to upload."""

    codec = "codec"
    conversion = "conversion"
    empty_file = "empty_file"
    invalid_file = "invalid_file"
    too_small = "too_small"
    upload_aborted = "upload_aborted"

    def __str__(self):
        return self.value


class UploadRejectionReason(Enum):
    """Explains why YouTube rejected an uploaded video."""

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
    """The video's privacy status. Can be :attr:`private`, :attr:`public` or :attr:`unlisted`."""

    private = "private"
    public = "public"
    unlisted = "unlisted"
    privacy_status_unspecified = "privacy_status_unspecified"

    def __str__(self):
        return self.value


class License(Enum):
    """The video's license."""

    creative_common = "creative_common"
    youtube = "youtube"

    def __str__(self):
        return self.value


class CaptionStatus(Enum):
    """The caption track's status."""

    failed = "failed"
    serving = "serving"
    syncing = "syncing"

    def __str__(self):
        return self.value


class CaptionFailureReason(Enum):
    """The reason that YouTube failed to process the caption track."""

    processing_failed = "processing_failed"
    unknown_format = "unknown_format"
    unsupported_format = "unsupported_format"

    def __str__(self):
        return self.value


class AudioTrackType(Enum):
    """The type of audio track associated with the caption track."""

    commentary = "commentary"
    descriptive = "descriptive"
    primary = "primary"
    unknown = "unknown"

    def __str__(self):
        return self.value


class CaptionTrackKind(Enum):
    """The caption track's type."""

    asr = "asr"
    forced = "forced"
    standard = "standard"

    def __str__(self):
        return self.value


class SubscriptionActivityType(Enum):
    """
    The type of activity this subscription is for.

    .. versionadded:: 0.4.0
    """

    all = "all"
    uploads = "uploads"

    def __str__(self):
        return self.value


class UploadFileType(Enum):
    """
    The uploaded file's type as detected by YouTube's video processing engine.

    .. versionadded:: 0.4.0
    """

    archive = "archive"
    audio = "audio"
    document = "document"
    image = "image"
    other = "other"
    project = "project"
    video = "video"

    def __str__(self):
        return self.value


class ProcessingStatus(Enum):
    """
    The video's processing status.

    .. versionadded:: 0.4.0
    """

    failed = "failed"
    processing = "processing"
    succeeded = "succeeded"
    terminated = "terminated"

    def __str__(self):
        return self.value


class ProcessingFailureReason(Enum):
    """
    The reason that YouTube failed to process the video.

    .. versionadded:: 0.4.0
    """

    other = "other"
    streaming_failed = "streaming_failed "
    transcode_failed = "transcode_failed"
    upload_failed = "upload_failed"

    def __str__(self):
        return self.value


class ProcessingError(Enum):
    """
    Errors that will prevent YouTube from successfully processing the uploaded video.

    .. versionadded:: 0.4.0
    """

    archive_file = "archive_file"
    audio_file = "audio_file"
    doc_file = "doc_file"
    image_file = "image_file"
    not_a_video_file = "not_a_video_file"
    project_file = "project_file"

    def __str__(self):
        return self.value


class ProcessingWarning(Enum):
    """
    Reasons why YouTube may have difficulty transcoding the uploaded video or that might result in an
    erroneous transcoding.

    .. versionadded:: 0.4.0
    """

    has_editlist = "has_editlist"
    has_edit_list = "has_edit_list"
    inconsistent_resolution = "inconsistent_resolution"
    problematic_audio_codec = "problematic_audio_codec"
    problematic_video_codec = "problematic_video_codec"
    unknown_audio_codec = "unknown_audio_codec"
    unknown_container = "unknown_container"
    unknown_video_codec = "unknown_video_codec"

    def __str__(self):
        return self.value


class ProcessingHint(Enum):
    """
    Suggestions that may improve YouTube's ability to process the video.

    .. versionadded:: 0.4.0
    """

    non_streamable_mov = "non_streamable_mov"
    send_best_quality_video = "send_best_quality_video"

    def __str__(self):
        return self.value


class EditorSuggestion(Enum):
    """
    Video editing operations that might improve the video quality or playback experience of the uploaded video.

    .. versionadded:: 0.4.0
    """

    audio_quiet_audio_swap = "audio_quiet_audio_swap"
    video_auto_levels = "video_auto_levels"
    video_crop = "video_crop"
    video_stabilize = "video_stabilize"

    def __str__(self):
        return self.value
