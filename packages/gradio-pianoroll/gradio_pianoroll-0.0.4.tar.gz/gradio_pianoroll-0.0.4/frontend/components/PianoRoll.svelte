<!--
  Main PianoRoll component that integrates all subcomponents.
  This component serves as the container for the entire piano roll interface.
  Now with playback functionality using Flicks timing, waveform visualization, and playhead.
-->
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import Toolbar from './Toolbar.svelte';
  import KeyboardComponent from './KeyboardComponent.svelte';
  import GridComponent from './GridComponent.svelte';
  import TimeLineComponent from './TimeLineComponent.svelte';
  import WaveformComponent from './WaveformComponent.svelte';
  import PlayheadComponent from './PlayheadComponent.svelte';
  import DebugComponent from './DebugComponent.svelte';
  import { AudioEngineManager } from '../utils/audioEngine';
  import { beatsToFlicks, flicksToBeats, formatFlicks } from '../utils/flicks';
  import { createEventDispatcher } from 'svelte';

  // 이벤트 디스패처 생성
  const dispatch = createEventDispatcher();

  // Props
  export let width = 1000;  // Total width of the piano roll
  export let height = 600;  // Total height of the piano roll
  export let keyboardWidth = 120; // Width of the keyboard component
  export let timelineHeight = 40; // Height of the timeline component
  export let elem_id = '';  // 컴포넌트 고유 ID

  // 백엔드 데이터 속성들
  export let audio_data: string | null = null;
  export let curve_data: object | null = null;
  export let segment_data: Array<any> | null = null;
  export let use_backend_audio: boolean = false;

  // use_backend_audio prop 변경 감지
  $: {
    console.log("🔊 PianoRoll: use_backend_audio prop changed to:", use_backend_audio);
    console.log("🔊 PianoRoll: audio_data present:", !!audio_data);
    console.log("🔊 PianoRoll: elem_id:", elem_id);
  }

  // Shared state
  export let notes: Array<{
    id: string,
    start: number,
    duration: number,
    startFlicks?: number,      // Optional for backward compatibility
    durationFlicks?: number,   // Optional for backward compatibility
    startSeconds?: number,     // Optional - seconds timing
    durationSeconds?: number,  // Optional - seconds timing
    endSeconds?: number,       // Optional - end time in seconds
    startBeats?: number,       // Optional - beats timing
    durationBeats?: number,    // Optional - beats timing
    startTicks?: number,       // Optional - MIDI ticks timing
    durationTicks?: number,    // Optional - MIDI ticks timing
    startSample?: number,      // Optional - sample timing
    durationSamples?: number,  // Optional - sample timing
    pitch: number,
    velocity: number,
    lyric?: string,
    phoneme?: string
  }> = [];

  // Settings
  export let tempo = 120;
  export let timeSignature = { numerator: 4, denominator: 4 };
  export let editMode = 'select'; // 'select', 'draw', 'erase', etc.
  export let snapSetting = '1/4'; // Default snap setting: 1/4

  // Audio metadata
  export let sampleRate = 44100; // Audio sample rate
  export let ppqn = 480;         // MIDI pulses per quarter note

  // Playback state
  let isPlaying = false;
  let isRendering = false;
  let currentFlicks = 0;
  let waveformOpacity = 0.7; // Initial opacity for waveform

  // References to components
  let waveformComponent: any; // Reference to waveform component

  // Zoom level (pixels per beat) - now controlled from parent
  export let pixelsPerBeat = 80;
  const MIN_PIXELS_PER_BEAT = 40; // Minimum zoom level
  const MAX_PIXELS_PER_BEAT = 200; // Maximum zoom level
  const ZOOM_STEP = 20; // Zoom step size (must be integer to avoid coordinate calculation errors)

  // Zoom in function
  function zoomIn() {
    if (pixelsPerBeat < MAX_PIXELS_PER_BEAT) {
      pixelsPerBeat += ZOOM_STEP;
      dispatchDataChange();
    }
  }

  // Zoom out function
  function zoomOut() {
    if (pixelsPerBeat > MIN_PIXELS_PER_BEAT) {
      pixelsPerBeat -= ZOOM_STEP;
      dispatchDataChange();
    }
  }

  // Scroll positions
  let horizontalScroll = 0;
  let verticalScroll = 0;

  // References to DOM elements
  let containerElement: HTMLDivElement;

  // 컴포넌트별 오디오 엔진 인스턴스
  $: audioEngine = AudioEngineManager.getInstance(elem_id || 'default');

  // Backend audio playback state
  let backendAudioContext: AudioContext | null = null;
  let backendAudioBuffer: AudioBuffer | null = null;
  let backendAudioSource: AudioBufferSourceNode | null = null;
  let backendPlayStartTime = 0;
  let backendPlayheadInterval: number | null = null;

  // 전체 데이터 변경 이벤트 발생
  function dispatchDataChange() {
    dispatch('dataChange', {
      notes,
      tempo,
      timeSignature,
      editMode,
      snapSetting,
      pixelsPerBeat,
      sampleRate,
      ppqn
    });
  }

  // 노트만 변경 이벤트 발생
  function dispatchNoteChange() {
    dispatch('noteChange', {
      notes
    });
  }

  // Sync scroll handlers
  function handleGridScroll(event: CustomEvent) {
    horizontalScroll = event.detail.horizontalScroll;
    verticalScroll = event.detail.verticalScroll;
    // The scroll values are now reactively bound to the other components
    // and will trigger updates when they change
  }

  // Settings handlers
  function handleTimeSignatureChange(event: CustomEvent) {
    timeSignature = event.detail;
    dispatchDataChange();
  }

  function handleEditModeChange(event: CustomEvent) {
    editMode = event.detail;
    dispatchDataChange();
  }

  function handleSnapChange(event: CustomEvent) {
    snapSetting = event.detail;
    dispatchDataChange();
  }

  // Handle zoom changes from toolbar
  function handleZoomChange(event: CustomEvent) {
    const { action } = event.detail;
    if (action === 'zoom-in') {
      zoomIn();
    } else if (action === 'zoom-out') {
      zoomOut();
    }
  }

  // Calculate total length in beats
  $: totalLengthInBeats = 32 * timeSignature.numerator; // 32 measures

  // Playback control functions
  async function renderAudio() {
    // 백엔드 오디오를 사용하는 경우 렌더링하지 않음
    if (use_backend_audio) {
      console.log("🎵 Backend audio enabled - skipping frontend rendering");
      return;
    }

    // Synthesizer Demo에서는 초기 자동 렌더링 방지
    // elem_id가 "piano_roll_synth"인 경우 사용자가 명시적으로 요청할 때만 렌더링
    if (elem_id === "piano_roll_synth" && !(curve_data && (curve_data as any).waveform_data) && !audio_data) {
      console.log("Synthesizer Demo: 자동 렌더링 건너뛰기 - 백엔드 오디오 생성 대기");
      return;
    }

    isRendering = true;
    try {
      // Initialize component-specific audio engine
      audioEngine.initialize();

      // Render the notes to an audio buffer
      // Pass pixelsPerBeat to ensure proper alignment between waveform and notes
      await audioEngine.renderNotes(notes, tempo, totalLengthInBeats, pixelsPerBeat);

      // Update waveform visualization
      if (waveformComponent) {
        waveformComponent.forceRedraw();
      }
    } catch (error) {
      console.error('Error rendering audio:', error);
    } finally {
      isRendering = false;
    }
  }

  async function initBackendAudio() {
    console.log("🎵 Initializing backend audio context...");
    if (!backendAudioContext) {
      try {
        backendAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        console.log("✅ Backend audio context created successfully");
        console.log("Initial audio context state:", backendAudioContext.state);

        // AudioContext가 suspended 상태라면 resume (사용자 상호작용 후에만 가능)
        if (backendAudioContext.state === 'suspended') {
          console.log("🔄 Resuming suspended audio context...");
          await backendAudioContext.resume();
          console.log("✅ Audio context resumed, new state:", backendAudioContext.state);
        }
      } catch (error) {
        console.error("❌ Failed to create backend audio context:", error);
        throw error;
      }
    } else {
      console.log("✅ Backend audio context already exists, state:", backendAudioContext.state);

      // 기존 컨텍스트가 있어도 suspended 상태일 수 있음
      if (backendAudioContext.state === 'suspended') {
        console.log("🔄 Resuming existing suspended audio context...");
        try {
          await backendAudioContext.resume();
          console.log("✅ Audio context resumed, new state:", backendAudioContext.state);
        } catch (error) {
          console.error("❌ Failed to resume audio context:", error);
          throw error;
        }
      }
    }
  }

  async function decodeBackendAudio() {
    console.log("🎵 Starting backend audio decoding...");
    console.log("Audio data length:", audio_data ? audio_data.length : 0);
    console.log("Audio data preview:", audio_data ? audio_data.substring(0, 50) + "..." : "null");

    if (!audio_data || !backendAudioContext) {
      console.log("❌ Missing audio data or context for decoding");
      return null;
    }

    try {
      let arrayBuffer: ArrayBuffer;

      if (audio_data.startsWith('data:')) {
        console.log("🔄 Decoding base64 audio data...");
        // Base64 데이터 처리
        const base64Data = audio_data.split(',')[1];
        if (!base64Data) {
          throw new Error("Invalid base64 data format");
        }

        const binaryString = atob(base64Data);
        arrayBuffer = new ArrayBuffer(binaryString.length);
        const uint8Array = new Uint8Array(arrayBuffer);
        for (let i = 0; i < binaryString.length; i++) {
          uint8Array[i] = binaryString.charCodeAt(i);
        }
        console.log("✅ Base64 decoding complete, array buffer size:", arrayBuffer.byteLength);
      } else {
        console.log("🔄 Fetching audio from URL...");
        // URL 처리
        const response = await fetch(audio_data);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        arrayBuffer = await response.arrayBuffer();
        console.log("✅ URL fetch complete, array buffer size:", arrayBuffer.byteLength);
      }

      if (arrayBuffer.byteLength === 0) {
        throw new Error("Empty audio buffer received");
      }

      console.log("🔄 Decoding audio buffer...");
      backendAudioBuffer = await backendAudioContext.decodeAudioData(arrayBuffer);
      console.log("✅ Audio buffer decoded successfully");
      console.log("Audio buffer duration:", backendAudioBuffer.duration, "seconds");
      console.log("Audio buffer sample rate:", backendAudioBuffer.sampleRate);
      console.log("Audio buffer channels:", backendAudioBuffer.numberOfChannels);

      return backendAudioBuffer;
    } catch (error) {
      console.error('❌ Backend audio decoding error:', error);
      console.error('Error details:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
      backendAudioBuffer = null;
      return null;
    }
  }

  function startBackendAudioPlayback() {
    console.log("🎵 Starting backend audio playback...");
    console.log("Backend audio context:", backendAudioContext);
    console.log("Backend audio context state:", backendAudioContext?.state);
    console.log("Backend audio buffer:", backendAudioBuffer);

    if (!backendAudioContext || !backendAudioBuffer) {
      console.error("❌ Missing audio context or buffer for playback");
      return;
    }

    // 다시 한번 AudioContext 상태 확인 및 resume
    if (backendAudioContext.state === 'suspended') {
      console.log("🔄 AudioContext still suspended, attempting resume...");
      backendAudioContext.resume().then(() => {
        console.log("✅ Audio context resumed just before playback, state:", backendAudioContext!.state);
        if (backendAudioContext!.state === 'running') {
          actuallyStartPlayback();
        } else {
          console.error("❌ AudioContext still not running after resume attempt");
        }
      }).catch((error) => {
        console.error("❌ Failed to resume AudioContext:", error);
      });
    } else {
      actuallyStartPlayback();
    }

    function actuallyStartPlayback() {
      try {
        console.log("🎵 Actually starting playback now...");
        console.log("AudioContext state before source creation:", backendAudioContext!.state);

        // 이전 source가 있다면 정리
        if (backendAudioSource) {
          try {
            backendAudioSource.stop();
          } catch (e) {
            // 이미 stop된 경우 무시
          }
          backendAudioSource = null;
        }

        // Create new source
        backendAudioSource = backendAudioContext!.createBufferSource();
        backendAudioSource.buffer = backendAudioBuffer;
        backendAudioSource.connect(backendAudioContext!.destination);

        // Calculate start position in seconds
        const startPositionInSeconds = currentFlicks / 705600000; // Convert flicks to seconds
        const currentTime = backendAudioContext!.currentTime;

        console.log("🎵 Playback details:");
        console.log("- Start position (flicks):", currentFlicks);
        console.log("- Start position (seconds):", startPositionInSeconds);
        console.log("- Current time:", currentTime);
        console.log("- Buffer duration:", backendAudioBuffer!.duration);
        console.log("- AudioContext state:", backendAudioContext!.state);

        // Start playback
        if (startPositionInSeconds < backendAudioBuffer!.duration) {
          backendAudioSource.start(currentTime, startPositionInSeconds);
          backendPlayStartTime = currentTime - startPositionInSeconds;
          isPlaying = true;

          console.log("✅ Backend audio playback started successfully!");

          // Update playhead position
          updateBackendPlayhead();

          // Handle end of playback
          backendAudioSource.onended = () => {
            console.log("🔚 Backend audio playback ended");
            stopBackendAudio();
          };
        } else {
          console.warn("⚠️ Start position is beyond audio duration, not starting playback");
          isPlaying = false;
        }
      } catch (error) {
        console.error("❌ Error starting backend audio playback:", error);
        console.error('Error details:', {
          name: error.name,
          message: error.message,
          stack: error.stack
        });
        isPlaying = false;
      }
    }
  }

  function pauseBackendAudio() {
    console.log("⏸️ Pausing backend audio...");
    if (backendAudioSource) {
      // Calculate current position and store it
      const elapsedTime = backendAudioContext!.currentTime - backendPlayStartTime;
      currentFlicks = Math.round(elapsedTime * 705600000); // Convert to flicks
      console.log("⏸️ Paused at position:", currentFlicks, "flicks (", elapsedTime, "seconds)");

      backendAudioSource.stop();
      backendAudioSource = null;
    }

    if (backendPlayheadInterval) {
      clearInterval(backendPlayheadInterval);
      backendPlayheadInterval = null;
    }

    isPlaying = false;
    console.log("✅ Backend audio paused");
  }

  function stopBackendAudio() {
    console.log("⏹️ Stopping backend audio...");
    if (backendAudioSource) {
      backendAudioSource.stop();
      backendAudioSource = null;
    }

    if (backendPlayheadInterval) {
      clearInterval(backendPlayheadInterval);
      backendPlayheadInterval = null;
    }

    currentFlicks = 0;
    isPlaying = false;
    console.log("✅ Backend audio stopped");
  }

  function updateBackendPlayhead() {
    if (!isPlaying || !backendAudioContext) return;

    backendPlayheadInterval = setInterval(() => {
      if (isPlaying && backendAudioContext) {
        const elapsedTime = backendAudioContext.currentTime - backendPlayStartTime;
        currentFlicks = Math.round(elapsedTime * 705600000); // Convert to flicks

        // Check if playback ended
        if (backendAudioBuffer && elapsedTime >= backendAudioBuffer.duration) {
          console.log("🔚 Playback duration reached, stopping...");
          stopBackendAudio();
        }
      }
    }, 16); // ~60fps
  }

  function play() {
    if (isPlaying) {
      console.log("⚠️ Already playing, ignoring play request");
      return;
    }

    console.log("▶️ Play function called");
    console.log("- use_backend_audio:", use_backend_audio);
    console.log("- audio_data present:", !!audio_data);
    console.log("- elem_id:", elem_id);

    // 재생 이벤트 발생
    dispatch('play', {
      currentPosition: currentFlicks,
      notes,
      tempo,
      use_backend_audio
    });

    if (use_backend_audio && audio_data) {
      console.log("🎵 Using backend audio for playback");
      // 백엔드 오디오 재생
      initBackendAudio().then(() => {
        if (!backendAudioBuffer) {
          console.log("🔄 No audio buffer, decoding first...");
          decodeBackendAudio().then(() => {
            if (backendAudioBuffer) {
              console.log("✅ Audio decoded, starting playback");
              startBackendAudioPlayback();
            } else {
              console.error("❌ Failed to decode audio, falling back to frontend");
              fallbackToFrontendAudio();
            }
          });
        } else {
          console.log("✅ Audio buffer ready, starting playback");
          startBackendAudioPlayback();
        }
      }).catch((error) => {
        console.error("❌ Backend audio initialization failed:", error);
        fallbackToFrontendAudio();
      });
      return;
    }

    console.log("🎵 Using frontend audio engine");
    if (!audioEngine.getRenderedBuffer()) {
      console.log("🔄 No rendered buffer, rendering first...");
      // Render audio first if not already rendered
      renderAudio().then(() => {
        startPlayback();
      });
    } else {
      console.log("✅ Rendered buffer ready, starting playback");
      startPlayback();
    }
  }

  function fallbackToFrontendAudio() {
    console.log("🔄 Falling back to frontend audio engine");
    use_backend_audio = false;
    if (!audioEngine.getRenderedBuffer()) {
      renderAudio().then(() => {
        startPlayback();
      });
    } else {
      startPlayback();
    }
  }

  function startPlayback() {
    if (use_backend_audio) {
      console.log("⚠️ startPlayback called but use_backend_audio is true - should not happen");
      return; // 백엔드 오디오 사용 시 건너뛰기
    }

    console.log("▶️ Starting frontend audio playback");
    audioEngine.play();
    isPlaying = true;
  }

  function pause() {
    console.log("⏸️ Pause function called");
    console.log("- use_backend_audio:", use_backend_audio);

    // 일시정지 이벤트 발생
    dispatch('pause', {
      currentPosition: currentFlicks,
      use_backend_audio
    });

    if (use_backend_audio) {
      pauseBackendAudio();
      return;
    }

    console.log("⏸️ Pausing frontend audio");
    audioEngine.pause();
    isPlaying = false;
  }

  function stop() {
    console.log("⏹️ Stop function called");
    console.log("- use_backend_audio:", use_backend_audio);

    // 정지 이벤트 발생
    dispatch('stop', {
      currentPosition: currentFlicks,
      use_backend_audio
    });

    if (use_backend_audio) {
      stopBackendAudio();
      return;
    }

    console.log("⏹️ Stopping frontend audio");
    audioEngine.stop();
    isPlaying = false;
    currentFlicks = 0;
    // Also reset the audio engine's internal position
    audioEngine.seekToFlicks(0);
  }

  function togglePlayback() {
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }

  // Handle position updates from audio engine
  function updatePlayheadPosition(flicks: number) {
    currentFlicks = flicks;

    // Check if playhead is out of view and scroll to keep it visible
    const positionInBeats = flicksToBeats(flicks, tempo);
    const positionInPixels = positionInBeats * pixelsPerBeat;

    // Auto-scroll if playhead is near the edge of the view
    const bufferPixels = 100; // Buffer to start scrolling before edge
    if (positionInPixels > horizontalScroll + width - bufferPixels) {
      horizontalScroll = Math.max(0, positionInPixels - width / 2);
    } else if (positionInPixels < horizontalScroll + bufferPixels) {
      horizontalScroll = Math.max(0, positionInPixels - bufferPixels);
    }
  }

  // Handle note changes to re-render audio
  function handleNoteChange(event: CustomEvent) {
    notes = event.detail.notes;
    // Re-render audio when notes change
    renderAudio();
    // 노트 변경 이벤트 발생
    dispatchNoteChange();
  }

  // Handle tempo changes
  function handleTempoChange(event: CustomEvent) {
    tempo = event.detail;
    // Re-render audio when tempo changes
    renderAudio();
    // 전체 데이터 변경 이벤트 발생
    dispatchDataChange();
  }

  // Handle position change from timeline click
  function handlePositionChange(event: CustomEvent) {
    const { flicks } = event.detail;
    currentFlicks = flicks;

    // Seek audio engine to new position
    audioEngine.seekToFlicks(flicks);
  }

  // 가사 입력 이벤트 발생 (GridComponent에서 전달받은 것을 상위로 전달)
  function handleLyricInput(event: CustomEvent) {
    dispatch('lyricInput', event.detail);
  }

  onMount(() => {
    // Set up playhead position update callback
    audioEngine.setPlayheadUpdateCallback(updatePlayheadPosition);

    // Initial audio render
    if (notes.length > 0) {
      renderAudio();
    }
  });

  onDestroy(() => {
    // Clean up backend audio
    if (backendPlayheadInterval) {
      clearInterval(backendPlayheadInterval);
    }
    if (backendAudioSource) {
      backendAudioSource.stop();
    }
    if (backendAudioContext) {
      backendAudioContext.close();
    }

    // Clean up component-specific audio engine resources
    if (elem_id) {
      AudioEngineManager.disposeInstance(elem_id);
    } else {
      audioEngine.dispose();
    }
  });

  // Reactive statement to decode backend audio when audio_data changes
  $: if (audio_data && use_backend_audio) {
    console.log("🔄 Audio data or backend flag changed, initializing...");
    console.log("- audio_data present:", !!audio_data);
    console.log("- use_backend_audio:", use_backend_audio);

    initBackendAudio().then(() => {
      decodeBackendAudio();
    }).catch((error) => {
      console.error("❌ Failed to initialize backend audio:", error);
    });
  }
</script>

<div
  class="piano-roll-container"
  bind:this={containerElement}
  style="width: {width}px; height: {height}px;"
>
  <Toolbar
    {tempo}
    {timeSignature}
    {editMode}
    {snapSetting}
    {isPlaying}
    on:tempoChange={handleTempoChange}
    on:timeSignatureChange={handleTimeSignatureChange}
    on:editModeChange={handleEditModeChange}
    on:snapChange={handleSnapChange}
    on:zoomChange={handleZoomChange}
    on:play={play}
    on:pause={pause}
    on:stop={stop}
    on:togglePlay={togglePlayback}
  />

  <div class="piano-roll-main" style="height: {height - 40}px;">
    <!-- Timeline positioned at the top -->
    <div class="timeline-container" style="margin-left: {keyboardWidth}px;">
      <TimeLineComponent
        width={width - keyboardWidth}
        {timelineHeight}
        {timeSignature}
        {snapSetting}
        {horizontalScroll}
        {pixelsPerBeat}
        {tempo}
        on:zoomChange={handleZoomChange}
        on:positionChange={handlePositionChange}
      />
    </div>

    <!-- Main content area with keyboard and grid aligned -->
    <div class="content-container">
      <KeyboardComponent
        {keyboardWidth}
        height={height - 40 - timelineHeight}
        {verticalScroll}
      />

      <div class="grid-container" style="position: relative;">
        <!-- Waveform positioned below the grid but above the grid lines -->
        <WaveformComponent
          bind:this={waveformComponent}
          width={width - keyboardWidth}
          height={(height - 40 - timelineHeight) / 2}
          {horizontalScroll}
          {pixelsPerBeat}
          {tempo}
          opacity={waveformOpacity}
          top={(height - 100 - timelineHeight) / 2}
          {audio_data}
          {curve_data}
          {use_backend_audio}
          {elem_id}
        />

        <!-- Grid component containing notes and grid lines -->
        <GridComponent
          width={width - keyboardWidth}
          height={height - 40 - timelineHeight}
          {notes}
          {tempo}
          {timeSignature}
          {editMode}
          {snapSetting}
          {horizontalScroll}
          {verticalScroll}
          {pixelsPerBeat}
          {currentFlicks}
          {isPlaying}
          {sampleRate}
          {ppqn}
          on:scroll={handleGridScroll}
          on:noteChange={handleNoteChange}
          on:lyricInput={handleLyricInput}
        />

        <!-- Playhead position indicator -->
        <PlayheadComponent
          width={width - keyboardWidth}
          height={height - 40 - timelineHeight}
          {horizontalScroll}
          {pixelsPerBeat}
          {tempo}
          {currentFlicks}
          {isPlaying}
        />
      </div>
    </div>
  </div>
</div>

<!-- Debug component for Flicks timing information -->
<DebugComponent
  {currentFlicks}
  {tempo}
  {notes}
  {isPlaying}
  {isRendering}
/>

<style>
  .piano-roll-container {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background-color: #2c2c2c;
    border-radius: 5px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }

  .piano-roll-main {
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  .timeline-container {
    display: flex;
    height: var(--timeline-height, 40px);
  }

  .content-container {
    display: flex;
    flex-direction: row;
    flex: 1;
  }
</style>
