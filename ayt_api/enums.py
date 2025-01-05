from __future__ import annotations
from enum import Enum


class LongUploadsStatus(Enum):
    """
    The eligibility status of the channel to upload videos longer than 15 minutes.

    Attributes:
        allowed: This channel can upload videos that are more than 15 minutes long.
        disallowed: This channel is not able or eligible to upload videos that are more than 15 minutes long.
        eligible: This channel is eligible to upload videos that are more than 15 minutes long.
        long_uploads_unspecified: YouTube may occasionally return this value if the status is unavailable.
    """

    allowed = "allowed"
    disallowed = "disallowed"
    eligible = "eligible"
    long_uploads_unspecified = "long_uploads_unspecified"

    def __str__(self):
        return self.value


class LiveBroadcastContent(Enum):
    """
    Indicates if the video is a livestream and if it is live.

    Attributes:
        live: The video is an active live broadcast.
        upcoming: The video is an upcoming broadcast.
        none: The video is not an upcoming/active live broadcast.
    """

    live = "live"
    upcoming = "upcoming"
    none = "none"

    def __str__(self):
        return self.value


class VideoDefinition(Enum):
    """
    Indicates whether the video is available in high definition (HD) or only in standard definition.

    Attributes:
        hd: The video is available in high definition (HD).
        sd: The video is only in standard definition.
    """

    hd = "hd"
    sd = "sd"

    def __str__(self):
        return self.value


class AcbRating(Enum):
    """
    The video's Australian Classification Board (ACB) or Australian Communications andMedia Authority (ACMA) rating.
    ACMA ratings are used to classify children's television programming.

    Attributes:
        acb_c: Programs that have been given a C classification by the Australian Communications and Media Authority.
            These programs are intended for children (other than preschool children) who are younger than 14 years of
            age.
        acb_e: Exempt (E): Some video are exempt from needing to be classified.
        acb_g: General (G) The content is very mild in impact. Videos classified G (General) are suitable for everyone.
            They can have content that may scare very young children.
        acb_m: Mature (M): The content is moderate in impact. Videos classified M (Mature) are not
            recommended for children under the age of 15. They can have content such as violence and themes that
            requires a mature outlook.
        acb_ma15plus: Mature Accompanied (MA 15+): The content is strong in impact. Films and computer games classified
            MA 15+ are legally restricted to people aged 15 and over. They can contain content such as sex scenes and
            drug use that may have a strong impact on the viewer.
        acb_p: Preschool (P): Programs that have been given a P classification by the Australian Communications and
            Media Authority. These programs are intended for preschool children.
        acb_pg: Parental Guidance (PG): The content is mild in impact. Films and computer games classified PG
            (Parental Guidance) can have content that a child may find confusing or upsetting and require the guidance
            of a parent or guardian. It is not recommended for viewing by children under the age of 15 without guidance
            of a parent or guardian.
        acb_r18plus: Restricted (R 18+): The content is high in impact. Films and computer games classified as R 18+
            are legally restricted to adults 18 years and over. They can contain content that may be offensive to
            sections of the adult community.
        acb_unrated: No rating is available.
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
    """
    Specifies the projection format of the video (example: 360 or rectangular).

    Attributes:
        _360: The video is a 360 video that will work with VR headsets.
        rectangular: The video is a regular rectangular video.
    """

    _360 = "360"
    rectangular = "rectangular"

    def __str__(self):
        return self.value


class UploadStatus(Enum):
    """
    The status of the uploaded video.

    Attributes:
        deleted: The upload was deleted.
        failed: The upload process failed.
        rejected: The upload has been rejected by YouTube.
        uploaded: The upload was successful.
    """

    deleted = "deleted"
    failed = "failed"
    processed = "processed"
    rejected = "rejected"
    uploaded = "uploaded"

    def __str__(self):
        return self.value


class UploadFailureReason(Enum):
    """
    Explains why a video failed to upload.

    Attributes:
        codec: The upload has an unsupported codec.
        conversion: Converting the upload failed.
        empty_file: The upload file is empty.
        invalid_file: The upload file is an invalid file type.
        too_small: The upload file is too small.
        upload_aborted: The upload process was aborted.
    """

    codec = "codec"
    conversion = "conversion"
    empty_file = "empty_file"
    invalid_file = "invalid_file"
    too_small = "too_small"
    upload_aborted = "upload_aborted"

    def __str__(self):
        return self.value


class UploadRejectionReason(Enum):
    """
    Explains why YouTube rejected an uploaded video.

    Attributes:
        claim: The upload has a copyright claim.
        copyright: The upload was rejected due to a copyright takedown request.
        duplicate: The upload is a duplicate of an existing upload.
        inappropriate: The upload contains inappropriate material not suitable for YouTube.
        legal: The upload was rejected for legal reasons.
        length: The upload is too long
        terms_of_use: The upload violates YouTube's terms of use.
        trademark: The upload was rejected due to trademark reasons.
        uploader_account_closed: The account of the uploader is deleted or terminated.
        uploader_account_suspended: The account of the uploader is suspended.
    """

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
    """
    The video or playlist's privacy status. Can be :attr:`private`, :attr:`public` or :attr:`unlisted`.

    Attributes:
        private: The video or playlist is only available to the uploader/owner and people granted access.
        public: The video or playlist is visible to everyone.
        unlisted: The video or playlist is accessible to anyone with its link.
        privacy_status_unspecified: The privacy status of the video is unknown.
    """

    private = "private"
    public = "public"
    unlisted = "unlisted"
    privacy_status_unspecified = "privacy_status_unspecified"

    def __str__(self):
        return self.value


class PodcastStatus(Enum):
    """
    A playlist's podcast status.

    .. versionadded:: 0.4.0

    Attributes:
        enabled: The playlist is marked as a podcast show
        disabled: the playlist is not marked as a podcast show
        unspecified: The podcast status is unspecified.
    """

    enabled = "enabled"
    disabled = "disabled"
    unspecified = "unspecified"

    def __str__(self):
        return self.value


class License(Enum):
    """
    The video's license.

    Attributes:
        creative_common: The video uses a creative commons license.
        youtube: The video uses YouTube's standard license.
    """

    creative_common = "creative_common"
    youtube = "youtube"

    def __str__(self):
        return self.value


class CaptionStatus(Enum):
    """
    The caption track's status.

    Attributes:
        failed: Processing the caption track failed.
        serving: The caption track is currently serving.
        syncing: The caption track is currently being synced.
    """

    failed = "failed"
    serving = "serving"
    syncing = "syncing"

    def __str__(self):
        return self.value


class CaptionFailureReason(Enum):
    """
    The reason that YouTube failed to process the caption track.

    Attributes:
        processing_failed: YouTube failed to process the uploaded caption track.
        unknown_format: The caption track's format was not recognized.
        unsupported_format: The caption track's format is not supported.
    """

    processing_failed = "processing_failed"
    unknown_format = "unknown_format"
    unsupported_format = "unsupported_format"

    def __str__(self):
        return self.value


class AudioTrackType(Enum):
    """
    The type of audio track associated with the caption track.

    Attributes:
        commentary: The caption track corresponds to an alternate audio track that includes commentary, such as
            directory commentary.
        descriptive: The caption track corresponds to an alternate audio track that includes additional descriptive
            audio.
        primary: The caption track corresponds to the primary audio track for the video, which is the audio track
            normally associated with the video.
        unknown: This is the default value.
    """

    commentary = "commentary"
    descriptive = "descriptive"
    primary = "primary"
    unknown = "unknown"

    def __str__(self):
        return self.value


class CaptionTrackKind(Enum):
    """
    The caption track's type.

    Attributes:
        asr: A caption track generated using automatic speech recognition.
        forced: A caption track that plays when no other track is selected in the player. For example, a video that
            shows aliens speaking in an alien language might have a forced caption track to only show subtitles for the
            alien language.
        standard: A regular caption track. This is the default value.
    """

    asr = "asr"
    forced = "forced"
    standard = "standard"

    def __str__(self):
        return self.value


class SubscriptionActivityType(Enum):
    """
    The type of activity this subscription is for.

    .. versionadded:: 0.4.0

    Attributes:
        all: This subscription is for everything
        uploads: This subscription is specifically for uploads.
    """

    all = "all"
    uploads = "uploads"

    def __str__(self):
        return self.value


class UploadFileType(Enum):
    """
    The uploaded file's type as detected by YouTube's video processing engine.

    .. versionadded:: 0.4.0

    Attributes:
        archive: The file is an archive file, such as a .zip archive.
        audio: The file is a known audio file type, such as an .mp3 file.
        document: The file is a document or text file, such as an MS Word document.
        image: The file is an image file, such as a .jpeg image.
        other: The file is another non-video file type.
        project: The file is a video project file, such as a Microsoft Windows Movie Maker project, that does not
            contain actual video data.
        video: The file is a known video file type, such as an .mp4 file.
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

    Attributes:
        failed: Video processing has failed. See ProcessingFailureReason.
        processing: Video is currently being processed. See ProcessingProgress.
        succeeded: Video has been successfully processed.
        terminated: Processing information is no longer available.
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

    Attributes:
        other: Some other processing component has failed.
        streaming_failed: Video could not be sent to streamers.
        transcode_failed: Content transcoding has failed.
        upload_failed: File delivery has failed.
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

    Attributes:
        archive_file: An archive file (e.g., a ZIP archive).
        audio_file: File contains audio only (e.g., an MP3 file).
        doc_file: Document or text file (e.g., MS Word document).
        image_file: Image file (e.g., a JPEG image).
        not_a_video_file: Other non-video file.
        project_file: Movie project file (e.g., Microsoft Windows Movie Maker project).
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

    Attributes:
        has_editlist: Edit lists are not currently supported.
        has_edit_list: Alias of :attr:`has_editlist`. Edit lists are not currently supported.
        inconsistent_resolution: Conflicting container and stream resolutions.
        problematic_audio_codec: Audio codec that is known to cause problems was used.
        problematic_video_codec: Video codec that is known to cause problems was used.
        unknown_audio_codec: Unrecognized audio codec, transcoding is likely to fail.
        unknown_container: Unrecognized file format, transcoding is likely to fail.
        unknown_video_codec: Unrecognized video codec, transcoding is likely to fail.
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

    Attributes:
        non_streamable_mov: The MP4 file is not streamable, this will slow down the processing.
        send_best_quality_video: Probably a better quality version of the video exists.
    """

    non_streamable_mov = "non_streamable_mov"
    send_best_quality_video = "send_best_quality_video"

    def __str__(self):
        return self.value


class EditorSuggestion(Enum):
    """
    Video editing operations that might improve the video quality or playback experience of the uploaded video.

    .. versionadded:: 0.4.0

    Attributes:
        audio_quiet_audio_swap: The audio track appears silent and could be swapped with a better quality one.
        video_auto_levels: Picture brightness levels seem off and could be corrected.
        video_crop: Margins (mattes) detected around the picture could be cropped.
        video_stabilize: The video appears shaky and could be stabilized.
    """

    audio_quiet_audio_swap = "audio_quiet_audio_swap"
    video_auto_levels = "video_auto_levels"
    video_crop = "video_crop"
    video_stabilize = "video_stabilize"

    def __str__(self):
        return self.value


class OAuth2Scope(Enum):
    """
    OAuth2 scopes when using OAuth2 with the library.

    Attributes:
        youtube: Manage your YouTube account.
        youtube_channel_memberships_creator: See a list of your current active channel members, their current level,
            and when they became a member.
        youtube_force_ssl: See, edit, and permanently delete your YouTube videos, ratings, comments and captions.
        youtube_readonly: View your YouTube account.
        youtube_upload: Manage your YouTube videos.
        youtube_partner: View and manage your assets and associated content on YouTube.
        youtube_partner_channel_audit: View private information of your YouTube channel relevant during the audit
            process with a YouTube partner.
    """
    youtube = "https://www.googleapis.com/auth/youtube"
    youtube_channel_memberships_creator = "https://www.googleapis.com/auth/youtube.channel-memberships.creator"
    youtube_force_ssl = "https://www.googleapis.com/auth/youtube.force-ssl"
    youtube_readonly = "https://www.googleapis.com/auth/youtube.readonly"
    youtube_upload = "https://www.googleapis.com/auth/youtube.upload"
    youtube_partner = "https://www.googleapis.com/auth/youtubepartner"
    youtube_partner_channel_audit = "https://www.googleapis.com/auth/youtubepartner-channel-audit"

    def __str__(self):
        return self.value

    @classmethod
    def all(cls) -> list[OAuth2Scope]:
        """
        A list of all the available scopes related to the YouTube data api.

        Returns:
            list[OAuth2Scope]: A list of all the scopes
        """
        return [
            cls.youtube, cls.youtube_channel_memberships_creator, cls.youtube_force_ssl, cls.youtube_readonly,
            cls.youtube_upload, cls.youtube_partner, cls.youtube_partner_channel_audit
        ]

    @classmethod
    def default(cls) -> list[OAuth2Scope]:
        """
        A list of scopes used by this library by default.

        Returns:
            list[OAuth2Scope]: A list of all the scopes
        """
        return [cls.youtube]


class CaptionFormat(Enum):
    """
    The available caption formats YouTube support.

    Attributes:
        sbv: SubViewer subtitle.
        scc: Scenarist Closed Caption format.
        srt: SubRip subtitle.
        ttml: Timed Text Markup Language caption.
        vtt: Web Video Text Tracks caption.

    """

    sbv = "sbv"
    scc = "scc"
    srt = "srt"
    ttml = "ttml"
    vtt = "vtt"

    def __str__(self):
        return self.value


class WatermarkTimingType(Enum):
    """
    The timing method that determines when the watermark image is displayed during the video playback.

    Attributes:
        offset_from_start: The offset is from the start of the video.
        offset_from_end: The offset is from the end of the video.

    """
    offset_from_start = "offset_from_start"
    offset_from_end = "offset_from_end"

    def __str__(self):
        return self.value
