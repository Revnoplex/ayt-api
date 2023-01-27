def strip_video_id(url: str) -> str:
    """supported urls:
    https://www.youtube.com/watch?v=ID

    https://www.youtube.com/v/ID

    https://youtu.be/ID"
    Args:
        url (str): The url to strip the id from
    Returns:
        str: The video id with the rest of the url removed
    """
    if url.split('/')[2] == 'youtu.be':
        return url.split('/')[3].split("?")[0].split('&')[0]
    else:
        slash_index = 4 if url.split("/")[3] == "v" or url.split("/")[3] == "embed" else 3
        return url.split("/")[slash_index].replace("watch?v=", "").split("&")[0].split("?")[0]
