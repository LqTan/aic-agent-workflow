from __future__ import annotations

from sqlmodel import Field, SQLModel


class KeyframeORM(SQLModel, table=True):
    __tablename__ = "keyframes"

    keyframe_id: str = Field(primary_key=True, max_length=64)
    collection_id: str = Field(max_length=32, index=True)
    video_id: str = Field(max_length=64, index=True)
    keyframe_number: int = Field(default=0)
    clip_vector_index: int = Field(default=0, index=True)
    frame_number: int = Field(default=0)
    timestamp_ms: int = Field(default=0, index=True)
    image_path: str = Field(max_length=255)
    video_path: str = Field(default="", max_length=255)

