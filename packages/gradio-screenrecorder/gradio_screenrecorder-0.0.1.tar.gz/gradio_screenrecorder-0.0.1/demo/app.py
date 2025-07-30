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
