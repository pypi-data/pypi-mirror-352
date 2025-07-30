<script lang="ts">
    import { onMount, onDestroy, createEventDispatcher } from 'svelte';
    import { Block } from '@gradio/atoms';
    import { StatusTracker } from '@gradio/statustracker';
    import type { LoadingStatus } from "@gradio/statustracker";
    import type { Gradio } from "@gradio/utils";
    import fixWebmDuration from 'fix-webm-duration';
    
    // Type definitions
    interface MediaRecorderOptions {
        mimeType?: string;
        audioBitsPerSecond?: number;
        videoBitsPerSecond?: number;
        bitsPerSecond?: number;
    }
    
    interface MediaTrackConstraints {
        displaySurface?: 'browser' | 'monitor' | 'window';
        cursor?: 'always' | 'motion' | 'never';
    }

    // Type definitions
    interface RecordingData {
        video: string;
        duration: number;
        audio_enabled?: boolean;
        status?: string;
        orig_name?: string;
        size?: number | null;
        data?: string; // Base64 encoded data for Gradio
        name?: string;  // Alias for orig_name for Gradio compatibility
        is_file?: boolean;
        type?: string;  // MIME type of the recording
    }

    interface Position {
        x: number;
        y: number;
    }

    // Event types for the component
    type EventMap = {
        'error': { message: string; error: string };
        'recording-started': void;
        'recording-stopped': RecordingData;
        'record_stop': RecordingData;
        'change': RecordingData;
        'webcam-error': { message: string; error: string };
    };

    // Component props with proper types and defaults
    export let gradio: Gradio<any>;
    export let value: Partial<RecordingData> | null = null;
    export const elem_id = ''; // Marked as const since it's not modified
    export let elem_classes: string[] = [];
    export let scale: number | null = null;
    export let min_width: number | null = null;
    export let visible = true;
    export let interactive = true;
    export let loading_status: LoadingStatus | null = null;
    export let audio_enabled = false;
    export let webcam_overlay = false;
    export let webcam_position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' = 'bottom-right';
    export let recording_format: 'webm' | 'mp4' | 'gif' = 'webm';
    export let max_duration: number | null = null;
    
    // Computed styles for the container
    let containerStyle = '';
    
    // Component methods interface
    interface ComponentMethods {
        startRecording: () => Promise<void>;
        stopRecording: () => void;
        togglePause: () => void;
        cleanup: () => void;
    }
    
    // Component state with explicit types and initial values
    let isPaused = false;
    let isRecording = false;
    let recordingTime = 0;
    let recordingTimer: number | null = null;
    let recordedChunks: Blob[] = [];
    
    // Media streams and elements
    let screenStream: MediaStream | null = null;
    let webcamStream: MediaStream | null = null;
    let combinedStream: MediaStream | null = null;
    let canvas: HTMLCanvasElement | null = null;
    let ctx: CanvasRenderingContext2D | null = null;
    let animationFrameId: number | null = null;
    let previewVideo: HTMLVideoElement | null = null;
    let webcamVideo: HTMLVideoElement | null = null;
    let recordingStartTime = 0;
    let mediaRecorder: MediaRecorder | null = null;
    
    // Internal video elements
    let webcamVideoInternal: HTMLVideoElement | null = null;
    let screenVideoInternal: HTMLVideoElement | null = null;
    
    // Bind canvas element
    function bindCanvas(node: HTMLCanvasElement) {
        canvas = node;
        if (canvas) {
            const context = canvas.getContext('2d', { willReadFrequently: true });
            if (context) {
                ctx = context;
                // Set canvas dimensions with null checks
                const width = canvas.offsetWidth;
                const height = canvas.offsetHeight;
                if (width && height) {
                    canvas.width = width;
                    canvas.height = height;
                }
            }
        }
        return {
            destroy() {
                canvas = null;
                ctx = null;
            }
        };
    }
    
    // Canvas binding is now handled by the bindCanvas function
    
    // Configuration
    const webcam_size = 200;
    const webcam_border = 10;
    const webcam_radius = '50%';
    
    // Ensure max_duration has a default value if null
    $: effectiveMaxDuration = max_duration ?? 0;
    
    // Computed styles for the container
    $: containerStyle = [
        scale !== null ? `--scale: ${scale};` : '',
        min_width !== null ? `min-width: ${min_width}px;` : ''
    ].filter(Boolean).join(' ');
    
    onDestroy(() => {
        if (isRecording) {
            componentMethods.stopRecording();
        }
        componentMethods.cleanup();
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
    });
    
    // Component state and props are already declared above
    
    // Event dispatcher with proper typing
    const dispatch = createEventDispatcher<EventMap>();
    
    // Type guard for error handling
    function isErrorWithMessage(error: unknown): error is Error {
        return error instanceof Error;
    }

    // Component methods implementation
    const componentMethods: ComponentMethods = {
        startRecording: async (): Promise<void> => {
            if (isRecording) return;
            isRecording = true;
            recordedChunks = [];
            recordingTime = 0;
            
            try {
                // Composite screen and optional webcam overlay via hidden canvas
                const screenStreamCapture = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false });
                screenStream = screenStreamCapture;
                // Assign to hidden video for composition
                if (screenVideoInternal) {
                    screenVideoInternal.srcObject = screenStreamCapture;
                    await screenVideoInternal.play().catch(() => {});
                }
                let captureStream: MediaStream;
                if (webcam_overlay && webcamVideoInternal && canvas && ctx) {
                    try {
                        webcamStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
                        webcamVideoInternal.srcObject = webcamStream;
                        await webcamVideoInternal.play().catch(() => {});
                        // Resize canvas to match screen video
                        canvas.width = screenVideoInternal!.videoWidth;
                        canvas.height = screenVideoInternal!.videoHeight;
                        const overlaySize = Math.min(canvas.width, canvas.height) / 4;
                        const posMap: Record<string, [number, number]> = {
                            'top-left': [10, 10],
                            'top-right': [canvas.width - overlaySize - 10, 10],
                            'bottom-left': [10, canvas.height - overlaySize - 10],
                            'bottom-right': [canvas.width - overlaySize - 10, canvas.height - overlaySize - 10]
                        };
                        const [ox, oy] = posMap[webcam_position];
                        function draw() {
                            ctx!.drawImage(screenVideoInternal!, 0, 0, canvas.width, canvas.height);
                            ctx!.drawImage(webcamVideoInternal!, ox, oy, overlaySize, overlaySize);
                            animationFrameId = requestAnimationFrame(draw);
                        }
                        draw();
                        const canvasStream = canvas.captureStream(30);
                        const audioTracks = audio_enabled
                            ? (await navigator.mediaDevices.getUserMedia({ audio: true })).getAudioTracks()
                            : screenStreamCapture.getAudioTracks();
                        combinedStream = new MediaStream([...canvasStream.getVideoTracks(), ...audioTracks]);
                        captureStream = combinedStream;
                    } catch (err) {
                        console.warn('Webcam overlay failed, falling back to screen only', err);
                        captureStream = screenStreamCapture;
                    }
                } else {
                    // No overlay: combine audio if enabled with screen
                    const audioTracks = audio_enabled
                        ? (await navigator.mediaDevices.getUserMedia({ audio: true })).getAudioTracks()
                        : screenStreamCapture.getAudioTracks();
                    combinedStream = new MediaStream([...screenStreamCapture.getVideoTracks(), ...audioTracks]);
                    captureStream = combinedStream;
                }
                
                // Handle track ended event
                screenStreamCapture.getVideoTracks()[0].onended = () => {
                    if (isRecording) {
                        componentMethods.stopRecording();
                    }
                };
                
                // Start recording
                const options: MediaRecorderOptions = {
                    mimeType: recording_format === 'webm' ? 'video/webm;codecs=vp9' : 'video/mp4'
                };
                
                mediaRecorder = new MediaRecorder(captureStream, options);
                mediaRecorder.ondataavailable = handleDataAvailable;
                mediaRecorder.onstop = handleRecordingStop;
                mediaRecorder.start();
                
                recordingStartTime = Date.now();
                updateRecordingTime();
                
                dispatch('recording-started');
            } catch (error) {
                isRecording = false;
                if (isErrorWithMessage(error)) {
                    dispatch('error', { 
                        message: 'Failed to start recording', 
                        error: error.message
                    });
                }
            }
        },
        
        stopRecording: (): void => {
            if (!isRecording || !mediaRecorder) return;
            
            try {
                mediaRecorder.stop();
                isRecording = false;
                
                // Stop all tracks
                [screenStream, webcamStream, combinedStream].forEach(stream => {
                    if (stream) {
                        stream.getTracks().forEach(track => track.stop());
                    }
                });
                
                if (recordingTimer) {
                    clearTimeout(recordingTimer);
                    recordingTimer = null;
                }
                
                const recordingData: RecordingData = {
                    video: '',
                    duration: recordingTime / 1000,
                    audio_enabled: audio_enabled,
                    status: 'completed'
                };
                
                dispatch('recording-stopped', recordingData);
                dispatch('record_stop', recordingData);
                dispatch('change', recordingData);
            } catch (error) {
                isRecording = false;
                if (isErrorWithMessage(error)) {
                    dispatch('error', { 
                        message: 'Error stopping recording', 
                        error: error.message
                    });
                }
            }
        },
        
        togglePause: (): void => {
            if (!mediaRecorder) return;
            
            isPaused = !isPaused;
            
            if (isPaused) {
                mediaRecorder.pause();
                if (recordingTimer) {
                    clearTimeout(recordingTimer);
                    recordingTimer = null;
                }
            } else {
                mediaRecorder.resume();
                updateRecordingTime();
            }
            if (isPaused) {
                // Pause logic
            } else {
                // Resume logic
            }
        },
        
        cleanup: (): void => {
            // Stop all media streams
            [screenStream, webcamStream, combinedStream].forEach(stream => {
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
            });
            
            // Clear media recorder
            if (mediaRecorder) {
                if (mediaRecorder.state !== 'inactive') {
                    mediaRecorder.stop();
                }
                mediaRecorder = null;
            }
            
            // Clear canvas
            if (ctx) {
                ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
            }
            
            // Reset state
            isRecording = false;
            isPaused = false;
            recordingTime = 0;
            recordedChunks = [];
            
            // Clear timers
            if (recordingTimer) {
                clearInterval(recordingTimer);
                recordingTimer = null;
            }
            
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
                animationFrameId = null;
            }
        }
    };

    // Handle data available event
    function handleDataAvailable(event: BlobEvent): void {
        if (event.data && event.data.size > 0) {
            recordedChunks.push(event.data);
        }
    }
    
    // Handle recording stop
    function handleRecordingStop(): void {
        if (recordedChunks.length === 0) {
            console.warn('No recording data available');
            return;
        }
        
        const mimeType = recording_format === 'webm' ? 'video/webm' : 'video/mp4';
        const blob = new Blob(recordedChunks, { type: mimeType });
        const url = URL.createObjectURL(blob);
        
        console.log('Recording stopped. Blob size:', blob.size, 'bytes');
        
        // Create a file reader to read the blob as base64
        const reader = new FileReader();
        reader.onload = (e) => {
            const base64data = e.target?.result as string;
            // Extract the base64 data (remove the data URL prefix)
            const base64Content = base64data.split(',')[1];
            const fileName = `recording_${Date.now()}.${recording_format}`;
            
            // Dispatch event with recording data
            const recordingData: RecordingData = {
                video: url,
                duration: recordingTime,
                audio_enabled: audio_enabled,
                status: 'completed',
                size: blob.size > 0 ? blob.size : undefined,
                orig_name: fileName,
                name: fileName,  // Alias for Gradio compatibility
                is_file: true,
                type: mimeType,
                data: base64Content
            };
            
            console.log('Dispatching recording-stopped event');
            dispatch('recording-stopped', recordingData);
            dispatch('record_stop', recordingData);
            dispatch('change', recordingData);
            
            // Update the value prop to trigger re-render
            value = { ...value, ...recordingData };
        };
        
        reader.onerror = (error) => {
            console.error('Error reading blob:', error);
            dispatch('error', { 
                message: 'Failed to process recording', 
                error: 'Could not read recording data' 
            });
        };
        
        // Read the blob as data URL
        reader.readAsDataURL(blob);
    }
    
    // Update recording time
    function updateRecordingTime(): void {
        if (!isRecording) return;
        
        recordingTime = Math.floor((Date.now() - recordingStartTime) / 1000);
        
        // Check if max duration has been reached
        if (max_duration !== null && max_duration > 0 && recordingTime >= max_duration) {
            console.log('Max duration reached, stopping');
            componentMethods.stopRecording();
            return;
        }
        
        // Schedule the next update
        recordingTimer = window.setTimeout(updateRecordingTime, 1000);
    }
    
    function stopTimer(): void {
        if (recordingTimer) {
            clearTimeout(recordingTimer);
            recordingTimer = null;
        }
    }
    
    // Format time as MM:SS
    function formatTime(seconds: number): string {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    // Format file size in human-readable format
    function formatFileSize(bytes: number | string | null | undefined): string {
        if (bytes === null || bytes === undefined) return '0 B';
        const numBytes = Number(bytes);
        if (isNaN(numBytes) || numBytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(numBytes) / Math.log(k));
        return parseFloat((numBytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
</script>

<div class="screen-recorder-container {!visible ? 'invisible' : ''} {elem_classes.join(' ')}" style="{containerStyle}">
    {#if loading_status}
        <StatusTracker
            autoscroll={gradio.autoscroll}
            i18n={gradio.i18n}
            {...loading_status}
        />
    {/if}

    <div class="screen-recorder">
        <div class="controls">
            {#if !isRecording}
                <button 
                    class="record-btn start" 
                    on:click={componentMethods.startRecording}
                    disabled={!interactive}
                >
                    <span class="recording-icon">●</span> Start Recording
                </button>
            {:else}
                <button 
                    class="record-btn stop" 
                    on:click={componentMethods.stopRecording}
                >
                    <span class="stop-icon">■</span> Stop Recording
                </button>
                <span class="recording-time">
                    {formatTime(recordingTime)}
                </span>
                {#if max_duration}
                    <span class="max-duration">/ {formatTime(max_duration)}</span>
                {/if}
            {/if}
        </div>
        
        <!-- Live Preview - Always show when recording -->
        {#if isRecording}
            <div class="preview-container">
                <video 
                    bind:this={previewVideo}
                    class="preview-video"
                    autoplay
                    muted
                    playsinline
                    aria-label="Live preview"
                    on:loadedmetadata={() => {
                        if (previewVideo) {
                            previewVideo.play().catch(console.warn);
                        }
                    }}
                >
                    <track kind="captions" />
                </video>
                {#if webcam_overlay}
                    <video 
                        bind:this={webcamVideo}
                        class="webcam-overlay {webcam_position}"
                        style="width: 200px; height: 200px;"
                        autoplay
                        muted
                        playsinline
                        aria-label="Webcam overlay"
                    >
                        <track kind="captions" />
                    </video>
                {/if}
                <div class="recording-indicator">
                    <span class="pulse">●</span> RECORDING
                </div>
            </div>
        {/if}

            {#if value?.video}
                <div class="recording-preview" style="position: relative;">
                    {#if audio_enabled}
                        <div class="speaker-overlay">🔊</div>
                    {/if}
                    <video 
                        src={value.video}
                        controls
                        class="preview-video"
                        aria-label="Recording preview"
                        on:loadedmetadata
                        on:loadeddata
                        on:error={(e) => console.error('Video error:', e)}
                    >
                        <track kind="captions" />
                    </video>
                    <div class="recording-info">
                        <div>Duration: {value.duration ? value.duration.toFixed(1) : '0.0'}s</div>
                        {#if value.size}
                            <div>Size: {formatFileSize(value.size)}</div>
                        {/if}
                    </div>
                </div>
            {/if}

        <!-- Configuration Display -->
        <div class="config-info">
            <span>Audio: {audio_enabled ? '🔊' : '🔇'}</span>
            <span>Format: {recording_format.toUpperCase()}</span>
            {#if max_duration}
                <span>Max: {formatTime(max_duration)}</span>
            {/if}
        </div>
        
        <!-- Debug info -->
        {#if value}
            <div class="debug-info">
                <small>Last recording: {value.orig_name} ({Math.round(value.size / 1024)}KB)</small>
            </div>
        {/if}
    </div>
    <video bind:this={screenVideoInternal} hidden muted playsinline style="display:none"></video>
    {#if webcam_overlay}
        <video bind:this={webcamVideoInternal} hidden muted playsinline style="display:none"></video>
    {/if}
    <canvas bind:this={canvas} use:bindCanvas hidden style="display:none"></canvas>
</div>

<style>
    .screen-recorder-container {
        display: block;
        width: 100%;
        box-sizing: border-box;
    }
    
    .screen-recorder-container.invisible {
        display: none;
    }
    
    .screen-recorder {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        background: #f9f9f9;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .controls {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
        flex-wrap: wrap;
    }
    
    .record-btn {
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .record-btn.start {
        background: #4CAF50;
        color: white;
    }
    
    .record-btn.start:hover {
        background: #45a049;
    }
    
    .record-btn.stop {
        background: #f44336;
        color: white;
    }
    
    .record-btn.stop:hover {
        background: #da190b;
    }
    
    .record-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    .recording-time {
        font-family: 'Courier New', monospace;
        font-size: 18px;
        font-weight: bold;
        color: #f44336;
    }
    
    .max-duration {
        font-family: 'Courier New', monospace;
        font-size: 14px;
        color: #666;
    }
    

    .preview-container {
        position: relative;
        margin: 12px 0;
        border-radius: 6px;
        overflow: hidden;
        background: black;
        min-height: 200px;
    }
    
    .preview-video {
        width: 100%;
        max-height: 400px;
        display: block;
        object-fit: contain;
    }

    
    .recording-indicator {
        position: absolute;
        top: 10px;
        left: 10px;
        background: rgba(244, 67, 54, 0.9);
        color: white;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        animation: pulse 1s infinite;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .config-info {
        display: flex;
        gap: 8px;
        font-size: 12px;
        color: #666;
        margin-top: 8px;
        flex-wrap: wrap;
    }
    
    .config-info span {
        padding: 4px 8px;
        background: #e8e8e8;
        border-radius: 4px;
        border: 1px solid #ddd;
    }
    
    .debug-info {
        margin-top: 8px;
        padding: 8px;
        background: #e8f5e8;
        border-radius: 4px;
        border: 1px solid #c8e6c8;
    }
    
    .speaker-overlay {
        position: absolute;
        top: 8px;
        right: 8px;
        background: rgba(0,0,0,0.5);
        color: white;
        padding: 4px;
        border-radius: 4px;
        font-size: 14px;
        pointer-events: none;
    }
</style>
