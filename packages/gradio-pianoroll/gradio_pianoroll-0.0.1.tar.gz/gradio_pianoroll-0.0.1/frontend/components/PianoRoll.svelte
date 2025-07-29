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
  import { audioEngine } from '../utils/audioEngine';
  import { beatsToFlicks, flicksToBeats, formatFlicks } from '../utils/flicks';
  import { createEventDispatcher } from 'svelte';

  // 이벤트 디스패처 생성
  const dispatch = createEventDispatcher();

  // Props
  export let width = 1000;  // Total width of the piano roll
  export let height = 600;  // Total height of the piano roll
  export let keyboardWidth = 120; // Width of the keyboard component
  export let timelineHeight = 40; // Height of the timeline component

  // Shared state
  export let notes: Array<{
    id: string,
    start: number,
    duration: number,
    pitch: number,
    velocity: number,
    lyric?: string
  }> = [];

  // Settings
  export let tempo = 120;
  export let timeSignature = { numerator: 4, denominator: 4 };
  export let editMode = 'select'; // 'select', 'draw', 'erase', etc.
  export let snapSetting = '1/4'; // Default snap setting: 1/4

  // Playback state
  let isPlaying = false;
  let isRendering = false;
  let currentFlicks = 0;
  let waveformOpacity = 0.7; // Initial opacity for waveform

  // References to components
  let waveformComponent: any; // Reference to waveform component

  // Zoom level (pixels per beat)
  let pixelsPerBeat = 80; // Default zoom level
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

  // 전체 데이터 변경 이벤트 발생
  function dispatchDataChange() {
    dispatch('dataChange', {
      notes,
      tempo,
      timeSignature,
      editMode,
      snapSetting,
      pixelsPerBeat
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
    isRendering = true;
    try {
      // Initialize audio engine
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

  function play() {
    if (isPlaying) return;

    if (!audioEngine.getRenderedBuffer()) {
      // Render audio first if not already rendered
      renderAudio().then(() => {
        startPlayback();
      });
    } else {
      startPlayback();
    }
  }

  function startPlayback() {
    audioEngine.play(currentFlicks);
    isPlaying = true;
  }

  function pause() {
    audioEngine.pause();
    isPlaying = false;
  }

  function stop() {
    audioEngine.stop();
    isPlaying = false;
    currentFlicks = 0;
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

  onMount(() => {
    // Set up playhead position update callback
    audioEngine.setPlayheadUpdateCallback(updatePlayheadPosition);

    // Initial audio render
    if (notes.length > 0) {
      renderAudio();
    }
  });

  onDestroy(() => {
    // Clean up audio engine resources
    audioEngine.dispose();
  });
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
        on:zoomChange={handleZoomChange}
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
          on:scroll={handleGridScroll}
          on:noteChange={handleNoteChange}
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
