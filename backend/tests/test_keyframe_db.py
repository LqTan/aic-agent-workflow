from __future__ import annotations

from pathlib import Path

from sqlmodel import Session, select

from app.features.data_pipeline.importer import import_manifest_to_db
from app.shared.db.models import KeyframeORM
from app.shared.db.session import get_engine, init_engine
from app.core.config import get_settings


def test_import_manifest_to_db(tmp_path: Path):
    # Create a small sample manifest
    csv_file = tmp_path / "manifest.csv"
    csv_file.write_text(
        "keyframe_id,collection_id,video_id,keyframe_number,clip_vector_index,frame_number,timestamp_ms,image_path,video_path\n"
        "L21_V001_000001,L21,L21_V001,1,0,0,0,keyframes/L21_V001/001.jpg,videos/L21_V001.mp4\n"
        "L21_V001_000002,L21,L21_V001,2,1,90,3000,keyframes/L21_V001/002.jpg,videos/L21_V001.mp4\n",
        encoding="utf-8",
    )

    settings = get_settings()
    engine = init_engine(settings)
    with Session(engine) as session:
        imported = import_manifest_to_db(csv_file, session, overwrite=True)
        assert imported == 2

        records = session.exec(select(KeyframeORM)).all()
        assert len(records) == 2
        assert records[0].keyframe_id == "L21_V001_000001"
        assert records[0].collection_id == "L21"
        assert records[0].video_id == "L21_V001"
        assert records[1].timestamp_ms == 3000

