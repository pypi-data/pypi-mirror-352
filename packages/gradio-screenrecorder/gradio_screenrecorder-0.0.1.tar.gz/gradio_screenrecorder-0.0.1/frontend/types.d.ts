// Extend the Window interface
declare global {
    interface Window {
        requestAnimationFrame(callback: FrameRequestCallback): number;
        cancelAnimationFrame(handle: number): void;
        MediaRecorder: typeof MediaRecorder;
    }
    
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
}

// Export the types
export {};
