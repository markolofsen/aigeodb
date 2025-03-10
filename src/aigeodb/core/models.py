from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    iso3 = Column(String(3))
    numeric_code = Column(String(3))
    iso2 = Column(String(2))
    phonecode = Column(String(255))
    capital = Column(String(255))
    currency = Column(String(255))
    currency_name = Column(String(255))
    currency_symbol = Column(String(255))
    tld = Column(String(255))
    native = Column(String(255))
    region = Column(String(255))
    region_id = Column(Integer)
    subregion = Column(String(255))
    subregion_id = Column(Integer)
    nationality = Column(String(255))
    timezones = Column(Text)
    translations = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    emoji = Column(String(191))
    emojiU = Column(String(191))
    created_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow)
    flag = Column(Boolean, default=True)
    wikiDataId = Column(String(255))

    # Relationships
    states = relationship("State", back_populates="country")
    cities = relationship("City", back_populates="country")


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    translations = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow)
    flag = Column(Boolean, default=True)
    wikiDataId = Column(String(255))

    # Relationships
    subregions = relationship("Subregion", back_populates="region")


class Subregion(Base):
    __tablename__ = "subregions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    translations = Column(Text)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow)
    flag = Column(Boolean, default=True)
    wikiDataId = Column(String(255))

    # Relationships
    region = relationship("Region", back_populates="subregions")


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    country_code = Column(String(2), nullable=False)
    fips_code = Column(String(255))
    iso2 = Column(String(255))
    type = Column(String(191))
    level = Column(Integer)
    parent_id = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow)
    flag = Column(Boolean, default=True)
    wikiDataId = Column(String(255))

    # Relationships
    country = relationship("Country", back_populates="states")
    cities = relationship("City", back_populates="state")


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    state_code = Column(String(255), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    country_code = Column(String(2), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    flag = Column(Boolean, default=True)
    wikiDataId = Column(String(255))

    # Relationships
    country = relationship("Country", back_populates="cities")
    state = relationship("State", back_populates="cities")
