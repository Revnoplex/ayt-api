# Changelog

All notable changes are kept track of in this file for use in creating release notes.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.4.0] - 2025-01-06

**BREAKING CHANGES.** See *Changed* and *Removed* for details.

**This Version Drops Python 3.8 Support**

### Added

- API call `fetch_channel_from_handle` that fetches channel information using a channel handle instead of a channel id. 
([40470a9#diff-cbbc953-R394](https://github.com/Revnoplex/ayt-api/commit/40470a952af9d870d8a348aaae4286cf7d51a7d0#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R394))
- API util `resolve_handle` that gets a channel id from a channel's handle.
([40470a9#diff-cbbc953-R581](https://github.com/Revnoplex/ayt-api/commit/40470a952af9d870d8a348aaae4286cf7d51a7d0#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R581))
- Parameter `oauth_token` to `AsyncYoutubeAPI` to authenticate using an OAuth2 token. 
([b7a188d#diff-cbbc953-R33](https://github.com/Revnoplex/ayt-api/commit/b7a188de98f9d5f1667f5ff63a0c3d52d5818374#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R33))
- Parameter `authorised` to `fetch_video()` which prompts the return of `AuthorisedYoutubeVideo` over a `YoutubeVideo`. 
([032e817](https://github.com/Revnoplex/ayt-api/commit/032e8174eb26ce222952c58246d8eaef70ea6f12))
- Exception `NoAuth` which raises when neither an API key nor OAuth token is passed to `AsyncYoutubeAPI`. 
([b7a188d#diff-3f857ff](https://github.com/Revnoplex/ayt-api/commit/b7a188de98f9d5f1667f5ff63a0c3d52d5818374#diff-3f857ff3ed9ca4dc99077beeb478c3f68371dbbfa6b84ede9fd9f3d47d72b788))
- Exception `NoSession` which raises when performing an operation that needs an `OAuth2Session` instance when there isn't one. 
([9cf6422](https://github.com/Revnoplex/ayt-api/commit/9cf6422675e74ae6063744f8840c45405dc5f0a3))
- Base Exception `AuthException` which is the base for authorisation related errors.
([fedeb89#diff-3f857ff-R16](https://github.com/Revnoplex/ayt-api/commit/fedeb89a67e1455ccef0c5337dfd21f4523f314b#diff-3f857ff3ed9ca4dc99077beeb478c3f68371dbbfa6b84ede9fd9f3d47d72b788R16))
- Base Exception `OAuth2Exception` which is the base for OAuth2 related errors.
([fedeb89#diff-3f857ff-R21](https://github.com/Revnoplex/ayt-api/commit/fedeb89a67e1455ccef0c5337dfd21f4523f314b#diff-3f857ff3ed9ca4dc99077beeb478c3f68371dbbfa6b84ede9fd9f3d47d72b788R21))
- Parameter `max_items` to all playlist item API calls. 
([90e1ad1](https://github.com/Revnoplex/ayt-api/commit/90e1ad16e10a38b37fa9b78b4249acb7843f9f14))
- Parameter `use_oauth` to `AsyncYoutubeAPI` to prefer authenticating with OAuth2 over using an API key. 
([7ae3f3e#diff-cbbc953-R32](https://github.com/Revnoplex/ayt-api/commit/7ae3f3e7183c6b7ec8b405e21c487688e47b4d0a#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R32))
- API call `fetch_subscriptions` and associated types that fetches the subscriptions a channel has.
([53674e6](https://github.com/Revnoplex/ayt-api/commit/53674e6f02e4d007e05ed34ef2d00017ca0ff3fe),
[48b0dd3](https://github.com/Revnoplex/ayt-api/commit/48b0dd31c5702105bb03c25c854c2e5b3ed0d280))
- Video categories (api call and associated types). 
([9d60ec3](https://github.com/Revnoplex/ayt-api/commit/9d60ec3373042a33f2a0893b219d1b07b28825a4), 
[455ec21](https://github.com/Revnoplex/ayt-api/commit/455ec218551f774c936558f9af153eafaa98a762))
- Exception `InvalidToken` which raises when the OAuth token is invalid.
([9190f66](https://github.com/Revnoplex/ayt-api/commit/9190f66ff4964efd21c11c7f289901f8301de95b))
- `AsyncYoutubeAPI` class-method `with_authorisation_code` which allows initialising using an OAuth2 authorisation code.
([079797a](https://github.com/Revnoplex/ayt-api/commit/079797ac1988d81d9590167e22668fb0a2f4aa31))
- `AsyncYoutubeAPI` class-method `with_oauth_flow_generator` which automates the OAuth2 authorisation flow.
([6aede33#diff-cbbc953-R69](https://github.com/Revnoplex/ayt-api/commit/6aede33eea2f50920eec5f81f2ac7c165a1e91b9#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R69))
- Util `basic_html_page()` that creates a html page for `with_oauth_flow_generator()` to display.
([80857bb](https://github.com/Revnoplex/ayt-api/commit/80857bb6bb2d02b17d49244c72ba64748fd6be16))
- `AsyncYoutubeAPI` class-method `generate_url_and_socket` which returns an OAuth2 consent url and socket to be used 
with `with_authcode_receiver` after giving the user the consent url. 
([774a185#diff-cbbc953-R72](https://github.com/Revnoplex/ayt-api/commit/774a18576ba438bddedcbe555afc06cd576030f5#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R72))
- `AsyncYoutubeAPI` class-method `with_authcode_receiver` which listens for an OAuth2 authentication code on the socket provided. 
([774a185#diff-cbbc953-R97](https://github.com/Revnoplex/ayt-api/commit/774a18576ba438bddedcbe555afc06cd576030f5#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R97))
- API call `fetch_youtube_regions` that fetches regions listed by YouTube. 
([f39b0a5#diff-cbbc953-R951](https://github.com/Revnoplex/ayt-api/commit/f39b0a53241adaf386ab1fdbc9689007e7bc7ce5#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R951))
- API call `fetch_youtube_languages` that fetches languages listed by YouTube. 
([f39b0a5#diff-cbbc953-R974](https://github.com/Revnoplex/ayt-api/commit/f39b0a53241adaf386ab1fdbc9689007e7bc7ce5#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R974))
- Enums for class `AuthorisedYoutubeVideo`. 
([19944de](https://github.com/Revnoplex/ayt-api/commit/19944deeacf8a0a68c3bbb2cfbb34e9123d89f0b))
- Class `OAuth2Session` for managing the current OAuth2 session.
([baa7b9d](https://github.com/Revnoplex/ayt-api/commit/baa7b9d8c6aeb543847ea08bd6b9cea242804178))
- Function `refresh_session` which refreshes the OAuth2 token for a session. 
([4e210fd](https://github.com/Revnoplex/ayt-api/commit/4e210fd62c5287566d92c1fef5ec3cc5e11c4d9d))
- Checker function `is_expired` to class `OAuth2Session`. 
([3ce06f7](https://github.com/Revnoplex/ayt-api/commit/3ce06f7a28a6903381c77c00a05607217e8d445c))
- `podcast_status` attribute to `YoutubePlaylist` and enum. 
([5c85d35](https://github.com/Revnoplex/ayt-api/commit/5c85d353d00cd0a40c7d5ccd22dc00160fe7a5bc))
- Enum `OAuth2Scope` and implementations into `AsyncYoutubeAPI.generate_url_and_socket()`. 
([3bd435a](https://github.com/Revnoplex/ayt-api/commit/3bd435a1079ffae33cb717f38b26df8e216fd1b8))
- Attribute `has_paid_product_placement` to class `YoutubeVideo`.
([e012a58](https://github.com/Revnoplex/ayt-api/commit/e012a5819b828132467e7e57d19f52e001ddf4eb))
- Attribute `contains_synthetic_media` to `YoutubeVideo` as a settable value when updating the instance. 
([10881c0#diff-7363042-R745](https://github.com/Revnoplex/ayt-api/commit/10881c08f8689da24cf2cc4062c7c15aa2240dbf#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834R745))
- API call `update_video` which can update metadata for a video. 
([4bfb5d1#cbbc953-R1250](https://github.com/Revnoplex/ayt-api/commit/4bfb5d1409ca2fe4092efce070f52d4326608d05#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R1250))
- Class `UseExisting` and constant `EXISTING` for new update methods as an indicator to use the existing values. 
([4bfb5d1#diff-7363042-R2209](https://github.com/Revnoplex/ayt-api/commit/4bfb5d1409ca2fe4092efce070f52d4326608d05#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834R2209))
- Util `use_existing` which is used in update methods to determine if the existing value should be used.
([4bfb5d1#diff-920c31e](https://github.com/Revnoplex/ayt-api/commit/4bfb5d1409ca2fe4092efce070f52d4326608d05#diff-920c31e8df6efd41a120b70811f3494522b1587fe3bd4cc389823cb5b004e407))
- Update method to `YoutubeVideo`. 
([c2bbd8d](https://github.com/Revnoplex/ayt-api/commit/c2bbd8d28b7f886acf19a6c098e512ed48cfdda5))
- Quota usage is now kept track of per session and is accessible via `AsyncYoutubeAPI.quota_usage`. 
([e8c42c8](https://github.com/Revnoplex/ayt-api/commit/e8c42c811b3a2ab99028c450d9d080cddd6d75f7))
- Etag attributes to classes of API calls. 
([d44b5a3](https://github.com/Revnoplex/ayt-api/commit/d44b5a37e3201bb6e19640232a7da989de1cf450),
[d2e3bcb](https://github.com/Revnoplex/ayt-api/commit/d2e3bcb1d482ec9f710946bd6ff88f91183bf03f))
- Enum `CaptionFormat` as a list of caption track formats supported by YouTube. 
([7e912bc](https://github.com/Revnoplex/ayt-api/commit/7e912bc752e21fdc2dc15ba8424bffdde4f14347))
- API method `download_caption()` to download captions if you are the owner of the captions. 
([af49fe6](https://github.com/Revnoplex/ayt-api/commit/af49fe6b8838a16aebe89d6f2e89b9219471a8d0))
- API method `save_caption()` to download **and save** captions if you are the owner of the captions. 
([482ff7c](https://github.com/Revnoplex/ayt-api/commit/482ff7cfc674066318038661ea4f77cdc075941d))
- `download()` and `save()` API methods to `VideoCaption`. 
([0e3c0ea](https://github.com/Revnoplex/ayt-api/commit/0e3c0ea25d261aa12d4fa5545725a76b06f25bbe))
- API method `set_video_thumbnail()` which uploads and sets thumbnails for a video. 
([ce864de](https://github.com/Revnoplex/ayt-api/commit/ce864defb5eb4d0871be00863850a6671e3d69d8))
- `set_thumbnnail()` API method to `AuthorisedYoutubeVideo`. 
([b292720](https://github.com/Revnoplex/ayt-api/commit/b292720fb00a11b3c9d969a4930bb06aef10d535))
- Util `ensure_missing_keys()`. See documentation for details. 
([088166f](https://github.com/Revnoplex/ayt-api/commit/088166f8ad6914e1deafc3475a54469e33eaea48))
- API call `update_channel()` which can update some metadata for a channel. 
([41c37d3](https://github.com/Revnoplex/ayt-api/commit/41c37d329f7758cd6a236dcd98f844b73daeeb1d))
- Update method to `YoutubeChannel`. 
([2a4eb75](https://github.com/Revnoplex/ayt-api/commit/2a4eb751ec5df5ff6b5fdffe801c113ba69770e0))
- Methods to set the banner image of a channel. 
([15d2e26](https://github.com/Revnoplex/ayt-api/commit/15d2e266bab23dfce1e34cb5eb5fae29b7e43162))
- Options to set the width of a YouTube channel banner. 
([58856d7](https://github.com/Revnoplex/ayt-api/commit/58856d7fcea5c99a4e599d68cd117cf7306c0f6c))
- Methods, classes and exceptions for watermarks.
([9c9126b](https://github.com/Revnoplex/ayt-api/commit/9c9126b143bc8b17de7fb571985416bf0a4a7fa5))
- Alias of `YoutubeChannel.custom_url`: `handle`.
([a5bcc67](https://github.com/Revnoplex/ayt-api/commit/a5bcc6701cefe94fd471ba577d7c1d9855568da2))
- Methods and classes for metadata on custom playlist cover images. 
([554ec4d](https://github.com/Revnoplex/ayt-api/commit/554ec4d05761b8d4eacf09fd3cbe625dc88f60a8))
- Parameter `ignore_not_found` to methods that can take multiple items. 
([4ae024c](https://github.com/Revnoplex/ayt-api/commit/4ae024c1614ccf01ef8f6021b5b9f73fc737a8ab))
- Methods to add items to playlists.
([a307789](https://github.com/Revnoplex/ayt-api/commit/a30778914a34a8e3931a0e58315eed82f08dd5e8))
- Attribute `resource_id` to `PlaylistItem`. 
([a6becbd](https://github.com/Revnoplex/ayt-api/commit/a6becbd0b6f64a151e3248d5de10629c74d77ebb))
- Update method for `PlaylistItem`s. 
([99c854f](https://github.com/Revnoplex/ayt-api/commit/99c854ff6f7c7bb8c63db3d0a36a4a18155d983b))
- Update method for `Playlist`s.
([ea250b6](https://github.com/Revnoplex/ayt-api/commit/ea250b62e4e372a262f14aaa389dcdf325862bcb)) 
- Method to specify OAuth token type. 
([5f53155](https://github.com/Revnoplex/ayt-api/commit/5f53155a240b14d4a1cb76b2b92b1a1b213bc16f))
- Method to fetch playlists created by a channel.
([f38d271](https://github.com/Revnoplex/ayt-api/commit/f38d2719d2d475da57ffaca735696c0796610450))
- Method to fetch playlists owned by an authenticated user.
([ba2b44c](https://github.com/Revnoplex/ayt-api/commit/ba2b44c31dae9e9118db4f9ae701afe6ff320fc0))
- Method to fetch the channel owned by an authenticated user.
([0f34669](https://github.com/Revnoplex/ayt-api/commit/0f34669513317c413bd6b69397f3dfa7b1aa74dd))
- *Documentation*: New homepage added to pypi links. 
([601e763](https://github.com/Revnoplex/ayt-api/commit/601e7633514fb6dfa397d45d6a3ec4e6beff23cf))
- *Documentation*: Changelog added to pypi links.
([2f9663c](https://github.com/Revnoplex/ayt-api/commit/2f9663cdcc61d4c6a642eb7bebaec1b24a264065))
- *Documentation*: New logo added to [README.md](README.md).
([ab5bda2](https://github.com/Revnoplex/ayt-api/commit/ab5bda215d8850bbacbdac358341c5d34e49b3bd))
- *Documentation*: Added readthedocs documentation. (too many commits to list)
- *Documentation*: Added OAuth2 examples. 
([5dcbf3f](https://github.com/Revnoplex/ayt-api/commit/5dcbf3fc8341744028a4349e131069c349edb882), 
[890d8c7](https://github.com/Revnoplex/ayt-api/commit/890d8c72675916f6b902c7dbb4c99ced624b937d), 
[ffdd5f1](https://github.com/Revnoplex/ayt-api/commit/ffdd5f117a4a22ec3f883e37af1184b162ba80b0))
- *Documentation*: Examples for setting video thumbnails, channel banners and watermarks.
([62f6879](https://github.com/Revnoplex/ayt-api/commit/62f6879770a9426f3270e50e264703e55a6b476a))

### Removed

- **Breaking**: Python 3.8 support.
([53c66cd](https://github.com/Revnoplex/ayt-api/commit/53c66cd0edcc0cc812f854d2209fa6a8bb7752bc))

### Deprecated
- `censor_token` in favour of `censor_key`. 
([a4c0258](https://github.com/Revnoplex/ayt-api/commit/a4c02587779aa64e42399d68c2fa65822b40a87a))
- `exclude` in favor of `ignore_not_found`.
([b68e1a6](https://github.com/Revnoplex/ayt-api/commit/b68e1a6079832f3b0044b71e667a913adc58c667))

### Fixed
- Outdated use of old attribute `banner_external_url` in [channel example](examples/channel.py). 
([2a0c7bd](https://github.com/Revnoplex/ayt-api/commit/2a0c7bd3d81c94c7650c389839fecf25c7c181f4))
- API keys in urls passed when after calling the api are always censored. 
([cbc1514](https://github.com/Revnoplex/ayt-api/commit/cbc1514a1930d65b54f5e3a62433fc7487a92911)) 
- Broken attributes of `AuthorisedYoutubeVideo`. 
([b7a188d#diff-7363042](https://github.com/Revnoplex/ayt-api/commit/b7a188de98f9d5f1667f5ff63a0c3d52d5818374#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834))
- `YoutubeChannel.likes_id` returning an invalid ID. 
([90e1ad1#diff-7363042-L1420](https://github.com/Revnoplex/ayt-api/commit/90e1ad16e10a38b37fa9b78b4249acb7843f9f14#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834L1420))
- `VideoStream` and `AudioStream` raising errors when certain values weren't set. 
([10881c0](https://github.com/Revnoplex/ayt-api/commit/10881c08f8689da24cf2cc4062c7c15aa2240dbf))
- `HTTPException` raising its own error when `error_data` is `None`. 
([2b3b18a](https://github.com/Revnoplex/ayt-api/commit/2b3b18afd76a0b962d9aec5d0b44fab4127768fc)) 
- Getting `file_name` in `AuthorisedYoutubeVideo` failing as it is sometimes not set.
([eacf5cb](https://github.com/Revnoplex/ayt-api/commit/eacf5cb731a7611a86c598d846f95a855ec13a64))
- *Documentation*: Updated old instances of class names still in documentation.
([e41fd3b](https://github.com/Revnoplex/ayt-api/commit/e41fd3b759ee24d30846ccc09b0eb2adf5617d39))
- *Documentation*: Formatting error in docstring for `exceptions.APITimeout`. 
([9ac4776](https://github.com/Revnoplex/ayt-api/commit/9ac4776e7b2c9759a26c1d2371f8dc35f15a3674))
- *Documentation*: wrong term used in `YoutubeBanner`. 
([e4ca4c3](https://github.com/Revnoplex/ayt-api/commit/e4ca4c3a6a14ab0d8a77a9c094e59c373a7e34cd))

### Changed
- **Breaking**: Renamed attribute `_type` to `kind` in `filters.SearchFilter`. 
([7a60e71](https://github.com/Revnoplex/ayt-api/commit/7a60e71289bafe78a9a44516f852d4a1553da009))
- **Breaking**: `PlaylistItem.id` is now the actual item ID and the video ID is now `PlaylistItem.video_id`. 
([d50d852](https://github.com/Revnoplex/ayt-api/commit/d50d8529e3d4162255f4f5c512de568d0da79dbc))
- `AsyncYoutubeAPI` can now raise `NoAuth` if no API key or OAuth token is provided. 
([b7a188d#diff-cbbc953-R47](https://github.com/Revnoplex/ayt-api/commit/b7a188de98f9d5f1667f5ff63a0c3d52d5818374#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R47))
- `fetch_video()` can now return a superclass of `YoutubeVideo`: `AuthorisedYoutubeVideo`. 
([b7a188d#diff-cbbc953-R334](https://github.com/Revnoplex/ayt-api/commit/b7a188de98f9d5f1667f5ff63a0c3d52d5818374#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R334))
- OAuth token is used if no API key is provided. 
([90e1ad1#diff-cbbc953-R92](https://github.com/Revnoplex/ayt-api/commit/90e1ad16e10a38b37fa9b78b4249acb7843f9f14#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R92))
- `InvalidKey` now inherits from the new class `AuthException`.
([fedeb89#diff-3f857ff-R174](https://github.com/Revnoplex/ayt-api/commit/fedeb89a67e1455ccef0c5337dfd21f4523f314b#diff-3f857ff3ed9ca4dc99077beeb478c3f68371dbbfa6b84ede9fd9f3d47d72b788R174))
- `YoutubeVideo` attribute `made_for_kids` can now be `None`. 
([4bfb5d1#diff-7363042-L744](https://github.com/Revnoplex/ayt-api/commit/4bfb5d1409ca2fe4092efce070f52d4326608d05#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834L744))
- `extract_video_id` supports all `*.ytimg.com` urls. 
([5cda291](https://github.com/Revnoplex/ayt-api/commit/5cda2915bc3f7d75bef3429342929cfab23967e7))
- *Documentation*: `__init__` docstring included in `AsyncYoutubeAPI` class. 
([3af95cd](https://github.com/Revnoplex/ayt-api/commit/3af95cd89ba922de30ef7070f3b9811636851075))

## [0.3.0] - 2024-10-12

**BREAKING CHANGES.** See *Changed* and *Removed* for details.

**This Version Drops Python 3.7 Support**

### Added

- Alias of `YoutubeThumbnail.resolution`: `YoutubeThumbnail.size`.
([7e10db5#diff-7363042-R35](https://github.com/Revnoplex/ayt-api/commit/7e10db574dab18f977aa41ba80c9a4080c67e1ea#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834R35))
- Method to get the name of the highest resolution available.
([7e10db5#diff-7363042-R65](https://github.com/Revnoplex/ayt-api/commit/7e10db574dab18f977aa41ba80c9a4080c67e1ea#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834R65))
- Property that returns the highest quality available thumbnail.
([7e10db5#diff-7363042-R79](https://github.com/Revnoplex/ayt-api/commit/7e10db574dab18f977aa41ba80c9a4080c67e1ea#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834R79))
- Methods to download thumbnails.
([31ed8ab](https://github.com/Revnoplex/ayt-api/commit/31ed8abdf3415b8177b66f75c9067be38f93f4a4))
- Python 3.13 Support.
([7b8f9ed#diff-50c86b7-R23](https://github.com/Revnoplex/ayt-api/commit/7b8f9eddc12e05365a73c5638d8efb5a7007d6a2#diff-50c86b7ed8ac2cf95bd48334961bf0530cdc77b5a56f852c5c61b89d735fd711R23))
- Alias of the `highlight_url` attribute for both `YoutubeComment` and `YoutubeComment`: `url`.
([c3baa03](https://github.com/Revnoplex/ayt-api/commit/c3baa03abdd4a021a4bb42da4252f92c1438b1df))
- 3 Aliases of `YoutubeChannel.thumbnails`: `icon`, `pfp` and `avatar`. 
([eb331c0](https://github.com/Revnoplex/ayt-api/commit/eb331c060639ea667de7985e410c699a908fa2e6))
- New 'banner' classes and methods simular to thumbnails, but for YouTube channel banners.
([6f8ec58](https://github.com/Revnoplex/ayt-api/commit/6f8ec58d4e46c45d2256ada7fb141e15870e4347))
- This changelog. ([42e5289](https://github.com/Revnoplex/ayt-api/commit/42e5289b6b968926644807c2d69062fb889ef465))
- Alias of `utils.censor_key`: `censor_token`.
([1874580#diff-920c31e-R197](https://github.com/Revnoplex/ayt-api/commit/1874580a085429f8533742acefd1b4ca4aac20bb#diff-920c31e8df6efd41a120b70811f3494522b1587fe3bd4cc389823cb5b004e407R197))
- Basic Unit Tests. 
([689c84f](https://github.com/Revnoplex/ayt-api/commit/689c84f62b03592b3612f9e246cd28afd3db572a))
- Search Example.
([e0678f0](https://github.com/Revnoplex/ayt-api/commit/e0678f01dcd510a05cdf96d6b611a2234b315b97))
- *Documentation*: Add additional badges to [README.md](README.md).
([fb06062](https://github.com/Revnoplex/ayt-api/commit/fb060623b20d74767059ef3153e18ff72ba74011))
- *Documentation*: Documented the limitations of `YoutubeComment` attributes. 
([9eb2919](https://github.com/Revnoplex/ayt-api/commit/9eb2919d327090c640d79336864ac9cb2d851005))


### Changed

- **Breaking**: The equivalent of `YoutubeChannel.banner_external_url` is now `YoutubeChannel.banner_external.url`.
([6f8ec58#diff-7363042-L1408](https://github.com/Revnoplex/ayt-api/commit/6f8ec58d4e46c45d2256ada7fb141e15870e4347#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834L1408))
- Updated the description of this project.
([2d0d274](https://github.com/Revnoplex/ayt-api/commit/2d0d27421f770fb9242f1f03626160d0b4399973), 
[6d4bac0](https://github.com/Revnoplex/ayt-api/commit/6d4bac01f7c61524615c34d78da820c2e7a2a646), 
[8caf94d](https://github.com/Revnoplex/ayt-api/commit/8caf94d58734912ce8e096b8ded5083c538e4545))
- Replaced instances of if-pass statements for simplified statements.
([bff7763](https://github.com/Revnoplex/ayt-api/commit/bff77633fbc2b12814045a08ba59674b0ca7be4e))
- `YoutubeThumbnailMetadata.available` is a `tuple`.
([7e10db5#diff-7363042-R56](https://github.com/Revnoplex/ayt-api/commit/7e10db574dab18f977aa41ba80c9a4080c67e1ea#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834R56))
- Permit any http code returned from the API under 400. 
([5bb8a23](https://github.com/Revnoplex/ayt-api/commit/5bb8a23f8e09268828a8fd20e46fe57d3285861e))
- Renamed `utils.censor_token` to `censor_key`
([1874580#diff-920c31e-L180](https://github.com/Revnoplex/ayt-api/commit/1874580a085429f8533742acefd1b4ca4aac20bb#diff-920c31e8df6efd41a120b70811f3494522b1587fe3bd4cc389823cb5b004e407L180))

### Fixed

- *Documentation*: Missing closing square bracket. 
([85678be](https://github.com/Revnoplex/ayt-api/commit/85678be945266008b0c7007725b3bb748622f13d))

### Removed

- **Breaking**: Python 3.7 support
([7b8f9ed](https://github.com/Revnoplex/ayt-api/commit/7b8f9eddc12e05365a73c5638d8efb5a7007d6a2))

## [0.2.1] - 2024-02-13

**BREAKING CHANGES.** See *Changed* for details.

### Added

- Added `exclude` parameter to `fetch_playlist_videos` which allows excluding certain videos from a result. 
This is useful when certain videos in a playlist are not found and you just wan't the available videos 
([878d5cb](https://github.com/Revnoplex/ayt-api/commit/878d5cbcb82b4e56cffaa341782c5a13c29392a3), 
[498ac9d](https://github.com/Revnoplex/ayt-api/commit/498ac9dd18ef814f7e6b98b8b47c638d2fae7dd2))

### Fixed

- Fixed an unhanded enum type `privacyStatusUnspecified` being passed to the enum `PrivacyStatus` 
([56207bb](https://github.com/Revnoplex/ayt-api/commit/56207bb0e967f0609190268ae248fe018e610aa9))
- Added proper types to `*NotFound` exceptions to reflect multiple requested items being not found since version 0.2.0
([b198ce1](https://github.com/Revnoplex/ayt-api/commit/b198ce1e399cfc87c4d8330950e953f3ccff230c))

### Changed

- **Breaking**: Renamed `AsyncYoutubeApi` back to `AsyncYoutubeAPI`. I will try not to change it again to 
keep things consistant ([2806395](https://github.com/Revnoplex/ayt-api/commit/2806395b6cbf69274e30ab776707517ef99fd544))

## [0.2.0.post2] - 2023-11-26

**BREAKING CHANGES.** See *Changed* for details.

### Added

- Added call functions, classes and exceptions for channels, comments and captions. 
([d0111a0](https://github.com/Revnoplex/ayt-api/commit/d0111a00ef4f201d4d8ba66598e52119f20309e4), 
[3a183ed](https://github.com/Revnoplex/ayt-api/commit/3a183edc389b9caebb4c22abfb174b1cb2a9158b), 
[186dcf8](https://github.com/Revnoplex/ayt-api/commit/186dcf8993273e36687d6cd99c08e9202389e752))
- Added API search function. 
([b6e4f92#diff-cbbc953-R305](https://github.com/Revnoplex/ayt-api/commit/b6e4f923699fd53e83604f4ec3ea8230c2b39eea#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R305))
- Added new utils to extract comment and channel IDs from URLs. 
([3a183ed#diff-920c31e](https://github.com/Revnoplex/ayt-api/commit/3a183edc389b9caebb4c22abfb174b1cb2a9158b#diff-920c31e8df6efd41a120b70811f3494522b1587fe3bd4cc389823cb5b004e407R48), 
[3a183ed#diff-0b0befd](https://github.com/Revnoplex/ayt-api/commit/3a183edc389b9caebb4c22abfb174b1cb2a9158b#diff-0b0befde3d2ae16c69bc3720a35e6e9e32990954abd211a7ee90c783f5972d66), 
[18973f6](https://github.com/Revnoplex/ayt-api/commit/18973f6aaae0f3f53cee3833af931bcf2fedd927))
- Added util to convert YouTube ids to integers. 
([83e6b9f](https://github.com/Revnoplex/ayt-api/commit/83e6b9f7eb63e6e217628f86df32665f7b0cfcd9),
[28605f0](https://github.com/Revnoplex/ayt-api/commit/28605f0c1d1f2cb5255e3fd2231f1e14783b0df7))
- Added utils to convert between camel case and snake case conventions. 
([2f5888c#diff-920c31e-R66](https://github.com/Revnoplex/ayt-api/commit/2f5888cb2dc89264930e025516969b3b7bb786a7#diff-920c31e8df6efd41a120b70811f3494522b1587fe3bd4cc389823cb5b004e407R66),
[85f8324](https://github.com/Revnoplex/ayt-api/commit/85f83248182de34ad670d00a41b4462fe18a5a0d))
- Added util to convert keys in dictionary from camel case to snake case. 
([2f5888c#diff-920c31e-R76](https://github.com/Revnoplex/ayt-api/commit/2f5888cb2dc89264930e025516969b3b7bb786a7#diff-920c31e8df6efd41a120b70811f3494522b1587fe3bd4cc389823cb5b004e407R76))
- Added util to censor token in call URLs. 
([dbde429](https://github.com/Revnoplex/ayt-api/commit/dbde4291ede6bd94555a96ba9781f1db5f2fa53a))
- Added enums for multi-return type attributes. 
([c2330d7#diff-bb27b51](https://github.com/Revnoplex/ayt-api/commit/c2330d7390bdca2d5a1890b428eab25db6dc5c05#diff-bb27b5198906dc8e1c04883def234a5863bba538bf4e28016ca200067960a515))
- Added special `SearchFilter` class for the new search function.
([e6e17d2](https://github.com/Revnoplex/ayt-api/commit/e6e17d21bbc956c9f609109a133e34797c2c030a))
- Added enums for multi-arg type attributes for `SearchFilter`. 
([c2330d7#diff-43ae858](https://github.com/Revnoplex/ayt-api/commit/c2330d7390bdca2d5a1890b428eab25db6dc5c05#diff-43ae858b4a3061ab4b2fd78482b49debf32f5eeaf711ec7abd33afe06fb6f742))

### Changed

- **Breaking**: Renamed `AsyncYoutubeAPI` to `AsyncYoutubeApi`. 
([c2330d7#diff-cbbc953](https://github.com/Revnoplex/ayt-api/commit/c2330d7390bdca2d5a1890b428eab25db6dc5c05#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1L15))
- **Breaking**: Renamed `get_playlist_metadata()` to `fetch_playlist()`.
([873c5a3#diff-cbbc953-L38](https://github.com/Revnoplex/ayt-api/commit/873c5a3432100103527e4da88b4866e2dc1f7dd0#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1L38),
[192eceb#diff-cbbc953-L38](https://github.com/Revnoplex/ayt-api/commit/192eceb68cf78d3053a44bd69991699d77a3fbcd#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1L38))
- **Breaking**: Split `get_videos_from_playlist()` into `fetch_playlist_items()` and `fetch_playlist_videos()`. 
([192eceb#diff-cbbc953-L85](https://github.com/Revnoplex/ayt-api/commit/192eceb68cf78d3053a44bd69991699d77a3fbcd#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1L85),
[192eceb#diff-cbbc953-R164](https://github.com/Revnoplex/ayt-api/commit/192eceb68cf78d3053a44bd69991699d77a3fbcd#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R164))
- **Breaking**: Renamed `get_video_metadata()` to `fetch_video()`.
([873c5a3#diff-cbbc953-L141](https://github.com/Revnoplex/ayt-api/commit/873c5a3432100103527e4da88b4866e2dc1f7dd0#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1L141))
- **Breaking**: Renamed `YoutubeVideoMetadata` to `YoutubeVideo` 
([873c5a3#diff-7363042-L415](https://github.com/Revnoplex/ayt-api/commit/873c5a3432100103527e4da88b4866e2dc1f7dd0#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834L415))
- **Breaking**: Renamed `PlaylistVideoMetadata` to `PlaylistItem` 
([873c5a3#diff-7363042-L713](https://github.com/Revnoplex/ayt-api/commit/873c5a3432100103527e4da88b4866e2dc1f7dd0#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834L713),
[192eceb#diff-7363042-R713](https://github.com/Revnoplex/ayt-api/commit/192eceb68cf78d3053a44bd69991699d77a3fbcd#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834R713))
- **Breaking**: Renamed `YoutubePlaylistMetadata` to `YoutubePlaylist` 
([192eceb#diff-7363042-L855](https://github.com/Revnoplex/ayt-api/commit/192eceb68cf78d3053a44bd69991699d77a3fbcd#diff-7363042fe6cc65ba3e9f2acdac65360c72c53676f992cc7195e04a9204da5834L855))
- All call functions use a single function to prevent duplicate code. 
([192eceb#diff-cbbc953-R39](https://github.com/Revnoplex/ayt-api/commit/192eceb68cf78d3053a44bd69991699d77a3fbcd#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R39))
- Some call functions support multiple IDs as arguments. 
([192eceb](https://github.com/Revnoplex/ayt-api/commit/192eceb68cf78d3053a44bd69991699d77a3fbcd))
- The api token query in the call_url is now censored. 
([b6e4f92#diff-cbbc953-R105](https://github.com/Revnoplex/ayt-api/commit/b6e4f923699fd53e83604f4ec3ea8230c2b39eea#diff-cbbc9533070ebb35c5c5d3abc0167a4019be28b3906a0fa2ff36eba0f64b01f1R105))

### Fixed

- **Correction**: Fixed outdated examples 
([36e25cd](https://github.com/Revnoplex/ayt-api/commit/36e25cd00249957c408874e68d9b0d91a754c4f0))
- **Correction**: Updated examples in `README.md` 
([94ae2e3](https://github.com/Revnoplex/ayt-api/commit/94ae2e371b14a21bd3bf5e27e2967fd4a17342c6))

## [0.1.6] - 2023-09-13

### Fixed

- Chapter names no longer have a trailing set of brackets if they surrounded the timestamp
([b22dcbe](https://github.com/Revnoplex/ayt-api/commit/b22dcbe67d66991317eb4fde5bd2b584ba2c9938))

## [0.1.5] - 2023-08-07

### Fixed

- Fixed a bug where trailing spaces followed by trailing hyphens would not be stripped 
([c95fa11](https://github.com/Revnoplex/ayt-api/commit/c95fa11c3be619da3b260ccad6d27721bae29cb1))

## [0.1.4] - 2023-07-20

### Fixed

- Fixed unintended behaviour where the id extractor functions would return the path of the url instead of `None` when passing an invalid url. 
([3374b96](https://github.com/Revnoplex/ayt-api/commit/3374b96d1b8ec6ece007a442990783007d35c4db))
- Fixed bad type hints for `extract_video_id` and `extract_playlist_id`: changed the type from `str` to `Optional[str]`
([3374b96](https://github.com/Revnoplex/ayt-api/commit/3374b96d1b8ec6ece007a442990783007d35c4db))

## [0.1.3] - 2023-07-18

### Added

- Added a list of test playlist urls to parse
([417719c](https://github.com/Revnoplex/ayt-api/commit/417719c8b6bfe31356d69700ce74e8bb8849c530))
- Added playlist id parsing
([e5965da#diff-920c31e-R28](https://github.com/Revnoplex/ayt-api/commit/e5965da29c4d0bc0178220f24a98da9f7b57d61f#diff-920c31e8df6efd41a120b70811f3494522b1587fe3bd4cc389823cb5b004e407R28))
- Added chapter parsing with new `VideoChapter` class and other related helper functions 
([875c82d](https://github.com/Revnoplex/ayt-api/commit/875c82dbfcbf37ed33aa2bdea8fbf8d79151fe0d))

### Changed

- Reworked video id parsing with `urllib.parse` library
([e5965da#diff-920c31e-L1](https://github.com/Revnoplex/ayt-api/commit/e5965da29c4d0bc0178220f24a98da9f7b57d61f#diff-920c31e8df6efd41a120b70811f3494522b1587fe3bd4cc389823cb5b004e407L1))
- Converted Some classes to dataclasses
([875c82d](https://github.com/Revnoplex/ayt-api/commit/875c82dbfcbf37ed33aa2bdea8fbf8d79151fe0d))
- Updated internal documentation
([875c82d](https://github.com/Revnoplex/ayt-api/commit/875c82dbfcbf37ed33aa2bdea8fbf8d79151fe0d))

## [0.1.2] - 2023-06-17

Too old to list changes

## [0.1.1] - 2022-10-28

Too old to list changes

## [0.1.0] - 2022-05-26

Too old to list changes

[unreleased]: https://github.com/Revnoplex/ayt-api/compare/v0.4.0...main
[0.4.0]: https://github.com/Revnoplex/ayt-api/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Revnoplex/ayt-api/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/Revnoplex/ayt-api/compare/v0.2.0.post2...v0.2.1
[0.2.0.post2]: https://github.com/Revnoplex/ayt-api/compare/v0.1.6...v0.2.0.post2
[0.1.6]: https://github.com/Revnoplex/ayt-api/compare/v0.1.5...v0.1.6
[0.1.5]: https://github.com/Revnoplex/ayt-api/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/Revnoplex/ayt-api/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/Revnoplex/ayt-api/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/Revnoplex/ayt-api/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/Revnoplex/ayt-api/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Revnoplex/ayt-api/commits/v0.1.0