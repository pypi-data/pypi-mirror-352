
import gradio as gr
from app import demo as app
import os

_docs = {'ScreenRecorder': {'description': 'Custom Gradio component for comprehensive screen recording functionality.', 'members': {'__init__': {'audio_enabled': {'type': 'bool', 'default': 'True', 'description': None}, 'webcam_overlay': {'type': 'bool', 'default': 'False', 'description': None}, 'webcam_position': {'type': '"top-left" | "top-right" | "bottom-left" | "bottom-right"', 'default': '"bottom-right"', 'description': None}, 'recording_format': {'type': 'str', 'default': '"webm"', 'description': None}, 'max_duration': {'type': 'typing.Optional[int][int, None]', 'default': 'None', 'description': None}, 'interactive': {'type': 'bool', 'default': 'True', 'description': None}}, 'postprocess': {}, 'preprocess': {'return': {'type': 'typing.Optional[\n    gradio_screenrecorder.screenrecorder.ScreenRecorderData\n][ScreenRecorderData, None]', 'description': None}, 'value': None}}, 'events': {'record_start': {'type': None, 'default': None, 'description': ''}, 'record_stop': {'type': None, 'default': None, 'description': ''}, 'stream_update': {'type': None, 'default': None, 'description': ''}, 'change': {'type': None, 'default': None, 'description': ''}}}, '__meta__': {'additional_interfaces': {'ScreenRecorderData': {'source': 'class ScreenRecorderData(GradioModel):\n    video: Optional[FileData] = None\n    duration: Optional[float] = None\n    audio_enabled: bool = True\n    status: Literal["recording", "stopped", "error"] = (\n        "stopped"\n    )\n\n    class Config:\n        json_encoders = {\n            FileData: lambda v: v.model_dump()\n            if v\n            else None\n        }'}}, 'user_fn_refs': {'ScreenRecorder': ['ScreenRecorderData']}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_screenrecorder`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

Screen Recorder Gradio Custom Component
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_screenrecorder
```

## Usage

```python
import gradio as gr
from gradio_screenrecorder import ScreenRecorder

def handle_recording(recording_data):
    \"\"\"Handle recorded video data\"\"\"
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


css = \"\"\"
.screen-recorder-demo {
    max-width: 800px;
    margin: 0 auto;
}
\"\"\"

with gr.Blocks(css=css, title="Screen Recorder Demo") as demo:
    gr.HTML(\"\"\"
    <h1 style='text-align: center'>
        Gradio Screen Recorder Component Demo
    </h1>
    \"\"\")
    
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
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `ScreenRecorder`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["ScreenRecorder"]["members"]["__init__"], linkify=['ScreenRecorderData'])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["ScreenRecorder"]["events"], linkify=['Event'])




    gr.Markdown("""

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
""", elem_classes=["md-custom", "ScreenRecorder-user-fn"], header_links=True)




    code_ScreenRecorderData = gr.Markdown("""
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
```""", elem_classes=["md-custom", "ScreenRecorderData"], header_links=True)

    demo.load(None, js=r"""function() {
    const refs = {
            ScreenRecorderData: [], };
    const user_fn_refs = {
          ScreenRecorder: ['ScreenRecorderData'], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
