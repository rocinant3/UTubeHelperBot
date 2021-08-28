
from googleapiclient.discovery import build


class YoutTubeClient:
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"

    def __init__(self, token: str):
        self.api_client = build(self.API_SERVICE_NAME, self.API_VERSION, developerKey=token)

    def get_video_meta(self, video_id: str):
        query = self.api_client.videos().list(
            id=video_id,
            part='snippet, recordingDetails, statistics'
        )

        return query.execute()
