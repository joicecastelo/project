# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-04-10 16:14:59

# general imports
import pytest
from pydantic import ValidationError
import datetime

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas


def import_modules():
    # additional custom imports
    from tests.configure_test_db import (
        engine as imported_engine,
        test_client as imported_test_client,
        override_get_db as imported_override_get_db
    )
    from database.database import Base as imported_base
    global engine
    engine = imported_engine
    global Base
    Base = imported_base
    global test_client
    test_client = imported_test_client
    global override_get_db
    override_get_db = imported_override_get_db


# Create the DB and IDP before each test and delete it afterwards
@pytest.fixture(autouse=True)
def setup(monkeypatch, mocker):
    import_modules()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_time_period_correct_database_creation_both_dates():

    # Prepare Test
    result = crud.create_organization(
        db=next(override_get_db()),
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="ITAv",
            existsDuring=TMF632Schemas.TimePeriod(
                startDateTime="2015-10-22T08:31:52.026Z",
                endDateTime="2016-10-22T08:31:52.026Z",
            )
        )
    )
    startDateTime = datetime.datetime(2015, 10, 22, 8, 31, 52, 26000)
    endDateTime = datetime.datetime(2016, 10, 22, 8, 31, 52, 26000)

    # Test
    assert result.existsDuringParsed.startDateTime.replace(tzinfo=None)\
        == startDateTime
    assert result.existsDuringParsed.endDateTime.replace(tzinfo=None)\
        == endDateTime


def test_time_period_correct_database_creation_only_1_date():

    # Prepare Test
    result = crud.create_organization(
        db=next(override_get_db()),
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="ITAv",
            existsDuring=TMF632Schemas.TimePeriod(
                startDateTime="2015-10-22T08:31:52.026Z",
            )
        )
    )
    startDateTime = datetime.datetime(2015, 10, 22, 8, 31, 52, 26000)

    # Test
    assert result.existsDuringParsed.startDateTime.replace(tzinfo=None)\
        == startDateTime
    assert result.existsDuringParsed.endDateTime is None


def test_time_period_incorrect_data():

    with pytest.raises(ValidationError) as exception:
        TMF632Schemas.TimePeriod(
            startDateTime="This 'date' is not a date!",
        )

    assert "TimePeriod" and "startDateTime" in str(exception)
