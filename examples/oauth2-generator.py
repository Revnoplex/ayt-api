import ayt_api
import asyncio


async def oauth2_generator_example():
    api = None
    async for stage in ayt_api.AsyncYoutubeAPI.with_oauth_flow_generator("Your Client ID", "Your Client Secret"):
        if isinstance(stage, str):
            # prints the oauth consent url
            print(stage)
            continue
        # stage is now an AscyncYoutubeAPI object that is assigned to api
        api = stage
    if api:
        resource = await api.fetch_video("Video ID", authorised=True)
        print(resource.file_name)


asyncio.run(oauth2_generator_example())
