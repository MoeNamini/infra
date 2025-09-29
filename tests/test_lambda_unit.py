# tests/test_lambda_unit.py
import json
from unittest.mock import MagicMock, patch
from scripts.lambda_handler import handler

@patch("scripts.lambda_handler.dynamodb")
@patch("scripts.lambda_handler.s3")
def test_handler_writes_ddb(mock_s3, mock_dynamo):
    # Arrange: fake S3 head_object response
    mock_s3.head_object.return_value = {'ContentLength': 123, 'ContentType': 'text/csv'}
    table = MagicMock()
    mock_dynamo.Table.return_value = table

    # Fake S3 event
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "my-bucket"},
                    "object": {"key": "upload/test.csv"}
                }
            }
        ]
    }
    # Act
    resp = handler(event, None)
    # Assert
    table.put_item.assert_called_once()
    args = table.put_item.call_args[1]['Item']
    assert args['s3_bucket'] == 'my-bucket'
    assert args['s3_key'] == 'upload/test.csv'
    assert args['processing_status'] == 'RECEIVED'