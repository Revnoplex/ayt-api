import ayt_api
import asyncio


async def oauth2_auth_code_example():
    api = ayt_api.AsyncYoutubeAPI(oauth_token="Your OAuth2 Token")
    resource = await api.fetch_video("Video ID", True)
    print(resource.file_name)


asyncio.run(oauth2_auth_code_example())
