---
tags: [custom-component-track, gradio-custom-component, screen-recorder, PIP, picture-in-picture]
title: gradio_screenrecorder
short_description: Screen Recorder with Picture in Picture Gradio Custom Component
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_screenrecorder`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  

Screen Recorder Gradio Custom Component

## Installation

```bash
pip install gradio_screenrecorder
```

## Usage

```python
import gradio as gr
from gradio_screenrecorder import ScreenRecorder

def handle_recording(recording_data):
    """Handle recorded video data"""
    print(f'Received recording data: {recording_data}')
    
    if not recording_data or not recording_data.get('video'):
        return None
    
    try:
        video_info = recording_data['video']
        # Return the video path that can be used by the Video component
        return video_info.get('path')
    except Exception as e:
        print(f'Error processing recording: {e}')
        return None


css = """
.screen-recorder-demo {
    max-width: 800px;
    margin: 0 auto;
}
"""

with gr.Blocks(css=css, title="Screen Recorder Demo") as demo:
    gr.HTML("""
    <h1 style='text-align: center'>
        Gradio Screen Recorder Component Demo
    </h1>
    """)
    
    with gr.Row():
        with gr.Column():
            recorder = ScreenRecorder(
                audio_enabled=True,
                webcam_overlay=True,  # Disabled for now
                webcam_position="top-left",
                recording_format="webm",
                max_duration=60,
                label="Screen Recorder"
            )
        
        with gr.Column():
            output_video = gr.Video(label="Recorded Video")
    
    # Event handler
    recorder.change(
        fn=handle_recording,
        inputs=recorder,
        outputs=output_video
    )

if __name__ == "__main__":
    demo.launch()

```

## `ScreenRecorder`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>audio_enabled</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>webcam_overlay</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>webcam_position</code></td>
<td align="left" style="width: 25%;">

```python
"top-left" | "top-right" | "bottom-left" | "bottom-right"
```

</td>
<td align="left"><code>"bottom-right"</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>recording_format</code></td>
<td align="left" style="width: 25%;">

```python
str
```

</td>
<td align="left"><code>"webm"</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>max_duration</code></td>
<td align="left" style="width: 25%;">

```python
typing.Optional[int][int, None]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">None</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `record_start` |  |
| `record_stop` |  |
| `stream_update` |  |
| `change` |  |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.



 ```python
 def predict(
     value: typing.Optional[
    gradio_screenrecorder.screenrecorder.ScreenRecorderData
][ScreenRecorderData, None]
 ) -> Unknown:
     return value
 ```
 

## `ScreenRecorderData`
```python
class ScreenRecorderData(GradioModel):
    video: Optional[FileData] = None
    duration: Optional[float] = None
    audio_enabled: bool = True
    status: Literal["recording", "stopped", "error"] = (
        "stopped"
    )

    class Config:
        json_encoders = {
            FileData: lambda v: v.model_dump()
            if v
            else None
        }
```
