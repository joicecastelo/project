# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 11:38:27
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-04-10 15:55:16

# generic imports
from sqlalchemy import Boolean, Column, ForeignKey, String, DateTime
from sqlalchemy import Integer

# custom imports
from database.database import Base


class TimePeriod(Base):
    __tablename__ = "TimePeriod"
    id = Column(Integer, primary_key=True, index=True)
    startDateTime = Column(DateTime)
    endDateTime = Column(DateTime)
    deleted = Column(Boolean, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.as_dict())


class Organization(Base):
    __tablename__ = "Organization"
    id = Column(Integer, primary_key=True, index=True)
    href = Column(String)
    isHeadOffice = Column(Boolean)
    isLegalEntity = Column(Boolean)
    name = Column(String)
    nameType = Column(String)
    organizationType = Column(String)
    tradingName = Column(String)
    existsDuring = Column(Integer, ForeignKey("TimePeriod.id"))
    status = Column(String, default="initialized")
    _baseType = Column(String)
    _schemaLocation = Column(String)
    _type = Column(String)
    deleted = Column(Boolean, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.as_dict())

    # Used to set the db for the partyCharacteristicParsed and
    # existsDuringParsed properties
    db = None

    @classmethod
    def set_db(self, db):
        self.db = db

    # This enables not having to create specific methods to get the
    # organization's party characteristics
    @property
    def partyCharacteristicParsed(self):
        if not self.db:
            return []
        return self.db\
            .query(Characteristic)\
            .filter(Characteristic.organization == self.id)\
            .filter(Characteristic.deleted == bool(False))\
            .all()

    # This enables not having to create specific methods to get the
    # organization's time period
    @property
    def existsDuringParsed(self):
        if not self.db:
            return
        return self.db\
            .query(TimePeriod)\
            .filter(TimePeriod.id == self.existsDuring)\
            .filter(TimePeriod.deleted == bool(False))\
            .first()


class Characteristic(Base):
    __tablename__ = "Characteristic"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    valueType = Column(String)
    value = Column(String, nullable=False)
    organization = Column(
        Integer,
        ForeignKey("Organization.id"),
        nullable=False
    )
    _baseType = Column(String)
    _schemaLocation = Column(String)
    _type = Column(String)
    deleted = Column(Boolean, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.as_dict())

