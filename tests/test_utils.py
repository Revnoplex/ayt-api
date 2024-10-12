import unittest
from ayt_api import utils


class MyTestCase(unittest.TestCase):
    def test_basic_video_url(self):
        self.assertEqual(utils.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_abnormal_query_video_url(self):
        self.assertEqual(utils.extract_video_id("https://youtu.be/oTJRivZTMLs&feature=channel"), "oTJRivZTMLs")

    def test_encoded_video_url(self):
        self.assertEqual(
            utils.extract_video_id(
                "https://www.youtube.com/attribution_link?a=JdfC0C9V6ZI&u=%2Fwatch%3Fv%3DEhxJLojIE_o%26feature%3Dshare"
            ),
            "EhxJLojIE_o"
        )

    def test_query_playlist_url(self):
        self.assertEqual(
            utils.extract_playlist_id(
                "https://www.youtube.com/playlist?list=PLwZcI0zn-JheRhv7jIV5Dl6IJQTuHR5e-&query=value"
            ),
            "PLwZcI0zn-JheRhv7jIV5Dl6IJQTuHR5e-"
        )

    def test_video_playlist_url(self):
        self.assertEqual(
            utils.extract_playlist_id(
                "https://www.youtube.com/watch?v=NS8DPG62Fto&list=PLwZcI0zn-JheRhv7jIV5Dl6IJQTuHR5e-&index=87"
            ),
            "PLwZcI0zn-JheRhv7jIV5Dl6IJQTuHR5e-"
        )

    def test_encoded_playlist_url(self):
        self.assertEqual(
            utils.extract_playlist_id(
                "https://www.youtube.com/attribution_link?a=JdfC0C9V6ZI&u=%2Fplaylist%3Flist%3DPLwZcI0zn-JheRhv7jIV5Dl6"
                "IJQTuHR5e-%26feature%3Dshare"
            ),
            "PLwZcI0zn-JheRhv7jIV5Dl6IJQTuHR5e-"
        )

    def test_query_channel_url(self):
        self.assertEqual(
            utils.extract_channel_id(
                "https://www.youtube.com/channel/UC1VSDiiRQZRTbxNvWhIrJfw?query=value"
            ),
            "UC1VSDiiRQZRTbxNvWhIrJfw"
        )

    def test_encoded_channel_url(self):
        self.assertEqual(
            utils.extract_channel_id(
                "https://www.youtube.com/attribution_link?a=JdfC0C9V6ZI&u=%2Fchannel%2FUC1VSDiiRQZRTbxNvWhIrJfw"
            ),
            "UC1VSDiiRQZRTbxNvWhIrJfw"
        )

    def test_query_comment_url(self):
        self.assertEqual(
            utils.extract_comment_id(
                "https://www.youtube.com/watch?v=3TdMGwC2NDk&feature=channel&lc=UgxMlgSMOq5LGVTF-zV4AaABAg"
            ),
            "UgxMlgSMOq5LGVTF-zV4AaABAg"
        )

    def test_encoded_comment_url(self):
        self.assertEqual(
            utils.extract_comment_id(
                "https://www.youtube.com/attribution_link?a=JdfC0C9V6ZI&u=%2Fwatch%3Fv%3D3TdMGwC2NDk%26lc%3DUgxMlgSMOq5"
                "LGVTF-zV4AaABAg%26feature%3Dshare"
            ),
            "UgxMlgSMOq5LGVTF-zV4AaABAg"
        )

    def test_censor_key(self):
        censored_key = utils.censor_key(
            "https://www.googleapis.com/youtube/v3/videos?part=snippet%2Cstatus%2CcontentDetails%2Cstatistics%2Cplayer%"
            "2CtopicDetails%2CrecordingDetails%2CliveStreamingDetails%2Clocalizations&id=500hSKU1owg&maxResults=50&key="
            "IMAGINARY_TOKEN"
        )
        self.assertNotIn("IMAGINARY_TOKEN", censored_key)
        self.assertEqual(
            censored_key,
            "https://www.googleapis.com/youtube/v3/videos?part=snippet%2Cstatus%2CcontentDetails%2Cstatistics%2C"
            "player%2CtopicDetails%2CrecordingDetails%2CliveStreamingDetails%2Clocalizations&id=500hSKU1owg&maxResults="
            "50&key=API_KEY"
        )


if __name__ == '__main__':
    unittest.main()
