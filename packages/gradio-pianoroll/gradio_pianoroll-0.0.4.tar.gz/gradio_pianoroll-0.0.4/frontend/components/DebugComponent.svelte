<!--
  DebugComponent.svelte
  Displays debug information about Flicks timing and playback
-->
<script lang="ts">
  import { flicksToBeats, formatFlicks } from '../utils/flicks';

  // Props
  export let currentFlicks = 0;
  export let tempo = 120;
  export let notes: Array<{
    id: string,
    start: number,
    duration: number,
    pitch: number,
    velocity: number,
    lyric?: string,
    phoneme?: string
  }> = [];
  export let isPlaying = false;
  export let isRendering = false;

  // Calculated values
  $: currentBeats = flicksToBeats(currentFlicks, tempo);
  $: currentMeasure = Math.floor(currentBeats / 4) + 1;
  $: currentBeat = (currentBeats % 4) + 1;

  // Get the currently playing notes based on position
  $: playingNotes = notes.filter(note => {
    const noteStartBeats = note.start / 100;
    const noteDurationBeats = note.duration / 100;
    const noteEndBeats = noteStartBeats + noteDurationBeats;

    return currentBeats >= noteStartBeats && currentBeats < noteEndBeats;
  });
</script>

<div class="debug-panel" class:minimized={!isPlaying && !isRendering}>
  <div class="debug-header">Flicks Debug</div>

  <div class="debug-content">
    <div class="debug-section">
      <div class="debug-label">Playback Status:</div>
      <div class="debug-value status-value">
        {#if isRendering}
          <span class="status-rendering">Rendering...</span>
        {:else if isPlaying}
          <span class="status-playing">Playing</span>
        {:else}
          <span class="status-stopped">Stopped</span>
        {/if}
      </div>
    </div>

    <div class="debug-section">
      <div class="debug-label">Current Flicks:</div>
      <div class="debug-value">{currentFlicks.toLocaleString()}</div>
    </div>

    <div class="debug-section">
      <div class="debug-label">Formatted Time:</div>
      <div class="debug-value">{formatFlicks(currentFlicks)}</div>
    </div>

    <div class="debug-section">
      <div class="debug-label">Position:</div>
      <div class="debug-value">Measure {currentMeasure}, Beat {currentBeat.toFixed(3)}</div>
    </div>

    <div class="debug-section">
      <div class="debug-label">Tempo:</div>
      <div class="debug-value">{tempo} BPM</div>
    </div>

    {#if playingNotes.length > 0}
      <div class="debug-section">
        <div class="debug-label">Playing Notes:</div>
        <div class="debug-value">
          {#each playingNotes as note}
            <div class="note-info">
              Pitch: {note.pitch}, Velocity: {note.velocity}
              {#if note.lyric}
                , Lyric: "{note.lyric}"
              {/if}
              {#if note.phoneme}
                , Phoneme: [{note.phoneme}]
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .debug-panel {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 300px;
    background-color: rgba(0, 0, 0, 0.85);
    border: 1px solid #444;
    border-radius: 4px;
    color: #fff;
    font-family: 'Roboto Mono', monospace;
    font-size: 12px;
    z-index: 1000;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    transition: transform 0.3s ease, opacity 0.3s ease;
  }

  .debug-panel.minimized {
    transform: translateY(calc(100% - 30px));
    opacity: 0.7;
  }

  .debug-panel:hover {
    opacity: 1;
    transform: translateY(0);
  }

  .debug-header {
    background-color: #333;
    padding: 6px 12px;
    font-weight: bold;
    border-bottom: 1px solid #444;
    cursor: pointer;
    user-select: none;
  }

  .debug-content {
    padding: 10px;
    max-height: 300px;
    overflow-y: auto;
  }

  .debug-section {
    margin-bottom: 8px;
    display: flex;
    flex-wrap: wrap;
  }

  .debug-label {
    width: 120px;
    color: #aaa;
  }

  .debug-value {
    flex: 1;
    min-width: 150px;
    color: #fff;
  }

  .status-value {
    font-weight: bold;
  }

  .status-playing {
    color: #4caf50;
  }

  .status-stopped {
    color: #f44336;
  }

  .status-rendering {
    color: #ff9800;
    animation: blink 1s infinite;
  }

  .note-info {
    margin-bottom: 4px;
    padding-left: 8px;
    border-left: 2px solid #2196F3;
  }

  @keyframes blink {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
</style>
