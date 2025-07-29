"""
Tests for the NomadicML video client.
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
from nomadicml import NomadicML
from nomadicml.types import VideoSource, ProcessingStatus, Severity, EventType
from nomadicml.exceptions import ValidationError, AnalysisError, NomadicMLError
import time

class TestVideoClient:
    """Test cases for the NomadicML video client."""

    @pytest.fixture
    def client(self):
        """Create a NomadicML client for testing."""
        return NomadicML(api_key="test_api_key")

    def test_upload_video_with_invalid_source(self, client):
        """Test upload_video with an invalid source."""
        with pytest.raises(ValueError):
            client.video.upload_video(source="invalid")

    def test_upload_video_file_with_missing_path(self, client):
        """Test upload_video with FILE source but missing file_path."""
        with pytest.raises(ValidationError):
            client.video.upload_video(source=VideoSource.FILE)

    def test_upload_video_saved_with_missing_id(self, client):
        """Test upload_video with SAVED source but missing video_id."""
        with pytest.raises(ValidationError):
            client.video.upload_video(source=VideoSource.SAVED)

    # Override the actual validate_file_path in the module namespace
    @patch("nomadicml.video.validate_file_path")
    @patch("nomadicml.video.VideoClient.get_user_id")
    @patch("nomadicml.utils.get_filename_from_path")
    @patch("nomadicml.utils.get_file_mime_type")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake video data")
    @patch("nomadicml.client.NomadicML._make_request")
    def test_upload_video_file_success(self, mock_make_request, mock_open_file,
                                   mock_get_mime_type, mock_get_filename,
                                   mock_get_user_id, mock_validate_path, client):
        """Test successful video file upload."""
        # Setup mocks
        mock_validate_path.return_value = None  # Just ensure it doesn't raise an exception
        mock_get_filename.return_value = "test_video.mp4"
        mock_get_mime_type.return_value = "video/mp4"
        mock_get_user_id.return_value = "test_user"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "video_id": "test_video_id"}
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = client.video.upload_video(
            source=VideoSource.FILE,
            file_path="/path/to/test_video.mp4"
        )
        
        # Assertions
        assert result == {"status": "success", "video_id": "test_video_id"}
        mock_validate_path.assert_called_once_with("/path/to/test_video.mp4")
        mock_make_request.assert_called_once()

    @patch("nomadicml.video.VideoClient.get_user_id")
    @patch("nomadicml.client.NomadicML._make_request")
    def test_upload_video_saved_success(self, mock_make_request, mock_get_user_id, client):
        """Test successful saved video upload."""
        # Setup mocks
        mock_get_user_id.return_value = "test_user"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "video_id": "test_video_id"}
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = client.video.upload_video(
            source=VideoSource.SAVED,
            video_id="test_video_id"
        )
        
        # Assertions
        assert result == {"status": "success", "video_id": "test_video_id"}
        # We'll check for the specific call instead of just assertion on call count
        mock_make_request.assert_any_call(
            method="POST", 
            endpoint="/api/upload-video", 
            data={
                'source': 'saved', 
                'firebase_collection_name': client.collection_name, 
                'created_by': 'test_user', 
                'video_id': 'test_video_id'
            }, 
            files=None, 
            timeout=18000
        )

    @patch("nomadicml.client.NomadicML._make_request")
    def test_analyze_video_success(self, mock_make_request, client):
        """Test successful video analysis."""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "processing", "video_id": "test_video_id"}
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = client.video.analyze_video("test_video_id")
        
        # Assertions
        # We need to make sure we're comparing to the return value from json()
        assert result == {"status": "processing", "video_id": "test_video_id"}

    @patch("nomadicml.client.NomadicML._make_request")
    def test_get_video_status(self, mock_make_request, client):
        """Test get_video_status method."""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "processing",
            "metadata": {"filename": "test.mp4"},
            "downloadProgress": {"percentage": 50}
        }
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = client.video.get_video_status("test_video_id")
        
        # Assertions
        # We need to ensure we're testing the return value from json(), not the mock itself
        assert result["status"] == "processing"

    @patch("nomadicml.video.VideoClient.get_video_status")
    @patch("time.sleep")
    def test_wait_for_analysis_success(self, mock_sleep, mock_get_status, client):
        """Test wait_for_analysis with successful completion."""
        # Setup mocks to first return processing, then completed
        mock_get_status.side_effect = [
            {"status": "processing", "metadata": {}},
            {"status": "completed", "metadata": {}}
        ]
        
        # Call the method
        result = client.video.wait_for_analysis("test_video_id", poll_interval=1)
        
        # Assertions
        assert result["status"] == "completed"
        assert mock_get_status.call_count == 2
        mock_sleep.assert_called_once_with(1)

    @patch("nomadicml.video.VideoClient.get_video_status")
    def test_wait_for_analysis_failure(self, mock_get_status, client):
        """Test wait_for_analysis with analysis failure."""
        # Setup mock to return failed status
        mock_get_status.return_value = {
            "status": "failed",
            "error": "Analysis failed"
        }
        
        # Call the method
        result = client.video.wait_for_analysis("test_video_id", poll_interval=0)  # Use 0 to skip sleep
        
        # Assertions
        assert result == {"status": "failed", "error": "Analysis failed"}
        assert mock_get_status.call_count >= 1

    # Important: Patch the validate_file_path in the video module
    @patch("nomadicml.video.validate_file_path")
    @patch("nomadicml.video.VideoClient.upload_video")
    @patch("nomadicml.video.VideoClient.analyze_video")
    @patch("nomadicml.video.VideoClient._wait_for_uploaded")
    @patch("nomadicml.video.VideoClient.wait_for_analysis")
    @patch("nomadicml.video.VideoClient.get_video_analysis")
    def test_upload_and_analyze_success(self, mock_get_analysis, mock_wait,
                                    mock_wait_uploaded,
                                    mock_analyze, mock_upload, mock_validate, client):
        """Test successful upload_and_analyze method."""
        # Setup mocks
        mock_validate.return_value = None
        mock_upload.return_value = {"status": "success", "video_id": "test_video_id"}
        mock_analyze.return_value = {"status": "processing"}
        mock_wait.return_value = {"status": "completed"}
        mock_wait_uploaded.return_value = None
        mock_get_analysis.return_value = {
            "video_metadata": {
                "video_id": "test_video_id"
            },
            "visual_analysis": {
                "events": [
                    {"event_type": "Traffic Violation", "start_time": 10.5}
                ]
            }
        }
        
        # Call the method
        result = client.video.upload_and_analyze("/path/to/test_video.mp4")
        
        # Assertions
        assert result.video_metadata.video_id == "test_video_id"
        assert result.visual_analysis is not None
        assert result.visual_analysis.events is not None
        assert len(result.visual_analysis.events) == 1
        assert result.visual_analysis.events[0].event_type == "Traffic Violation"
        assert result.visual_analysis.events[0].start_time == 10.5
        mock_validate.assert_called_once_with("/path/to/test_video.mp4")
        mock_upload.assert_called_once()
        mock_analyze.assert_called_once()
        mock_wait_uploaded.assert_called_once()
        mock_wait.assert_called_once()
        mock_get_analysis.assert_called_once()


    @patch("nomadicml.video.VideoClient.get_video_status")
    @patch("time.sleep")
    def test_wait_for_uploaded_chunked(self, mock_sleep, mock_status, client):
        mock_status.side_effect = [
            {"metadata": {"chunks_total": 2, "chunks_uploaded": 1}},
            {"metadata": {"chunks_total": 2, "chunks_uploaded": 2}},
        ]
        client.video._wait_for_uploaded("vid", timeout=10, initial_delay=0, max_delay=0)
        assert mock_status.call_count == 2


    @patch("nomadicml.client.NomadicML._make_request")
    def test_merge_video(self, mock_make_request, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 202
        mock_resp.json.return_value = {"message": "ok", "video_id": "123"}
        mock_make_request.return_value = mock_resp
        res = client.video._merge_video("123")
        assert res["video_id"] == "123"
        mock_make_request.assert_called_once_with("POST", "/api/merge-video/123", data={'firebase_collection_name': 'videos'})
