from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BaseDTO(BaseModel):
    class Config:
        populate_by_name = True


class CountryDTO(BaseDTO):
    id: int
    name: str
    iso3: Optional[str] = None
    numeric_code: Optional[str] = None
    iso2: Optional[str] = None
    phonecode: Optional[str] = None
    capital: Optional[str] = None
    currency: Optional[str] = None
    currency_name: Optional[str] = None
    currency_symbol: Optional[str] = None
    tld: Optional[str] = None
    native: Optional[str] = None
    region: Optional[str] = None
    region_id: Optional[int] = None
    subregion: Optional[str] = None
    subregion_id: Optional[int] = None
    nationality: Optional[str] = None
    timezones: Optional[str] = None
    translations: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    emoji: Optional[str] = None
    emoji_u: Optional[str] = Field(None, alias='emojiU')
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    flag: bool = True
    wiki_data_id: Optional[str] = Field(None, alias='wikiDataId')


class RegionDTO(BaseDTO):
    id: int
    name: str
    translations: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    flag: bool = True
    wiki_data_id: Optional[str] = Field(None, alias='wikiDataId')


class SubregionDTO(BaseDTO):
    id: int
    name: str
    translations: Optional[str] = None
    region_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    flag: bool = True
    wiki_data_id: Optional[str] = Field(None, alias='wikiDataId')


class StateDTO(BaseDTO):
    id: int
    name: str
    country_id: int = Field(alias='country')
    country_code: str
    fips_code: Optional[str] = None
    iso2: Optional[str] = None
    type: Optional[str] = None
    level: Optional[int] = None
    parent_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    flag: bool = True
    wiki_data_id: Optional[str] = Field(None, alias='wikiDataId')


class CityDTO(BaseDTO):
    id: int
    name: str
    state_id: int = Field(alias='state')
    state_code: str
    country_id: int = Field(alias='country')
    country_code: str
    latitude: float
    longitude: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    flag: bool = True
    wiki_data_id: Optional[str] = Field(None, alias='wikiDataId')
