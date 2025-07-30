import datetime
import time

import pydantic
import pytest
from packaging.version import Version

from freezeblaster import FakeDate, FakeDatetime, freeze_time


def test_simple() -> None:
    # time to freeze is always provided in UTC
    freezer = freeze_time("2012-01-14")
    # expected timestamp must be a timestamp, corresponding to 2012-01-14 UTC
    local_time = datetime.datetime(2012, 1, 14)
    utc_time = local_time - datetime.timedelta(seconds=time.timezone)
    expected_timestamp = time.mktime(utc_time.timetuple())

    freezer.start()
    assert time.time() == expected_timestamp
    assert time.monotonic() >= 0.0
    assert time.perf_counter() >= 0.0
    assert datetime.datetime.now() == datetime.datetime(2012, 1, 14)
    assert datetime.datetime.utcnow() == datetime.datetime(2012, 1, 14)
    assert datetime.date.today() == datetime.date(2012, 1, 14)
    assert datetime.datetime.now().today() == datetime.datetime(2012, 1, 14)
    freezer.stop()
    assert time.time() != expected_timestamp
    assert time.monotonic() >= 0.0
    assert time.perf_counter() >= 0.0
    assert datetime.datetime.now() != datetime.datetime(2012, 1, 14)
    assert datetime.datetime.utcnow() != datetime.datetime(2012, 1, 14)
    freezer = freeze_time("2012-01-10 13:52:01")
    freezer.start()
    assert datetime.datetime.now() == datetime.datetime(2012, 1, 10, 13, 52, 1)
    freezer.stop()


@pytest.mark.skipif(
    not Version("2") <= Version(pydantic.__version__) < Version("3"),
    reason="requires pydantic version 2.x",
)
def test_pydantic_v2() -> None:
    class TestModel(pydantic.BaseModel):
        test_datetime: datetime.datetime
        test_date: datetime.date

    freezer = freeze_time("2012-01-10 13:52:01")
    freezer.start()

    current_time = datetime.datetime.now(datetime.timezone.utc)
    test_data = TestModel(test_datetime=current_time, test_date=current_time.date())

    assert test_data.model_dump() == {
        "test_date": FakeDate(2012, 1, 10),
        "test_datetime": FakeDatetime(2012, 1, 10, 13, 52, 1, tzinfo=datetime.timezone.utc),
    }
    assert test_data.model_dump(mode="json") == {"test_date": "2012-01-10", "test_datetime": "2012-01-10T13:52:01Z"}
    assert test_data.model_dump_json() == '{"test_datetime":"2012-01-10T13:52:01Z","test_date":"2012-01-10"}'

    parsed_test_data = test_data.model_validate({"test_date": "2012-01-10", "test_datetime": "2012-01-10T13:52:01Z"})
    assert parsed_test_data == test_data

    freezer.stop()


@pytest.mark.skipif(
    not Version("1") <= Version(pydantic.__version__) < Version("2"),
    reason="requires pydantic version 2.x",
)
def test_pydantic_v1() -> None:
    class TestModel(pydantic.BaseModel):
        test_datetime: datetime.datetime
        test_date: datetime.date

    freezer = freeze_time("2012-01-10 13:52:01")
    freezer.start()

    current_time = datetime.datetime.now(datetime.timezone.utc)
    test_data = TestModel(test_datetime=current_time, test_date=current_time.date())

    assert test_data.dict() == {
        "test_date": FakeDate(2012, 1, 10),
        "test_datetime": FakeDatetime(2012, 1, 10, 13, 52, 1, tzinfo=datetime.timezone.utc),
    }
    assert test_data.json() == '{"test_datetime": "2012-01-10T13:52:01+00:00", "test_date": "2012-01-10"}'

    parsed_test_data = test_data.parse_obj({"test_date": "2012-01-10", "test_datetime": "2012-01-10T13:52:01Z"})
    assert parsed_test_data == test_data

    freezer.stop()
