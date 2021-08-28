from sqlalchemy import Column, String, Integer

from config.database import Base


class YoutubeVideo(Base):
    __tablename__ = 'youtube_video'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, nullable=False)

    title = Column(String, nullable=True)

    def __repr__(self):
        return self.title
