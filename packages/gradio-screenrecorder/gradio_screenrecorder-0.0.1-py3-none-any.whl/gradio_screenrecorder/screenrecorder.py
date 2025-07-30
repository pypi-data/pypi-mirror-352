import gradio as gr
from gradio.components.base import Component
from gradio.data_classes import FileData, GradioModel
from typing import Optional, Literal, Any
import tempfile
import os
import json

class ScreenRecorderData(GradioModel):
    video: Optional[FileData] = None
    duration: Optional[float] = None
    audio_enabled: bool = True
    status: Literal["recording", "stopped", "error"] = "stopped"

    class Config:
        json_encoders = {
            FileData: lambda v: v.model_dump() if v else None
        }


class ScreenRecorder(Component):
    """
    Custom Gradio component for comprehensive screen recording functionality.
    """
    
    data_model = ScreenRecorderData
    
    EVENTS = [
        "record_start",
        "record_stop", 
        "stream_update",
        "change"
    ]
    
    def __init__(
        self,
        value=None,
        audio_enabled: bool = True,
        webcam_overlay: bool = False,
        webcam_position: Literal["top-left", "top-right", "bottom-left", "bottom-right"] = "bottom-right",
        recording_format: str = "webm",
        max_duration: Optional[int] = None,
        interactive: bool = True,
        **kwargs
    ):
        self.audio_enabled = audio_enabled
        self.webcam_overlay = webcam_overlay
        self.webcam_position = webcam_position
        self.recording_format = recording_format
        self.max_duration = max_duration
        self._status = "stopped"
        
        super().__init__(
            value=value,
            interactive=interactive,
            **kwargs
        )
    
    def example_payload(self) -> dict:
        """
        The example inputs for this component for API usage. Must be JSON-serializable.
        """
        return {
            "video": {
                "path": "https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_1mb.mp4",
                "orig_name": "example_recording.webm",
                "size": 1024000
            },
            "duration": 30.5,
            "audio_enabled": True,
            "status": "stopped"
        }
    
    def example_value(self) -> ScreenRecorderData:
        """
        An example value for this component for the default app.
        """
        return ScreenRecorderData(
            video=FileData(
                path="https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_1mb.mp4",
                orig_name="example_recording.webm", 
                size=1024000
            ),
            duration=30.5,
            audio_enabled=True,
            status="stopped"
        )
    
    def flag(self, x, flag_dir: str = "") -> str:
        """
        Write the component's value to a format for flagging (CSV storage).
        """
        if x is None:
            return ""
        
        if isinstance(x, ScreenRecorderData) and x.video:
            return f"Recording: {x.video.orig_name} ({x.duration}s) - Status: {x.status}"
        
        if isinstance(x, dict) and "video" in x:
            duration = x.get("duration", "unknown")
            status = x.get("status", "unknown")
            video_name = x["video"].get("orig_name", "unknown") if x["video"] else "none"
            return f"Recording: {video_name} ({duration}s) - Status: {status}"
        
        return str(x)
    
    def preprocess(self, payload) -> Optional[ScreenRecorderData]:
        """Process incoming recording data from frontend."""
        if payload is None:
            return None

        if isinstance(payload, dict):
            if payload.get("status") == "error": # Early exit for errors from frontend
                raise gr.Error(f"Recording failed on frontend: {payload.get('error', 'Unknown error')}")

            # If 'video' field is a string, assume it's JSON and parse it.
            if "video" in payload and isinstance(payload["video"], str):
                try:
                    video_json_string = payload["video"]
                    if video_json_string.strip().startswith("{") and video_json_string.strip().endswith("}"):
                        payload["video"] = json.loads(video_json_string)
                    # If it's a string but not our expected JSON (e.g. 'null', or empty string, or simple path)
                    # json.loads would fail or Pydantic validation later will catch it if structure is wrong.
                    # For 'null' string, json.loads results in None for payload["video"].
                    elif video_json_string.lower() == 'null':
                        payload["video"] = None
                    else:
                        # This case implies a string that isn't a JSON object or 'null',
                        # e.g. a direct file path string, which FileData might not directly accept
                        # if it expects a dict. Pydantic will raise error later if type is incompatible.
                        gr.Warning(f"Video data is a string but not a recognized JSON object or 'null': {video_json_string[:100]}")
                        # To be safe, if it's not a JSON object string, we might want to error or handle specifically
                        # For now, let Pydantic try to handle it or fail.

                except json.JSONDecodeError:
                    raise gr.Error(f"Invalid JSON for video data: {payload['video'][:100]}")

            # --- Validations from here --- 
            video_data = payload.get("video") # Use .get() for safety, as 'video' might be absent or None

            if video_data is not None: # Only validate video_data if it exists
                if not isinstance(video_data, dict):
                    # This can happen if payload["video"] was a string like "some_path.webm" and not parsed to dict
                    # Or if it was parsed to something unexpected.
                    raise gr.Error(f"Video data is not a dictionary after processing: {type(video_data)}. Value: {str(video_data)[:100]}")
                
                if video_data.get("size", 0) == 0:
                    gr.Warning("Received recording with zero size. This might be an empty recording or an issue with data capture.")
                    # Depending on requirements, could raise gr.Error here.

                max_size = 500 * 1024 * 1024  # 500MB
                if video_data.get("size", 0) > max_size:
                    raise gr.Error(f"Recording file too large ({video_data.get('size', 0)} bytes). Maximum allowed: {max_size} bytes.")
            # If video_data is None (e.g. 'video': null was sent, or 'video' key missing), 
            # ScreenRecorderData will have video=None, which is allowed by Optional[FileData].
            
            duration = payload.get("duration", 0)
            if duration <= 0 and video_data is not None: # Only warn about duration if there's video data
                gr.Warning("Recording duration is 0 or invalid. The recording might be corrupted.")
            
            try:
                return ScreenRecorderData(**payload)
            except Exception as e: # Catch Pydantic validation errors or other issues during model instantiation
                # Log the payload for easier debugging if there's a Pydantic error
                # Be careful with logging sensitive data in production.
                # print(f"Error creating ScreenRecorderData. Payload: {payload}")
                raise gr.Error(f"Error creating ScreenRecorderData from payload: {e}")

        elif isinstance(payload, ScreenRecorderData): # If it's already the correct type
            return payload
        
        gr.Warning(f"Unexpected payload format: {type(payload)}. Payload: {str(payload)[:200]}")
        return None
    
    # def postprocess(self, value) -> Optional[dict]:
    #     """Process outgoing data to frontend."""
    #     if value is None:
    #         return {"status": "stopped"}  # Ensure valid empty state

    #     try:
    #         if isinstance(value, ScreenRecorderData):
    #             return value.model_dump()
    #         elif isinstance(value, dict):
    #             return value
    #         return None
    #     except Exception as e:
    #         return {"status": "error", "error": str(e)}


    def postprocess(self, value) -> Optional[dict]:
        """Process outgoing data to frontend."""
        print(f'value in postprocess: {value}')
        if value is None:
            return None
            
        try:
            # If it's already a dict, return as is
            if isinstance(value, dict):
                return value
                
            # If it's a ScreenRecorderData object, convert to dict
            if hasattr(value, 'model_dump'):
                return value.model_dump()
                
            # Handle string values
            if isinstance(value, str):
                return {"video": {"path": value}}
                
            return None
            
        except Exception as e:
            print(f'Error in postprocess: {e}')
            return None


        # try:
        #     if isinstance(value, ScreenRecorderData):
        #         # Ensure video data exists before sending
        #         if not value.video:
        #             return {"status": "error", "error": "No video recorded"}
                
        #         return {
        #             "video": value.video,
        #             "duration": value.duration,
        #             "audio_enabled": value.audio_enabled,
        #             "status": value.status
        #         }
            
        #     # Handle raw dict format from frontend
        #     if isinstance(value, dict):
        #         return {
        #             "video": FileData(**value.get("video", {})),
        #             "duration": value.get("duration"),
        #             "audio_enabled": value.get("audio_enabled", True),
        #             "status": value.get("status", "stopped")
        #         }
        
        # except Exception as e:
        #     return {"status": "error", "error": str(e)}
        
        # return {"status": "stopped"}

    def as_example(self, input_data):
        """Handle example data display."""
        if input_data is None:
            return None
        
        if isinstance(input_data, (ScreenRecorderData, dict)):
            return input_data
        
        # Convert simple video path to proper format
        if isinstance(input_data, str):
            return {
                "video": {
                    "path": input_data,
                    "orig_name": os.path.basename(input_data),
                    "size": 0
                },
                "duration": None,
                "audio_enabled": self.audio_enabled,
                "status": "stopped"
            }
        
        return input_data

    def update_status(self, status: Literal["recording", "stopped", "error"]):
        """Update the internal status of the recorder."""
        self._status = status
        
    def get_status(self) -> str:
        """Get the current status of the recorder."""
        return self._status
