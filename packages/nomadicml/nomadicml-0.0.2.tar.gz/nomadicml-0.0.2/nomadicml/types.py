"""Type definitions for the NomadicML SDK."""

from enum import Enum
from typing import Dict, List, Optional, Union, Any, Type, TypeVar
from dataclasses import dataclass, fields # Using fields for more robust field checking in subset_type if needed
import copy

class VideoSource(str, Enum):
    """Video source types."""
    
    FILE = "file"
    SAVED = "saved"


class ProcessingStatus(str, Enum):
    """Video processing status types."""
    
    UPLOADING = "uploading"
    UPLOADING_FAILED = "uploading_failed"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"



class Severity(str, Enum):
    """Severity levels for detected events."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class EventMetrics:
    """Metrics for a detected event."""
    
    relativeSpeed: Optional[str] = None
    distance: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class Event:
    """Represents a detected event in a video."""
    
    description: str
    type: str
    summaryStatus: str
    recommendations: str
    aiAnalysis: str
    potentialViolations: str
    time: str
    violationValidation: str
    severity: Severity
    end_time: str
    metrics: EventMetrics


@dataclass
class ChunkStatus:
    """Status of video processing chunks."""
    
    chunks_queued: int
    status: str
    chunks_total: int


@dataclass
class VisualAnalysis:
    """Visual analysis results for a video."""
    
    model_id: str
    events: List[Event]
    progress: int
    status: ChunkStatus
    timestamp: str


@dataclass
class VideoMetadata:
    """Metadata information about a video."""
    
    created_at: str
    video_url: str
    share_token: str
    id: str
    desc: str
    url: str
    fps: float
    width: int
    tag: str
    visual_analysis: VisualAnalysis
    filename: str
    chunks_total: int
    chunk_status: Dict[str, str]
    height: int
    chunk_ids: List[str]
    source: VideoSource
    duration_s: int
    created_by_app: str
    frame_count: int
    title: str
    created_by: str
    video_id: str
    chunks_completed: int
    pre_summary: str
    chunks_uploaded: int
    category: Optional[str] = None


@dataclass
class UploadAnalyzeResponse:
    """Response from upload_and_analyze method."""
    video_id: str
    metadata: VideoMetadata
    status: str


@dataclass
class EventSubset:
    description: str
    type: str
    severity: Severity
    time: str
    end_time: str
    recommendations: str
    potentialViolations: str
    violationValidation: str
    aiAnalysis: str

@dataclass
class VisualAnalysisSubset:
    model_id: str
    events: List[EventSubset]

@dataclass
class VideoMetadataSubset:
    filename: str
    created_at: str
    video_url: str
    tag: str
    duration_s: int
    created_by_app: str
    pre_summary: str
    visual_analysis: VisualAnalysisSubset


@dataclass
class UploadAnalyzeResponseSubset:
    """Response from upload_and_analyze method."""
    video_id: str
    metadata: VideoMetadataSubset
    status: str

def subset_type(input : Dict[str, Any], out_type : Type):
    input = {k: v for k, v in input.items() if k in out_type.__match_args__}
    return out_type(**input)

def convert_to_upload_analyze_response_subset(response: Dict[str, Any]) -> UploadAnalyzeResponseSubset:
    """Converts a full UploadAnalyzeResponse to its subset version."""
    # deep copy response
    response = copy.deepcopy(response)
    events = response['metadata']['visual_analysis']['events']
    events = [subset_type(e, EventSubset) for e in events]

    visual_analysis = VisualAnalysisSubset(
        model_id=response['metadata']['visual_analysis']['model_id'],
        events=events
    )
    metadata = response['metadata']
    metadata['visual_analysis'] = visual_analysis
    metadata = subset_type(metadata, VideoMetadataSubset)
    return UploadAnalyzeResponseSubset(
        video_id=response['video_id'],
        metadata=metadata,
        status=response['status'],
    )
