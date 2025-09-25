import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import MagicMock, patch
from generate_presigned_put import generate_presigned_put

@patch("boto3.client")
def test_generate_presigned_put_calls_boto3_with_sse(mock_boto_client):
    mock_client = MagicMock()
    mock_client.generate_presigned_url.return_value = "https://example.com/presigned"
    mock_boto_client.return_value = mock_client

    url = generate_presigned_put("my-bucket", "my-key", expiration=123)

    assert url == "https://example.com/presigned"
    mock_client.generate_presigned_url.assert_called_once()
    args, kwargs = mock_client.generate_presigned_url.call_args
    
    assert args[0] == "put_object"
    assert kwargs["Params"]["Bucket"] == "my-bucket"
    assert kwargs["Params"]["Key"] == "my-key" 
    assert kwargs["Params"]["ServerSideEncryption"] == "AES256"
    assert kwargs["ExpiresIn"] == 123
    assert kwargs["HttpMethod"] == "PUT"
