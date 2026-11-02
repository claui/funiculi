# pylint: disable=magic-value-comparison, missing-function-docstring, missing-module-docstring, no-self-use, too-many-public-methods

import pytest

from funiculi.api import Api


@pytest.fixture(name='api')
def fixture_api() -> Api:
    return Api(host='127.255.255.0')


def test_sanity(api: Api) -> None:
    assert api is not None
