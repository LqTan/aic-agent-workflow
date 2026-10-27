from __future__ import annotations

import csv
import logging
from pathlib import Path

from sqlmodel import Session, select

from app.shared.db.models import KeyframeORM

logger = logging.getLogger(__name__)


def import_manifest_to_db(
    manifest_path: Path | str,
    session: Session,
    *,
    batch_size: int = 1000,
    overwrite: bool = False,
) -> int:
    """Import ``manifest.csv`` rows into the ``keyframes`` table in PostgreSQL/database.

    Returns the number of keyframes imported.
    """
    manifest_path = Path(manifest_path).resolve()
    if not manifest_path.is_file():
        logger.warning("Manifest file not found: %s", manifest_path)
        return 0

    # If keyframes table already has data and overwrite is False, skip
    existing_count = session.exec(select(KeyframeORM)).first()
    if existing_count is not None and not overwrite:
        logger.info("keyframes table already contains records. Skipping import.")
        return 0

    if overwrite:
        # Delete existing records if overwriting
        for item in session.exec(select(KeyframeORM)).all():
            session.delete(item)
        session.commit()

    records_to_insert: list[KeyframeORM] = []
    total_imported = 0

    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                record = KeyframeORM(
                    keyframe_id=row["keyframe_id"].strip(),
                    collection_id=row["collection_id"].strip().upper(),
                    video_id=row["video_id"].strip(),
                    keyframe_number=int(row.get("keyframe_number") or 0),
                    clip_vector_index=int(row.get("clip_vector_index") or 0),
                    frame_number=int(row["frame_number"]),
                    timestamp_ms=int(row["timestamp_ms"]),
                    image_path=row["image_path"].strip(),
                    video_path=row.get("video_path", "").strip(),
                )
                records_to_insert.append(record)
            except (KeyError, ValueError) as exc:
                logger.warning("Skipping invalid manifest row %s: %s", row, exc)

            if len(records_to_insert) >= batch_size:
                session.add_all(records_to_insert)
                session.commit()
                total_imported += len(records_to_insert)
                records_to_insert.clear()

    if records_to_insert:
        session.add_all(records_to_insert)
        session.commit()
        total_imported += len(records_to_insert)

    logger.info("Successfully imported %d keyframes into database from %s", total_imported, manifest_path)
    return total_imported

