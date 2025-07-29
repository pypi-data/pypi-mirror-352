"""
Video-related operations for the NomadicML SDK.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import time
import logging
from typing import Dict, Any, List, Optional, Union
import random

from .client import NomadicML
from .types import (
    VideoSource, 
    UploadAnalyzeResponse,
    UploadAnalyzeResponseSubset, 
    convert_to_upload_analyze_response_subset
)
from .utils import (
    format_error_message, validate_file_path,
    get_file_mime_type, get_filename_from_path
)
from .exceptions import VideoUploadError, NomadicMLError, ValidationError

logger = logging.getLogger("nomadicml")


class VideoClient:
    """
    Client for video upload and analysis operations.
    
    This class extends the base NomadicML client with video-specific operations.
    
    Args:
        client: An initialized NomadicML client.
    """
    _status_ranks = {
        "NOT_STARTED": 0,
        "PREPARE_IN_PROGRESS": 0.5,
        "PREPARE_COMPLETED": 1,
        "UPLOADED": 1,
        "DETECTING_IN_PROGRESS": 1.5,
        "PROCESSING": 1.5,
        "DETECTING_COMPLETED": 2,
        "DETECTING_COMPLETED_NO_EVENTS": 2.1,
        "SUMMARIZING_IN_PROGRESS": 2.5,
        "SUMMARIZING_COMPLETED": 3,
        "COMPLETED": 3,
    }
    
    def __init__(self, client: NomadicML):
        """
        Initialize the video client with a NomadicML client.
        
        Args:
            client: An initialized NomadicML client.
        """
        self.client = client
        self._user_info = None

    def _print_status_bar(self, video_id: str, status: str):
        """
        Pretty-print a status bar based on the current processing status.
        """
        rank = self._status_ranks.get(status.upper(), 0)
        total = max(self._status_ranks.values())
        length = 30
        filled = int((rank / total) * length)
        bar = '[' + '=' * filled + ' ' * (length - filled) + ']' 
        logger.info(f"For video {video_id}: {bar} {status.upper()}\n")
        
    async def _get_auth_user(self) -> Optional[Dict[str, Any]]:
        """
        Get the authenticated user information.
        
        Returns:
            A dictionary with user information if available, None otherwise.
        """
        if self.user_info:
            return self.user_info
            
        try:
            response = self.client._make_request(
                method="POST",
                endpoint="/api/keys/verify",
            )
            
            self.user_info = response.json()
            return self.user_info
        except Exception as e:
            logger.warning(f"Failed to get authenticated user info: {e}")
            return None

    def _parse_api_events(self, analysis_json):
            """
            Parse the API analysis JSON into a list of event dictionaries.
            
            Args:
                analysis_json: The raw JSON dict returned from the API.
                default_duration: Default duration (in seconds) to assume if an event only has a single time point.
                
            Returns:
                list: List of events dictionaries with label, start_time, and end_time
            """
            results = []
            
            # Debug: Print top-level keys to help understand structure
            logger.debug(f"Parsing API events. Top-level keys: {list(analysis_json.keys())}")
            
            # Try different possible paths for events
            events_list = (
                analysis_json
                .get("events", {})
                .get("visual_analysis", {})
                .get("status", {})
                .get("quick_summary", {})
                .get("events", None)
            )

            if not events_list:
                logger.debug("events list empty in API response")
                return results
                
            # Process each event
            for event in events_list:
                # We'll treat 'description' as the label.
                label = event.get("description", "Unknown")
                
                # Print event structure for debugging
                logger.debug(f"Processing event: {label}")
                
                # Try to extract start and end time information
                start_time = None
                end_time = None
            
                if "time" in event:
                    time_str = event.get("time", "")
                    match = re.search(r"t=(\d+(\.\d+)?)", time_str)
                    if match:
                        start_time = float(match.group(1))
                    
                if "end_time" in event:
                    end_time_str = event.get("end_time", "")
                    match = re.search(r"t=(\d+(\.\d+)?)", end_time_str)
                    if match:
                        end_time = float(match.group(1))
                        
                
                # Check for refined_events if present
                used_refined_events = False
                refined = event.get("refined_events", "")
                if refined:
                    try:
                        refined_data = json.loads(refined)  # Expecting a list of intervals like [start, end, text]
                        if isinstance(refined_data, list):
                            for item in refined_data:
                                if isinstance(item, list) and len(item) >= 2:
                                    st = float(item[0])
                                    en = float(item[1])
                                    results.append({
                                        "label": label,
                                        "start_time": st,
                                        "end_time": en
                                    })
                                    used_refined_events = True
                                    logger.debug(f"  Added refined event: {label} from {st}s to {en}s")
                    except json.JSONDecodeError:
                        logger.warning(f"  Failed to parse refined_events JSON: {refined[:50]}...")
                        pass

                # If no refined intervals and we found basic timing, use that
                if not used_refined_events and start_time is not None and end_time is not None:
                    results.append({
                        "label": label,
                        "start_time": start_time,
                        "end_time": end_time
                    })
                    logger.debug(f"  Added event: {label} from {start_time}s to {end_time}s")
            
            logger.info(f"Total events extracted: {len(results)}")
            return results
    
    def get_user_id(self) -> Optional[str]:
        """
        Get the authenticated user ID.
        
        Returns:
            The user ID if available, None otherwise.
        """
        # Try to get cached user info
        if self._user_info and "user_id" in self._user_info:
            return self._user_info["user_id"]
        
        # Make a synchronous request to get user info
        try:
            response = self.client._make_request(
                method="POST",
                endpoint="/api/keys/verify"
            )
            self._user_info = response.json()
            return self._user_info.get("user_id")
        except Exception as e:
            logger.warning(f"Failed to get user ID: {str(e)}")
            return None
    
    def generate_events(      
        self,
        video_id: str,
        category: str = "violations",
        custom_event: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ask the backend to derive structured events for ``video_id`` using the
        pre-built prompt associated with ``category``.  Mirrors POST /generate-events.
        """
        data = {
            "video_id": video_id,
            "category": category,
            "firebase_collection_name": self.client.collection_name,  # passes through auth context
        }

        if custom_event:
            data["custom_event"] = custom_event

        resp = self.client._make_request("POST", "/api/generate-events", data=data)
        if not 200 <= resp.status_code < 300:
            raise NomadicMLError(f"generate-events failed: {format_error_message(resp.json())}")
        return resp.json()
    
    def upload_video(
        self,
        source: Union[str, VideoSource],
        file_path: Optional[str] = None,
        video_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a video for analysis.
        
        Args:
            source: The source of the video. Can be "file" or "saved".
            file_path: Path to the video file (required when source is "file").
            video_id: ID of an existing video (required when source is "saved").
        
        Returns:
            A dictionary with the upload status and video_id.
        
        Raises:
            ValidationError: If the input parameters are invalid.
            VideoUploadError: If the upload fails.
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        # Convert string source to enum if needed
        if isinstance(source, str):
            try:
                source = VideoSource(source)
            except ValueError:
                raise ValueError(f"Invalid source: {source}. Must be one of {[s.value for s in VideoSource]}")
        
        # Validate inputs based on source
        if source == VideoSource.FILE and not file_path:
            raise ValidationError("file_path is required when source is 'file'")
        elif source == VideoSource.SAVED and not video_id:
            raise ValidationError("video_id is required when source is 'saved'")
        elif source not in [VideoSource.FILE, VideoSource.SAVED]:
            raise ValidationError(f"Invalid source: {source}. Must be 'file' or 'saved'.")
        
        # Validate file path if provided
        if source == VideoSource.FILE and file_path:
            validate_file_path(file_path)
                
        user_id = self.get_user_id()
        actual_created_by = user_id if user_id else "api_client"
        
        # Prepare request data
        endpoint = "/api/upload-video"
        
        # Prepare form data
        form_data = {
            "source": source.value,
            "firebase_collection_name": self.client.collection_name,
            "created_by": actual_created_by,
        }
        
        # Add file or video ID based on source
        files = None
        if source == VideoSource.FILE:
            filename = get_filename_from_path(file_path)
            mime_type = get_file_mime_type(file_path)
            
            # Open the file for upload
            with open(file_path, "rb") as f:
                file_content = f.read()
            
            # Create a multipart/form-data request
            files = {"file": (filename, file_content, mime_type)}
            logger.info(f"Uploading video with filename: {filename}")
        elif source == VideoSource.SAVED:
            form_data["video_id"] = video_id
                
        # Make the request
        response = self.client._make_request(
            method="POST",
            endpoint=endpoint,
            data=form_data,
            files=files,
            timeout=self.client.timeout*20,  # Longer timeout for uploads
        )
        # Check for errors in the response
        if not (200 <= response.status_code < 300):        # accept 200-299
            error_message = format_error_message(response.json())
            raise VideoUploadError(f"Failed to upload video: {error_message}")
        # Log the response for debugging
        logger.info(f"Upload video with source {source.value} response: {response.json()}")
        
        # Return the parsed JSON response
        return response.json()
    
    def analyze_video(self, video_id: str, model_id: Optional[str] = "Nomadic-VL-XLarge") -> Dict[str, Any]:
        """
        Start analysis for an uploaded video.
        
        Args:
            video_id: The ID of the video to analyze.
            
        Returns:
            A dictionary with the analysis status.
            
        Raises:
            AnalysisError: If the analysis fails to start.
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        endpoint = f"/api/analyze-video/{video_id}"
        
        # Use authenticated user ID
        user_id = self.get_user_id()
        actual_created_by = user_id if user_id else "api_client"
        
        # Prepare form data with the collection name
        data = {
            "firebase_collection_name": self.client.collection_name,
            "created_by": actual_created_by,
            "model_id": model_id,
        }
        
        # Make the request
        response = self.client._make_request(
            method="POST",
            endpoint=endpoint,
            data=data,
        )
        
        # Return the parsed JSON response
        return response.json()

    def analyze_videos(
        self,
        video_ids: List[str],
        model_id: Optional[str] = "Nomadic-VL-XLarge"
    ) -> List[Dict[str, Any]]:
        """
        Trigger analysis for multiple existing videos.

        Args:
            video_ids: List of video IDs to analyze.
            model_id: (Optional) model to use.

        Returns:
            A list of dicts, each containing the video_id and the backend response.
        """
        results = []
        for vid in video_ids:
            status = self.analyze_video(vid, model_id=model_id)
            results.append({"video_id": vid, "response": status})
        return results

    def upload_and_analyze_videos(
        self,
        file_paths: List[str],
        model_id: Optional[str] = "Nomadic-VL-XLarge",
        wait_for_completion: bool = False,
        timeout: int = 600,
        return_subset: bool = True,
        custom_category: Optional[str] = None,
        custom_event: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Upload and analyze multiple local video files in parallel.
        """
        with ThreadPoolExecutor(max_workers=len(file_paths)) as executor:
            futures = [
                executor.submit(
                    self.upload_and_analyze,
                    path,
                    wait_for_completion=wait_for_completion,
                    timeout=timeout,
                    model_id=model_id,
                    return_subset=return_subset,
                    custom_category=custom_category,
                    custom_event=custom_event,
                )
                for path in file_paths
            ]
            # Gather results in input order
            analyses = [f.result() for f in futures]
        return analyses
    
    def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get the status of a video analysis.
        
        Args:
            video_id: The ID of the video.
            
        Returns:
            A dictionary with the video status.
            
        Raises:
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        endpoint = f"/api/video/{video_id}/status"
        
        # Add the required collection_name parameter
        params = {"firebase_collection_name": self.client.collection_name}
        
        # Make the request
        response = self.client._make_request("GET", endpoint, params=params)
        
        # Return the parsed JSON response
        return response.json()
        
    def wait_for_analysis(
        self,
        video_id: str,
        timeout: int = 2_400, # Default 40 minutes
        poll_interval: int = 5,
    ) -> dict:
        """
        Block until the parent analysis finishes, triggering /merge-video for
        chunked uploads if necessary.
        """
        start_time = time.time()
        merge_triggered = False

        while True:
            payload = self.get_video_status(video_id)
            meta = payload.get("metadata", {})

            api_chunks_total = meta.get("chunks_total")
            api_chunks_completed = meta.get("chunks_completed")
        
            current_overall_status = str(payload.get("status", "")).upper()

            self._print_status_bar(video_id, current_overall_status) # Keep UI feedback

            logger.debug(f"Video {video_id} - Status: '{current_overall_status}', payload: '{payload}'")

            # Check for terminal states first
            if current_overall_status in ("COMPLETED", "FAILED"):
                logger.info(f"Video {video_id} reached terminal status: {current_overall_status}.")
                return payload

            # Check overall timeout (before potentially long sleep or other operations)
            if time.time() - start_time > timeout:
                logger.error(
                    f"Analysis for video {video_id} timed out after {timeout}s. "
                    f"Last known overall status: {current_overall_status}."
                )
                raise TimeoutError(
                    f"Analysis for {video_id} did not complete in {timeout}s. "
                    f"Last known overall status: {current_overall_status}"
                )

            # Try to trigger merge if conditions are met and not already triggered
            if not merge_triggered:
                chunks_are_complete = (
                    isinstance(api_chunks_total, int) and api_chunks_total > 0 and
                    isinstance(api_chunks_completed, int) and api_chunks_completed >= api_chunks_total
                )

                # If chunks are complete and we haven't reached a terminal state yet,
                # and merge hasn't been triggered, trigger it.
                # (Terminal state check is already done above)
                if chunks_are_complete:
                    try:
                        logger.info(
                            f"Video {video_id}: All chunks ({api_chunks_completed}/{api_chunks_total}) "
                            f"reported complete by API. Current status: '{current_overall_status}'. Triggering merge."
                        )
                        self._merge_video(video_id)
                        merge_triggered = True
                    except Exception as e:
                        # If merge trigger fails, log it but continue polling.
                        # The overall timeout or a status change to FAILED (if backend handles merge error) 
                        # will eventually stop the loop.
                        logger.warning(f"Video {video_id}: Failed to trigger merge: {e}. Will continue polling for status.")
        
            time.sleep(poll_interval)

    def wait_for_analyses(
        self,
        video_ids,
        timeout: int = 4800,
        poll_interval: int = 5
    ) -> dict:
        """
        Wait for multiple video analyses in parallel, with pretty status bars.
        """
        ids = list(video_ids)
        results = {}
        with ThreadPoolExecutor(max_workers=len(ids)) as executor:
            futures = {executor.submit(self.wait_for_analysis, vid, timeout, poll_interval): vid for vid in ids}
            for fut in as_completed(futures):
                vid = futures[fut]
                try:
                    results[vid] = fut.result()
                except Exception as e:
                    results[vid] = e
        return results
    
    def get_video_analysis(self, video_id: str) -> Dict[str, Any]:
        """
        Get the complete analysis of a video.
        
        Args:
            video_id: The ID of the video.
            
        Returns:
            The complete video analysis.
            
        Raises:
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        endpoint = f"/api/video/{video_id}/analysis"
        params = {"firebase_collection_name": self.client.collection_name}
                
        response = self.client._make_request(
            method="GET",
            endpoint=endpoint,
            params=params,
        )
        
        return response.json()
    
    def get_video_analyses(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get analyses for multiple videos.
        
        Args:
            video_ids: List of video IDs.
            
        Returns:
            A list of analyses for each video.
            
        Raises:
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        analyses = []
        for vid in video_ids:
            analysis = self.get_video_analysis(vid)
            analyses.append(analysis)
        return analyses
    
    def get_detected_events(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get detected events for a video.
        
        Args:
            video_id: The ID of the video.
            
        Returns:
            A list of detected events.
            
        Raises:
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        return self._parse_api_events(self.get_video_analysis(video_id))
    

    # ─────────────────────── wait until status == UPLOADED ───────────── CHANGED
    def _wait_for_uploaded(self,
                           video_id: str,
                           timeout: int = 1200,
                           initial_delay: int = 15,
                           max_delay: int = 30,
                           multiplier: int = 2) -> None:
        """Block until video upload is finished.

        Handles both single videos and chunked uploads. When ``chunks_total`` is
        present in metadata, this waits until all chunks are reported as
        uploaded; otherwise it waits for ``visual_analysis.status.status`` to become
        ``UPLOADED``.
        """
        delay = initial_delay
        deadline = time.time() + timeout

        while True:
            payload = self.get_video_status(video_id)
            meta = payload.get("metadata", {})

            state = (self._status_from_metadata(meta) or "").upper()
            total = meta.get("chunks_total")
            uploaded = meta.get("chunks_uploaded", 0)

            if isinstance(total, int) and total > 0:
                if uploaded >= total:
                    return
            elif state == "UPLOADED":
                return

            if state in ("UPLOADING_FAILED", "FAILED"):
                raise VideoUploadError(f"Upload failed (backend status={state})")
            if time.time() > deadline:
                raise TimeoutError(f"Backend never reached UPLOADED in {timeout}s")

            sleep_for = max(0, delay + random.uniform(-1, 1))
            time.sleep(sleep_for)

            delay = min(delay * multiplier, max_delay)

    def _merge_video(self, video_id: str) -> Dict[str, Any]:
        """Trigger merging of chunk analysis results for ``video_id``."""
        logger.info(f"SDK: Requesting merge for video {video_id} in collection {self.client.collection_name}")
        response = self.client._make_request(
            "POST",
            f"/api/merge-video/{video_id}",
            data={"firebase_collection_name": self.client.collection_name}
        )
        if response.status_code != 202:  # 202 Accepted is expected
            logger.error(
                f"Failed to trigger merge for video {video_id}: {response.status_code} {response.text}"
            )
            raise NomadicMLError(f"Failed to trigger merge for video {video_id}")
        return response.json()

    def upload_and_analyze(
        self,
        file_path: str,
        wait_for_completion: bool = True,
        timeout: int = 2400,  # 40 minutes
        model_id: Optional[str] = "Nomadic-VL-XLarge",
        return_subset: bool = True,
        custom_category: Optional[str] = None,
        custom_event: Optional[str] = None,
    ) -> Union[UploadAnalyzeResponse, UploadAnalyzeResponseSubset, Dict[str, Any]]:
        """
        Upload a video file and start analysis in one operation.
        
        Args:
            file_path: Path to the video file.
            wait_for_completion: Whether to wait for analysis to complete.
            timeout: Maximum time to wait for analysis in seconds.
            return_subset: Whether to return a subset of the analysis response.
            custom_category: (Optional) custom category to use.
            custom_event: (Optional) custom event to use.
            
        Returns:
            The video analysis result or status.
            
        Raises:
            ValidationError: If the input parameters are invalid.
            VideoUploadError: If the upload fails.
            AnalysisError: If the analysis fails.
            TimeoutError: If the analysis does not complete within the timeout.
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        # Validate file path - directly call here to allow mocking in tests
        validate_file_path(file_path)
        
       # 1. upload
        upload_result = self.upload_video(
            source=VideoSource.FILE,
            file_path=file_path,
        )
        video_id = upload_result["video_id"]
        logger.info(f"Video ID: {video_id}")

        # 2. wait until backend (and any chunks) finished uploading
        self._wait_for_uploaded(video_id, timeout=timeout)
        
        video_id = upload_result.get("video_id")
        if not video_id:
            raise NomadicMLError("Failed to get video ID from upload response")
        
        is_event_request = custom_category and custom_event   

        #.  Events-only fast path  (skip heavy analysis) --------------------
        if is_event_request:
            # build payload for /generate-events
            payload = {"video_id": video_id,
                    "firebase_collection_name": self.client.collection_name}

            if custom_category:
                payload["category"] = custom_category      
            if custom_event:
                payload["custom_event"] = custom_event    

            ev = self.generate_events(video_id, custom_category, custom_event)           # thin wrapper around _make_request
            return {
                "video_id": video_id,
                "events":   ev,
                "mode":     "events_only",
            }
        
        # Start analysis once all chunks are uploaded
        analysis_result = self.analyze_video(
            video_id=video_id,
            model_id=model_id
        )

        if wait_for_completion:
            _final_status = self.wait_for_analysis(
                video_id=video_id,
                timeout=timeout,
            )

            analysis_response_dict = self.get_video_analysis(video_id)
            if return_subset:
                try:
                    return convert_to_upload_analyze_response_subset(analysis_response_dict)
                except Exception as e:
                    logger.warning(f"Failed to convert to subset: {e}, returning full response")
                    return analysis_response_dict
            else:
                return analysis_response_dict

        # When wait_for_completion is False, analysis_result is Dict[str, Any] from analyze_video
        # and cannot be converted to UploadAnalyzeResponseSubset directly.
        return analysis_result

    def _status_from_metadata(self, meta: dict) -> Optional[str]:
        """
        Return the processing state stored in the scalar Firestore field
        `visual_analysis.status.status`.
        """
        return meta.get("visual_analysis", {}).get("status", {}).get("status")
    # ────────────────────────────────────────────────────────────────────
