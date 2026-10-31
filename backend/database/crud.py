"""
Database CRUD helper functions for Raahi Transit Platform.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import (
    User, City, TransitAgency, Station, Route, Trip, StopTime,
    CalendarService, SavedJourney, SavedPlace, UserPreference
)


def get_user(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_active_cities(db: Session) -> List[City]:
    return db.query(City).filter(City.is_active == True).all()


def get_stations_by_city(db: Session, city_id: str) -> List[Station]:
    return db.query(Station).filter(Station.city_id == city_id).all()


def get_saved_journeys(db: Session, user_id: str) -> List[SavedJourney]:
    return db.query(SavedJourney).filter(SavedJourney.user_id == user_id).all()


def get_saved_places(db: Session, user_id: str) -> List[SavedPlace]:
    return db.query(SavedPlace).filter(SavedPlace.user_id == user_id).all()


def get_user_preferences(db: Session, user_id: str) -> Optional[UserPreference]:
    return db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
