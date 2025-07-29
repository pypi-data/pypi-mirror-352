"""Models for basho data."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class RikishiPrize(BaseModel):
    """Model representing a rikishi who won a prize."""

    type: str
    rikishi_id: int = Field(alias="rikishiId")
    shikona_en: str = Field(alias="shikonaEn")
    shikona_jp: str = Field(alias="shikonaJp")


class Basho(BaseModel):
    """Model representing a basho tournament."""

    date: str  # YYYYMM format
    location: str
    start_date: datetime = Field(alias="startDate")
    end_date: datetime = Field(alias="endDate")
    yusho: List[RikishiPrize]  # Tournament winners for each division
    special_prizes: List[RikishiPrize] = Field(
        alias="specialPrizes"
    )  # Special prizes (sansho)
