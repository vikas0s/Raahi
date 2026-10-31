"""
SQLAlchemy ORM models for Raahi Transit Platform.
Implements the relational transit network schema:
- User
- City
- TransitAgency
- Station
- Route
- Trip
- StopTime
- CalendarService
- SavedJourney
- SavedPlace
- UserPreference
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from .connection import Base


def _utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    email = Column(String(256), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=_utc_now)

    saved_journeys = relationship("SavedJourney", back_populates="user", cascade="all, delete-orphan")
    saved_places = relationship("SavedPlace", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")


class City(Base):
    __tablename__ = "cities"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    country = Column(String(64), default="India")
    timezone = Column(String(64), default="Asia/Kolkata")
    center_lat = Column(Float, nullable=True)
    center_lon = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)

    stations = relationship("Station", back_populates="city")
    agencies = relationship("TransitAgency", back_populates="city")


class TransitAgency(Base):
    __tablename__ = "transit_agencies"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    city_id = Column(String(64), ForeignKey("cities.id"), nullable=False)
    source = Column(String(64), default="official")
    active_status = Column(String(32), default="active")

    city = relationship("City", back_populates="agencies")
    routes = relationship("Route", back_populates="agency")


class Station(Base):
    __tablename__ = "stations"

    id = Column(String(64), primary_key=True)
    external_stop_id = Column(String(64), nullable=True, index=True)
    city_id = Column(String(64), ForeignKey("cities.id"), nullable=False, index=True)
    name = Column(String(256), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    stop_type = Column(String(64), default="metro_station")
    source = Column(String(64), default="places_catalog")
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)

    city = relationship("City", back_populates="stations")
    stop_times = relationship("StopTime", back_populates="station")


class Route(Base):
    __tablename__ = "routes"

    id = Column(String(128), primary_key=True)
    external_route_id = Column(String(64), nullable=True, index=True)
    agency_id = Column(String(64), ForeignKey("transit_agencies.id"), nullable=False, index=True)
    city_id = Column(String(64), ForeignKey("cities.id"), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    route_type = Column(String(64), default="suburban_rail")
    line_color = Column(String(32), nullable=True)
    source = Column(String(64), default="ir_railradar")

    agency = relationship("TransitAgency", back_populates="routes")
    trips = relationship("Trip", back_populates="route", cascade="all, delete-orphan")


class CalendarService(Base):
    __tablename__ = "calendar_services"

    service_id = Column(String(64), primary_key=True)
    operating_days = Column(String(64), default="Mon,Tue,Wed,Thu,Fri,Sat,Sun")
    start_date = Column(String(32), default="2026-01-01")
    end_date = Column(String(32), default="2026-12-31")
    exceptions = Column(Text, nullable=True)

    trips = relationship("Trip", back_populates="service")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(String(128), primary_key=True)
    external_trip_id = Column(String(64), nullable=True, index=True)
    route_id = Column(String(128), ForeignKey("routes.id"), nullable=False, index=True)
    service_id = Column(String(64), ForeignKey("calendar_services.service_id"), nullable=False)
    trip_headsign = Column(String(256), nullable=True)
    direction_id = Column(Integer, default=0)

    route = relationship("Route", back_populates="trips")
    service = relationship("CalendarService", back_populates="trips")
    stop_times = relationship("StopTime", back_populates="trip", cascade="all, delete-orphan")


class StopTime(Base):
    __tablename__ = "stop_times"

    id = Column(String(128), primary_key=True)
    trip_id = Column(String(128), ForeignKey("trips.id"), nullable=False, index=True)
    stop_id = Column(String(64), ForeignKey("stations.id"), nullable=False, index=True)
    stop_sequence = Column(Integer, nullable=False)
    arrival_time = Column(String(16), nullable=False)
    departure_time = Column(String(16), nullable=False)

    trip = relationship("Trip", back_populates="stop_times")
    station = relationship("Station", back_populates="stop_times")


class SavedJourney(Base):
    __tablename__ = "saved_journeys"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=True, index=True)
    name = Column(String(256), nullable=False)
    origin = Column(String(256), nullable=False)
    destination = Column(String(256), nullable=False)
    city = Column(String(128), nullable=False)
    preferred_mode = Column(String(64), default="fastest")
    typical_duration_minutes = Column(Integer, default=30)
    typical_fare_inr = Column(Float, default=50.0)
    typical_transfers = Column(Integer, default=0)
    current_delay_minutes = Column(Integer, default=0)
    active_status = Column(String(64), default="Normal Service")
    created_at = Column(String(64), default=lambda: datetime.now(timezone.utc).isoformat())

    user = relationship("User", back_populates="saved_journeys")


class SavedPlace(Base):
    __tablename__ = "saved_places"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=True, index=True)
    name = Column(String(128), nullable=False)
    address = Column(String(512), nullable=True)
    category = Column(String(64), default="other")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    city = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=_utc_now)

    user = relationship("User", back_populates="saved_places")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id"), unique=True, nullable=False)
    preferred_language = Column(String(16), default="en")
    selected_city = Column(String(128), default="Delhi NCR")
    accessible_only = Column(Boolean, default=False)
    reduced_motion = Column(Boolean, default=False)
    travel_preferences_json = Column(Text, default='{"fastest": true, "cheapest": false}')

    user = relationship("User", back_populates="preferences")
