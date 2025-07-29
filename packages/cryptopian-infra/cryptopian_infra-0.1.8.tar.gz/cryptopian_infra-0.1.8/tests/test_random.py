import json
import uuid

import pytest


def test_uuid():
    print(uuid.uuid4())


@pytest.mark.parametrize('to_convert', ['True', 'true', 'false', 'False', 'Anything not empty', 1, 1000])
def test_convert_to_true_string(to_convert):
    assert bool(to_convert)


@pytest.mark.parametrize('to_convert', ['', 0])
def test_convert_to_false(to_convert):
    assert not bool(to_convert)


@pytest.mark.parametrize('to_convert,expected', [('False', False), ('false', False), ('True', True), ('true', True)])
def test_json_parse(to_convert, expected):
    assert json.loads(to_convert.lower()) == expected
