<!--
  KeyboardComponent that renders piano keys using canvas and allows users to preview sounds.
-->
<script lang="ts">
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  
  // Props
  export let keyboardWidth = 120;  // Width of the keyboard
  export let height = 560;  // Height of the keyboard component
  export let verticalScroll = 0;  // Vertical scroll position synced with GridComponent
  
  // Constants
  const WHITE_KEY_HEIGHT = 20;  // Height of a white key
  const BLACK_KEY_HEIGHT = 12;  // Height of a black key
  const BLACK_KEY_WIDTH = keyboardWidth * 0.6;  // Width of black keys (60% of keyboard width)
  
  // Define note names
  const NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  
  // Calculate total key range (MIDI range: 0-127)
  const TOTAL_KEYS = 128;
  const keyPositions: Array<{
    note: string,
    octave: number,
    isBlack: boolean,
    y: number
  }> = [];
  
  // Audio for note preview
  let audioContext: AudioContext | null = null;
  let canPlay = false;
  
  // DOM References
  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null = null;
  
  const dispatch = createEventDispatcher();
  
  // Initialize audio context
  function initAudio() {
    try {
      audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      canPlay = true;
    } catch (e) {
      console.error('Web Audio API is not supported in this browser', e);
      canPlay = false;
    }
  }
  
  // Play a preview note
  function playNote(midiNote: number) {
    if (!audioContext || !canPlay) return;
    
    const attackTime = 0.01;
    const releaseTime = 0.5;
    const frequency = 440 * Math.pow(2, (midiNote - 69) / 12);
    
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.type = 'sine';
    oscillator.frequency.value = frequency;
    
    gainNode.gain.setValueAtTime(0, audioContext.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + attackTime);
    gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + attackTime + releaseTime);
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.start();
    oscillator.stop(audioContext.currentTime + attackTime + releaseTime);
  }
  
  // Calculate positions for all keys
  function calculateKeyPositions() {
    keyPositions.length = 0;
    for (let midiNote = TOTAL_KEYS - 1; midiNote >= 0; midiNote--) {
      const octave = Math.floor(midiNote / 12) - 1;
      const noteIndex = midiNote % 12;
      const note = NOTES[noteIndex];
      const isBlack = note.includes('#');
      const y = (TOTAL_KEYS - 1 - midiNote) * WHITE_KEY_HEIGHT;
      
      keyPositions.push({
        note,
        octave,
        isBlack,
        y
      });
    }
  }
  
  // Draw the piano keyboard
  function drawKeyboard() {
    if (!ctx || !canvas) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Adjust based on vertical scroll
    const startIndex = Math.floor(verticalScroll / WHITE_KEY_HEIGHT);
    const visibleKeysCount = Math.ceil(height / WHITE_KEY_HEIGHT) + 1;
    
    // Draw visible white keys first (so black keys can overlay)
    for (let i = startIndex; i < Math.min(startIndex + visibleKeysCount, keyPositions.length); i++) {
      const key = keyPositions[i];
      if (!key.isBlack) {
        const y = key.y - verticalScroll;
        drawWhiteKey(key.note, key.octave, y);
      }
    }
    
    // Then draw black keys on top
    for (let i = startIndex; i < Math.min(startIndex + visibleKeysCount, keyPositions.length); i++) {
      const key = keyPositions[i];
      if (key.isBlack) {
        const y = key.y - verticalScroll;
        drawBlackKey(key.note, key.octave, y);
      }
    }
  }
  
  function drawWhiteKey(note: string, octave: number, y: number) {
    if (!ctx) return;
    
    ctx.fillStyle = '#ffffff';
    ctx.strokeStyle = '#cccccc';
    ctx.lineWidth = 1;
    
    ctx.fillRect(0, y, keyboardWidth, WHITE_KEY_HEIGHT);
    ctx.strokeRect(0, y, keyboardWidth, WHITE_KEY_HEIGHT);
    
    // Draw note name
    ctx.fillStyle = '#333333';
    ctx.font = '10px Arial';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${note}${octave}`, keyboardWidth - 6, y + WHITE_KEY_HEIGHT / 2);
  }
  
  function drawBlackKey(note: string, octave: number, y: number) {
    if (!ctx) return;
    
    ctx.fillStyle = '#333333';
    ctx.fillRect(0, y, BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT);
    
    // Draw note name on black key
    ctx.fillStyle = '#ffffff';
    ctx.font = '8px Arial';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${note}${octave}`, BLACK_KEY_WIDTH - 6, y + BLACK_KEY_HEIGHT / 2);
  }
  
  // Handle mouse events
  function handleMouseDown(event: MouseEvent) {
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top + verticalScroll;
    
    // Find which key was clicked
    for (let i = 0; i < keyPositions.length; i++) {
      const key = keyPositions[i];
      const keyHeight = key.isBlack ? BLACK_KEY_HEIGHT : WHITE_KEY_HEIGHT;
      const keyWidth = key.isBlack ? BLACK_KEY_WIDTH : keyboardWidth;
      
      if (y >= key.y && y < key.y + keyHeight && x <= keyWidth) {
        // Calculate MIDI note number
        const midiNote = TOTAL_KEYS - 1 - i;
        playNote(midiNote);
        break;
      }
    }
  }
  
  // Set up the component
  onMount(() => {
    // Get canvas context
    ctx = canvas.getContext('2d');
    
    // Set up canvas size
    canvas.width = keyboardWidth;
    canvas.height = height;
    
    // Calculate key positions
    calculateKeyPositions();
    
    // Draw initial keyboard
    drawKeyboard();
    
    // Initialize audio
    initAudio();
    
    // Note: We don't need to set the initial scroll position here
    // as it will be controlled by the GridComponent through the verticalScroll prop
  });
  
  // Update when props change
  $: {
    if (ctx && canvas) {
      drawKeyboard();
    }
  }
  
  // Specifically update when vertical scroll changes
  $: if (verticalScroll !== undefined && ctx && canvas) {
    drawKeyboard();
  }
</script>

<canvas 
  bind:this={canvas} 
  width={keyboardWidth} 
  height={height}
  on:mousedown={handleMouseDown}
  class="keyboard-canvas"
></canvas>

<style>
  .keyboard-canvas {
    display: block;
    background-color: #f8f8f8;
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  }
</style>
