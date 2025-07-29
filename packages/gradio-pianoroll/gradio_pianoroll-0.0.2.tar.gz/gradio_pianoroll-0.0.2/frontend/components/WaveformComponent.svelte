<!--
  WaveformComponent.svelte
  Displays audio waveform visualization below the piano roll grid
-->
<script lang="ts">
  import { onMount, onDestroy, afterUpdate } from 'svelte';
  import { AudioEngineManager } from '../utils/audioEngine';

  // Props
  export let width = 880;
  export let height = 80;
  export let horizontalScroll = 0;
  export let pixelsPerBeat = 80;
  export let tempo = 120;
  export let opacity = 0.7;
  export let top = 0; // Add position prop
  export let elem_id = '';  // 컴포넌트 ID

  // 백엔드 데이터 속성들
  export let audio_data: string | null = null;
  export let use_backend_audio: boolean = false;

  // 추가: curve_data에서 웨이브폼 데이터 지원
  export let curve_data: object | null = null;

  // 컴포넌트별 오디오 엔진 인스턴스
  $: audioEngine = AudioEngineManager.getInstance(elem_id || 'default');

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

    // Draw "No waveform" message
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('웨이브폼이 없습니다. "Synthesize Audio" 버튼을 클릭하세요.', width / 2, height / 2);
  }

  // Draw waveform from audio buffer
  function drawWaveform() {
    if (!ctx) return;

    // 1순위: 백엔드에서 미리 계산된 웨이브폼 데이터 사용
    if (curve_data && (curve_data as any).waveform_data) {
      drawPreCalculatedWaveform((curve_data as any).waveform_data);
      return;
    }

    // 2순위: 백엔드 오디오 버퍼 사용
    let buffer: AudioBuffer | null = null;
    if (use_backend_audio && backendAudioBuffer) {
      buffer = backendAudioBuffer;
    } else if (!use_backend_audio) {
      // Synthesizer Demo에서는 백엔드 데이터가 없으면 프론트엔드 렌더링 금지
      if (elem_id === "piano_roll_synth" && !audio_data && !(curve_data && (curve_data as any).waveform_data)) {
        drawEmptyWaveform();
        return;
      }

      // 프론트엔드 오디오 엔진 사용
      buffer = audioEngine.getRenderedBuffer();
    }

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
    ctx.strokeStyle = use_backend_audio ? '#4CAF50' : WAVEFORM_COLOR; // 백엔드 오디오는 녹색으로 표시
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

  // 백엔드에서 미리 계산된 웨이브폼 데이터로 그리기
  function drawPreCalculatedWaveform(waveformData: Array<{x: number, min: number, max: number}>) {
    if (!ctx || !waveformData || waveformData.length === 0) {
      drawEmptyWaveform();
      return;
    }

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

    // Draw waveform from pre-calculated data
    ctx.strokeStyle = '#4CAF50'; // 백엔드 웨이브폼은 녹색으로 표시
    ctx.lineWidth = 1.5;
    ctx.beginPath();

    const centerY = height / 2;
    let hasDrawnAnyPoint = false;

    // 웨이브폼 데이터를 x 좌표 기준으로 정렬
    const sortedData = [...waveformData].sort((a, b) => a.x - b.x);

    for (let screenX = 0; screenX < width; screenX++) {
      // 스크롤 위치를 고려한 데이터 포인트 찾기
      const dataX = screenX + horizontalScroll;

      // 해당 위치에 가장 가까운 웨이브폼 데이터 찾기
      const dataPoint = sortedData.find(point => Math.abs(point.x - dataX) < 1);

      if (dataPoint) {
        // Map sample values to y-coordinates (-1 to 1 범위를 canvas 높이로 매핑)
        const minY = centerY + dataPoint.min * centerY * 0.9;
        const maxY = centerY + dataPoint.max * centerY * 0.9;

        if (!hasDrawnAnyPoint) {
          ctx.moveTo(screenX, minY);
          hasDrawnAnyPoint = true;
        }

        // Draw vertical line from min to max
        ctx.lineTo(screenX, minY);
        ctx.lineTo(screenX, maxY);
      }
    }

    if (hasDrawnAnyPoint) {
      ctx.stroke();
      console.log(`웨이브폼 그리기 완료: ${waveformData.length}개 포인트 사용`);
    } else {
      console.log("웨이브폼 데이터가 현재 화면 영역에 없음");
    }

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
  $: if (ctx && (width || height || horizontalScroll || pixelsPerBeat || tempo || curve_data)) {
    drawWaveform();
  }

  // 백엔드 오디오 데이터 관련
  let backendAudioBuffer: AudioBuffer | null = null;
  let audioContextForDecoding: AudioContext | null = null;

  // 백엔드 오디오 데이터 디코딩
  async function decodeBackendAudio(audioData: string) {
    if (!audioData) return;

    try {
      if (!audioContextForDecoding) {
        audioContextForDecoding = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      let arrayBuffer: ArrayBuffer;

      if (audioData.startsWith('data:')) {
        // Base64 데이터 처리
        const base64Data = audioData.split(',')[1];
        const binaryString = atob(base64Data);
        arrayBuffer = new ArrayBuffer(binaryString.length);
        const uint8Array = new Uint8Array(arrayBuffer);
        for (let i = 0; i < binaryString.length; i++) {
          uint8Array[i] = binaryString.charCodeAt(i);
        }
      } else {
        // URL 처리
        const response = await fetch(audioData);
        arrayBuffer = await response.arrayBuffer();
      }

      backendAudioBuffer = await audioContextForDecoding.decodeAudioData(arrayBuffer);

      // 디코딩 완료 후 웨이브폼 다시 그리기
      drawWaveform();
    } catch (error) {
      console.error('Error decoding backend audio:', error);
      backendAudioBuffer = null;
    }
  }

  // 백엔드 오디오 데이터 변경 감지
  $: if (use_backend_audio && audio_data) {
    decodeBackendAudio(audio_data);
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
