import os
from unittest import mock

import pytest

try:
    from cryptography import x509
    from OpenSSL.crypto import FILETYPE_PEM, load_certificate  # type: ignore[import]

    from urllib3.contrib.pyopenssl import _dnsname_to_stdlib, get_subj_alt_name
except ImportError:
    pass


def setup_module() -> None:
    try:
        from urllib3.contrib.pyopenssl import inject_into_urllib3

        inject_into_urllib3()
    except ImportError as e:
        pytest.skip(f"Could not import PyOpenSSL: {e!r}")


def teardown_module() -> None:
    try:
        from urllib3.contrib.pyopenssl import extract_from_urllib3

        extract_from_urllib3()
    except ImportError:
        pass


from ..test_ssl import TestSSL  # noqa: E402, F401
from ..test_util import TestUtilSSL  # noqa: E402, F401
from ..with_dummyserver.test_https import (  # noqa: E402, F401
    TestHTTPS,
    TestHTTPS_IPSAN,
    TestHTTPS_IPV6SAN,
    TestHTTPS_TLSv1,
    TestHTTPS_TLSv1_1,
    TestHTTPS_TLSv1_2,
    TestHTTPS_TLSv1_3,
)
from ..with_dummyserver.test_socketlevel import (  # noqa: E402, F401
    TestClientCerts,
    TestSNI,
    TestSocketClosing,
)
from ..with_dummyserver.test_socketlevel import (  # noqa: E402, F401
    TestSSL as TestSocketSSL,
)


class TestPyOpenSSLHelpers:
    """
    Tests for PyOpenSSL helper functions.
    """

    def test_dnsname_to_stdlib_simple(self) -> None:
        """
        We can convert a dnsname to a native string when the domain is simple.
        """
        name = "उदाहरण.परीक"
        expected_result = "xn--p1b6ci4b4b3a.xn--11b5bs8d"

        assert _dnsname_to_stdlib(name) == expected_result

    def test_dnsname_to_stdlib_leading_period(self) -> None:
        """
        If there is a . in front of the domain name we correctly encode it.
        """
        name = ".उदाहरण.परीक"
        expected_result = ".xn--p1b6ci4b4b3a.xn--11b5bs8d"

        assert _dnsname_to_stdlib(name) == expected_result

    def test_dnsname_to_stdlib_leading_splat(self) -> None:
        """
        If there's a wildcard character in the front of the string we handle it
        appropriately.
        """
        name = "*.उदाहरण.परीक"
        expected_result = "*.xn--p1b6ci4b4b3a.xn--11b5bs8d"

        assert _dnsname_to_stdlib(name) == expected_result

    @mock.patch("urllib3.contrib.pyopenssl.log.warning")
    def test_get_subj_alt_name(self, mock_warning) -> None:
        """
        If a certificate has two subject alternative names, cryptography raises
        an x509.DuplicateExtension exception.
        """
        path = os.path.join(os.path.dirname(__file__), "duplicate_san.pem")
        with open(path) as fp:
            cert = load_certificate(FILETYPE_PEM, fp.read())

        assert get_subj_alt_name(cert) == []

        assert mock_warning.call_count == 1
        assert isinstance(mock_warning.call_args[0][1], x509.DuplicateExtension)
