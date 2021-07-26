import pickle
from email.errors import MessageDefect

import pytest

from urllib3.connection import HTTPConnection
from urllib3.connectionpool import HTTPConnectionPool
from urllib3.exceptions import (
    ClosedPoolError,
    ConnectTimeoutError,
    EmptyPoolError,
    HeaderParsingError,
    HostChangedError,
    HTTPError,
    LocationParseError,
    MaxRetryError,
    NewConnectionError,
    ReadTimeoutError,
)


class TestPickle:
    @pytest.mark.parametrize(
        "exception",
        [
            HTTPError(None),
            MaxRetryError(HTTPConnectionPool("localhost"), "dummy", None),
            LocationParseError("dummy"),
            ConnectTimeoutError(None),
            HTTPError("foo"),
            HTTPError("foo", IOError("foo")),
            MaxRetryError(HTTPConnectionPool("localhost"), "/", None),
            LocationParseError("fake location"),
            ClosedPoolError(HTTPConnectionPool("localhost"), "dummy"),
            EmptyPoolError(HTTPConnectionPool("localhost"), "dummy"),
            HostChangedError(HTTPConnectionPool("localhost"), "/", 1),
            ReadTimeoutError(HTTPConnectionPool("localhost"), "/", "dummy"),
        ],
    )
    def test_exceptions(self, exception: Exception) -> None:
        result = pickle.loads(pickle.dumps(exception))
        assert isinstance(result, type(exception))


class TestFormat:
    def test_header_parsing_errors(self) -> None:
        hpe = HeaderParsingError([MessageDefect("defect")], "unparsed_data")

        assert "defects" in str(hpe)
        assert "unparsed_data" in str(hpe)


class TestNewConnectionError:
    def test_pool_property_deprecation_warning(self) -> None:
        err = NewConnectionError(HTTPConnection("localhost"), "test")
        msg = (
            "The 'pool' property is deprecated and will be removed "
            "in a later urllib3 v2.x release. use 'conn' instead."
        )
        with pytest.warns(DeprecationWarning, match=msg):
            err.pool

        assert err.pool is err.conn
