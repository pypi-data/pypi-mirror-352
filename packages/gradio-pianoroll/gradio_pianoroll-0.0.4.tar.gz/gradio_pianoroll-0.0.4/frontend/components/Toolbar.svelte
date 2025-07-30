<!--
  Toolbar component for controlling tempo, time signature, edit mode, and playback.
-->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let tempo = 120;
  export let timeSignature = { numerator: 4, denominator: 4 };
  export let editMode = 'select'; // 'select', 'draw', 'erase', etc.
  export let snapSetting = '1/4'; // Default snap setting
  export let isPlaying = false; // Playback status

  const dispatch = createEventDispatcher();

  // Edit mode options
  const editModes = [
    { id: 'select', label: 'Select', icon: '👆' },
    { id: 'draw', label: 'Draw', icon: '✏️' },
    { id: 'erase', label: 'Erase', icon: '🧹' },
  ];

  // Time signature numerator and denominator options
  const numeratorOptions = [2, 3, 4, 5, 6, 7, 9, 12];
  const denominatorOptions = [2, 4, 8, 16];

  // Snap options
  const snapOptions = ['1/1', '1/2', '1/4', '1/8', '1/16', '1/32', 'none'];

  function updateTempo(event: Event) {
    const newTempo = parseInt((event.target as HTMLInputElement).value);
    dispatch('tempoChange', newTempo);
  }

  function updateTimeSignature() {
    dispatch('timeSignatureChange', timeSignature);
  }

  function setEditMode(mode: string) {
    dispatch('editModeChange', mode);
  }

  function updateSnapSetting(event: Event) {
    const newSnapSetting = (event.target as HTMLSelectElement).value;
    dispatch('snapChange', newSnapSetting);
  }

  // Playback control functions
  function play() {
    dispatch('play');
  }

  function pause() {
    dispatch('pause');
  }

  function stop() {
    dispatch('stop');
  }

  function togglePlay() {
    dispatch('togglePlay');
  }
</script>

<div class="toolbar">
  <!-- Playback controls -->
  <div class="section playback-section">
    <button
      class="playback-button"
      on:click={togglePlay}
      title={isPlaying ? 'Pause' : 'Play'}>
      {isPlaying ? '⏸' : '▶'}
    </button>

    <button
      class="playback-button"
      on:click={stop}
      title="Stop"
    >
      ⏹
    </button>
  </div>

  <div class="section time-section">
    <div class="tempo-control">
      <label for="tempo-input">Tempo</label>
      <div class="tempo-input-group">
        <input
          type="number"
          id="tempo-input"
          min="20"
          max="300"
          bind:value={tempo}
          on:change={updateTempo}
        />
        <span class="unit">BPM</span>
      </div>
    </div>

    <div class="time-signature-control">
      <div class="time-signature-wrapper">
        <label for="time-signature-numerator" class="label">Signature</label>
        <select
          id="time-signature-numerator"
          bind:value={timeSignature.numerator}
          on:change={updateTimeSignature}
        >
          {#each numeratorOptions as num}
            <option value={num}>{num}</option>
          {/each}
        </select>
        <span class="divider">/</span>
        <select
          id="time-signature-denominator"
          bind:value={timeSignature.denominator}
          on:change={updateTimeSignature}
        >
          {#each denominatorOptions as denom}
            <option value={denom}>{denom}</option>
          {/each}
        </select>
      </div>
    </div>

    <div class="snap-control-container">
      <label for="snap-setting" class="label">Snap</label>
      <div class="snap-control">
        <select
          id="snap-setting"
          bind:value={snapSetting}
          on:change={updateSnapSetting}
        >
          {#each snapOptions as snap}
            <option value={snap}>{snap}</option>
          {/each}
        </select>
      </div>
    </div>
  </div>

  <div class="section edit-mode-section">
    <div id="edit-mode-label" class="edit-mode-label">Mode</div>
    <div class="edit-mode-buttons" aria-labelledby="edit-mode-label">
      {#each editModes as mode}
        <button
          class="edit-mode-button {editMode === mode.id ? 'active' : ''}"
          on:click={() => setEditMode(mode.id)}
          title={mode.label}
        >
          <span class="icon">{mode.icon}</span>
          <span class="label">{mode.label}</span>
        </button>
      {/each}
    </div>
  </div>
</div>

<style>
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    height: 40px;
    background-color: #3a3a3a;
    border-bottom: 1px solid #555;
  }

  .section {
    display: flex;
    align-items: center;
  }

  label {
    font-size: 12px;
    margin-right: 8px;
    color: #ccc;
  }

  .tempo-control, .time-signature-control {
    display: flex;
    align-items: center;
    margin-right: 16px;
  }

  .tempo-input-group, .time-signature-wrapper {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  input, select {
    background-color: #2c2c2c;
    border: 1px solid #555;
    border-radius: 3px;
    color: #fff;
    font-size: 12px;
    padding: 4px 6px;
    width: 50px;
    height: 30px;
  }

  .tempo-input-group input {
    width: 70px;
    margin: 0 5px;
    text-align: right;
    font-weight: bold;
    display: inline-block !important;
    visibility: visible !important;
    opacity: 1 !important;
    height: 30px !important;
    background-color: #2c2c2c !important;
    color: #fff !important;
  }

  .unit, .divider {
    color: #ccc;
    font-size: 12px;
    margin: 0 4px;
  }

  .edit-mode-section, .playback-section {
    display: flex;
    align-items: center;
  }

  .edit-mode-label,
  .label {
    font-size: 12px;
    color: #ccc;
    margin-right: 8px;
  }

  .playback-button {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #2c2c2c;
    border: 1px solid #555;
    border-radius: 3px;
    color: #ccc;
    cursor: pointer;
    font-size: 12px;
    padding: 4px 8px;
    margin-right: 8px;
    min-width: 30px;
    height: 30px;
  }

  .playback-button:hover {
    background-color: #3c3c3c;
  }

  .edit-mode-buttons {
    display: flex;
    gap: 4px;
    height: 30px;
  }

  .snap-control-container {
    display: flex;
    align-items: center;
    margin-left: 16px;
  }

  .snap-control {
    display: flex;
    align-items: center;
  }

  .edit-mode-button {
    display: flex;
    align-items: center;
    background-color: #2c2c2c;
    border: 1px solid #555;
    border-radius: 3px;
    color: #ccc;
    cursor: pointer;
    font-size: 12px;
    padding: 4px 8px;
  }

  .edit-mode-button.active {
    background-color: #4a4a4a;
    color: #fff;
    border-color: #777;
  }

  .icon {
    margin-right: 4px;
  }

  @media (max-width: 768px) {
    .label {
      display: none;
    }

    .icon {
      margin-right: 0;
    }
  }
</style>
