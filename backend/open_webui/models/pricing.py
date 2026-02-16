import time
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, Float, Text

from open_webui.internal.db import Base, JSONField, get_db_context


class ModelPricing(Base):
    __tablename__ = "model_pricing"

    model_id = Column(Text, primary_key=True)
    provider = Column(Text)
    input_usd_per_million = Column(Float)
    output_usd_per_million = Column(Float)
    context_window = Column(BigInteger, nullable=True)
    updated_at = Column(BigInteger)
    source = Column(Text)
    raw = Column(JSONField, nullable=True)


class ModelPricingModel(BaseModel):
    model_id: str
    provider: str
    input_usd_per_million: float
    output_usd_per_million: float
    context_window: Optional[int] = None
    updated_at: int
    source: str
    raw: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class PricingTable:
    def get_all(self, db=None):
        with get_db_context(db) as db:
            return db.query(ModelPricing).all()

    def get_by_ids(self, model_ids: list[str], db=None):
        if not model_ids:
            return []
        with get_db_context(db) as db:
            return db.query(ModelPricing).filter(ModelPricing.model_id.in_(model_ids)).all()

    def upsert(self, rows: list[dict], db=None):
        now = int(time.time())
        with get_db_context(db) as db:
            for row in rows:
                row["updated_at"] = now
                existing = (
                    db.query(ModelPricing)
                    .filter_by(model_id=row["model_id"])
                    .first()
                )
                if existing:
                    for key, value in row.items():
                        setattr(existing, key, value)
                else:
                    db.add(ModelPricing(**row))
            db.commit()
