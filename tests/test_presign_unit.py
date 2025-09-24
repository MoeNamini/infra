# infra/tests/test_presign_unit.py
from unittest.mock import MagicMock, patch
from generate_presigned_put import generate_presigned_put

@patch("boto3.client")
def test_generate_presigned_put_calls_boto3_with_sse(mock_boto_client):
    # Arrange: make client with generate_presigned_url returning a sentinel URL
    mock_client = MagicMock()
    mock_client.generate_presigned_url.return_value = "https://example.com/presigned"
    mock_boto_client.return_value = mock_client

    # Act: call with SSE
    url = generate_presigned_put("my-bucket", "my-key", expiration=123)

    # Assert: URL returned and boto3 called with correct params
    assert url == "https://example.com/presigned"
    mock_client.generate_presigned_url.assert_called_once()
    _, kwargs = mock_client.generate_presigned_url.call_args
    assert kwargs["Params"]["Bucket"] == "my-bucket"
    assert kwargs["Params"]["Key"] == "my-key"