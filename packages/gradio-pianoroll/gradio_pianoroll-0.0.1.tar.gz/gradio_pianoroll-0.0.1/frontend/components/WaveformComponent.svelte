<!--
  WaveformComponent.svelte
  Displays audio waveform visualization below the piano roll grid
-->
<script lang="ts">
  import { onMount, onDestroy, afterUpdate } from 'svelte';
  import { audioEngine } from '../utils/audioEngine';

  // Props
  export let width = 880;
  export let height = 80;
  export let horizontalScroll = 0;
  export let pixelsPerBeat = 80;
  export let tempo = 120;
  export let opacity = 0.7;
  export let top = 0; // Add position prop

  // Canvas references
  let canvasElement: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null = null;

  // Animation state
  let animationId: number | null = null;
  let isRendered = false;

  // Color settings
  const WAVEFORM_COLOR = '#4287f5';
  const BACKGROUND_COLOR = 'rgba(30, 30, 30, 0.4)';

  // Initialize canvas
  function initCanvas() {
    if (!canvasElement) return;

    ctx = canvasElement.getContext('2d');
    if (!ctx) return;

    // Set up high-DPI canvas if needed
    const dpr = window.devicePixelRatio || 1;
    canvasElement.width = width * dpr;
    canvasElement.height = height * dpr;
    ctx.scale(dpr, dpr);

    canvasElement.style.width = `${width}px`;
    canvasElement.style.height = `${height}px`;

    // Draw initial empty waveform
    drawEmptyWaveform();
  }

  // Draw empty waveform background
  function drawEmptyWaveform() {
    if (!ctx) return;

    ctx.clearRect(0, 0, width, height);

    // Draw background
    ctx.fillStyle = BACKGROUND_COLOR;
    ctx.fillRect(0, 0, width, height);

    // Draw center line
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, height / 2);
    ctx.lineTo(width, height / 2);
    ctx.stroke();
  }

  // Draw waveform from audio buffer
  function drawWaveform() {
    if (!ctx) return;

    // Get rendered buffer from audio engine
    const buffer = audioEngine.getRenderedBuffer();
    if (!buffer) {
      drawEmptyWaveform();
      return;
    }

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw background
    ctx.fillStyle = BACKGROUND_COLOR;
    ctx.fillRect(0, 0, width, height);

    // Get audio data (use first channel)
    const channelData = buffer.getChannelData(0);
    const bufferLength = channelData.length;

    // Calculate total duration in seconds
    const totalSeconds = buffer.duration;
    // Calculate total length in pixels
    const totalPixels = (tempo / 60) * pixelsPerBeat * totalSeconds;
    // Calculate samples per pixel
    const samplesPerPixel = bufferLength / totalPixels;

    // Calculate visible region based on scroll position
    const startSample = Math.floor(horizontalScroll * samplesPerPixel);
    const endSample = Math.min(bufferLength, Math.floor((horizontalScroll + width) * samplesPerPixel));

    // Draw waveform
    ctx.strokeStyle = WAVEFORM_COLOR;
    ctx.lineWidth = 1.5;
    ctx.beginPath();

    // Map audio samples to canvas coordinates
    const centerY = height / 2;
    let lastX = -1;
    let lastMaxY = centerY;
    let lastMinY = centerY;

    for (let x = 0; x < width; x++) {
      const pixelStartSample = Math.floor((x + horizontalScroll) * samplesPerPixel);
      const pixelEndSample = Math.floor((x + 1 + horizontalScroll) * samplesPerPixel);

      // Find min and max sample values in this pixel column
      let min = 0;
      let max = 0;

      for (let i = pixelStartSample; i < pixelEndSample && i < bufferLength; i++) {
        if (i < 0) continue;

        const sample = channelData[i];
        if (sample < min) min = sample;
        if (sample > max) max = sample;
      }

      // Map sample values to y-coordinates
      const minY = centerY + min * centerY * 0.9;
      const maxY = centerY + max * centerY * 0.9;

      // Only draw if different from last pixel to optimize performance
      if (x === 0 || lastX !== x - 1 || lastMinY !== minY || lastMaxY !== maxY) {
        if (x === 0 || lastX !== x - 1) {
          ctx.moveTo(x, minY);
        }

        // Draw vertical line from min to max
        ctx.lineTo(x, minY);
        ctx.lineTo(x, maxY);

        lastX = x;
        lastMinY = minY;
        lastMaxY = maxY;
      }
    }

    ctx.stroke();

    // Draw center line
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, height / 2);
    ctx.lineTo(width, height / 2);
    ctx.stroke();

    isRendered = true;
  }

  // Draw waveform from realtime analyzer data (when playing)
  function drawRealtimeWaveform() {
    if (!ctx || !audioEngine.isCurrentlyPlaying()) {
      if (animationId) {
        cancelAnimationFrame(animationId);
        animationId = null;
      }
      return;
    }

    // Get analyzer data
    const dataArray = audioEngine.getWaveformData();
    if (!dataArray) return;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw background
    ctx.fillStyle = BACKGROUND_COLOR;
    ctx.fillRect(0, 0, width, height);

    // Draw center line
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, height / 2);
    ctx.lineTo(width, height / 2);
    ctx.stroke();

    // Draw waveform
    ctx.beginPath();
    ctx.strokeStyle = WAVEFORM_COLOR;
    ctx.lineWidth = 1.5;

    const sliceWidth = width / dataArray.length;
    let x = 0;

    for (let i = 0; i < dataArray.length; i++) {
      const v = dataArray[i];
      const y = (v * height / 2) + height / 2;

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    ctx.stroke();

    // Continue animation
    animationId = requestAnimationFrame(drawRealtimeWaveform);
  }

  // Watch for playback state changes
  function setupPlaybackListeners() {
    const checkPlayback = () => {
      if (audioEngine.isCurrentlyPlaying() && !animationId) {
        // Start realtime visualization
        animationId = requestAnimationFrame(drawRealtimeWaveform);
      }
    };

    // Check periodically for playback state changes
    const intervalId = setInterval(checkPlayback, 500);

    return () => {
      clearInterval(intervalId);
      if (animationId) {
        cancelAnimationFrame(animationId);
        animationId = null;
      }
    };
  }

  // Handle window resize
  function handleResize() {
    initCanvas();
    drawWaveform();
  }

  // Update waveform when props change
  $: if (ctx && (width || height || horizontalScroll || pixelsPerBeat || tempo)) {
    drawWaveform();
  }

  onMount(() => {
    initCanvas();
    const cleanup = setupPlaybackListeners();

    // Add window resize listener
    window.addEventListener('resize', handleResize);

    return () => {
      cleanup();
      window.removeEventListener('resize', handleResize);
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  });

  afterUpdate(() => {
    if (canvasElement && ctx) {
      drawWaveform();
    }
  });

  onDestroy(() => {
    if (animationId) {
      cancelAnimationFrame(animationId);
    }
  });

  // Public method to force redraw (called from parent when audio is rendered)
  export function forceRedraw() {
    drawWaveform();
  }
</script>

<div class="waveform-container" style="opacity: {opacity}; top: {top}px;">
  <canvas
    bind:this={canvasElement}
    width={width}
    height={height}
    class="waveform-canvas"
  ></canvas>
</div>

<style>
  .waveform-container {
    position: absolute;
    z-index: 2; /* Above grid, below notes */
    pointer-events: none; /* Allow interactions to pass through */
    transition: opacity 0.3s ease;
  }

  .waveform-canvas {
    display: block;
  }
</style>
