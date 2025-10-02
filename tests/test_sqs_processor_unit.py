# tests/test_sqs_processor_unit.py
from unittest.mock import MagicMock, patch
import json
from scripts.sqs_processor import handler, process_record

@patch("scripts.sqs_processor.table")  # Patch the table, not dynamodb
def test_process_record_puts_item_on_first_call(mock_table):
    # simulate successful put
    mock_table.put_item.return_value = {}
    body = json.dumps({"bucket":"b","key":"k"})
    ok = process_record(body)
    assert ok is True
    mock_table.put_item.assert_called_once()

@patch("scripts.sqs_processor.table")  # Patch the table, not dynamodb
def test_process_record_idempotent_skip(mock_table):
    # simulate conditional check failed
    from botocore.exceptions import ClientError
    error_response = {"Error": {"Code": "ConditionalCheckFailedException", "Message":"Exists"}}
    mock_table.put_item.side_effect = ClientError(error_response, "PutItem")
    body = json.dumps({"bucket":"b","key":"k"})
    ok = process_record(body)
    assert ok is True