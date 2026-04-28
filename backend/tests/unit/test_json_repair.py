from app.utils.json_repair import extract_json_block, parse_json_with_repair


def test_parse_clean_json():
    result = parse_json_with_repair('{"key": "value"}')
    assert result == {"key": "value"}


def test_extract_from_prose():
    text = 'Here is the result: {"title": "Test", "severity": "HIGH"} and done.'
    result = parse_json_with_repair(text)
    assert result is not None
    assert result["title"] == "Test"


def test_extract_from_fenced_block():
    text = '```json\n{"confidence": 80}\n```'
    result = parse_json_with_repair(text)
    assert result is not None
    assert result["confidence"] == 80


def test_none_on_no_json():
    assert parse_json_with_repair("no json here at all") is None


def test_extract_json_block_finds_brace():
    text = 'prefix {"a": 1} suffix'
    block = extract_json_block(text)
    assert block is not None
    assert '"a"' in block
