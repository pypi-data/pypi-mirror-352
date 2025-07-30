<script lang="ts">
    export let value: any;
    
    function formatDuration(duration: number): string {
        const minutes = Math.floor(duration / 60);
        const seconds = Math.floor(duration % 60);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
</script>

<div class="example-container">
    {#if value && value.video}
        <div class="video-thumbnail">
            <video 
                src={value.video.path} 
                controls={false}
                muted
                style="width: 100%; height: 60px; object-fit: cover;"
            >
            </video>
            <div class="overlay">
                <span class="duration">
                    {value.duration ? formatDuration(value.duration) : 'Recording'}
                </span>
                <span class="format">
                    {value.video.orig_name?.split('.').pop()?.toUpperCase() || 'VIDEO'}
                </span>
            </div>
        </div>
    {:else}
        <div class="placeholder">
            📹 Screen Recording
        </div>
    {/if}
</div>

<style>
    .example-container {
        width: 100%;
        height: 80px;
        border-radius: 4px;
        overflow: hidden;
        position: relative;
    }
    
    .video-thumbnail {
        position: relative;
        width: 100%;
        height: 100%;
    }
    
    .overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(transparent, rgba(0,0,0,0.7));
        padding: 4px 8px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }
    
    .duration, .format {
        color: white;
        font-size: 10px;
        font-weight: bold;
    }
    
    .placeholder {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        background: #f0f0f0;
        color: #666;
        font-size: 12px;
    }
</style>
