<!--
  TimeLineComponent that displays measures and beats timeline.
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { beatsToFlicks, pixelsToFlicks } from '../utils/flicks';
  
  // Props
  export let width = 880;  // Width of the timeline (same as grid width)
  export let timelineHeight = 40;  // Height of the timeline
  export let timeSignature = { numerator: 4, denominator: 4 };
  export let snapSetting = '1/8';  // Snap grid setting (1/1, 1/2, 1/4, 1/8, 1/16, 1/32, none)
  export let horizontalScroll = 0;  // Horizontal scroll position synced with GridComponent
  export let pixelsPerBeat = 80;  // Pixels per beat (controls zoom level)
  export let tempo = 120;  // Tempo in BPM (needed for flicks conversion)
  
  // Set up event dispatcher
  const dispatch = createEventDispatcher();
  
  // Calculate appropriate subdivisions based on time signature denominator
  function getSubdivisionsFromTimeSignature(denominator: number): { count: number, pixelsPerSubdivision: number } {
    // The number of subdivisions per beat depends on the denominator
    switch (denominator) {
      case 2: // Half note gets the beat
        return { count: 2, pixelsPerSubdivision: pixelsPerBeat / 2 };
      case 4: // Quarter note gets the beat
        return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 };
      case 8: // Eighth note gets the beat
        return { count: 2, pixelsPerSubdivision: pixelsPerBeat / 2 };
      case 16: // Sixteenth note gets the beat
        return { count: 2, pixelsPerSubdivision: pixelsPerBeat / 2 };
      default:
        return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 }; // Default to 16th notes
    }
  }
  
  // Get subdivisions based on snap setting
  function getSubdivisionsFromSnapSetting(): { count: number, pixelsPerSubdivision: number } {
    if (snapSetting === 'none') {
      // Default to quarter note subdivisions if snap is 'none'
      return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 };
    }
    
    const [numerator, denominator] = snapSetting.split('/');
    if (numerator === '1' && denominator) {
      const divisionValue = parseInt(denominator);
      
      switch (divisionValue) {
        case 1: // Whole note
          return { count: 1, pixelsPerSubdivision: pixelsPerBeat * 4 };
        case 2: // Half note
          return { count: 2, pixelsPerSubdivision: pixelsPerBeat * 2 };
        case 4: // Quarter note
          return { count: 4, pixelsPerSubdivision: pixelsPerBeat };
        case 8: // Eighth note
          return { count: 8, pixelsPerSubdivision: pixelsPerBeat / 2 };
        case 16: // Sixteenth note
          return { count: 16, pixelsPerSubdivision: pixelsPerBeat / 4 };
        case 32: // Thirty-second note
          return { count: 32, pixelsPerSubdivision: pixelsPerBeat / 8 };
        default: 
          return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 };
      }
    }
    
    // Default to quarter note subdivisions
    return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 };
  }
  
  // Derived grid constants based on time signature
  $: subdivisions = getSubdivisionsFromSnapSetting();
  
  // DOM References
  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null = null;
  
  // Calculate various dimensions
  $: beatsPerMeasure = timeSignature.numerator;
  $: pixelsPerMeasure = beatsPerMeasure * pixelsPerBeat;
  $: totalMeasures = 32;  // Should match GridComponent
  $: totalTimelineWidth = totalMeasures * pixelsPerMeasure;
  
  // Draw the timeline with measure and beat divisions
  function drawTimeline() {
    if (!ctx || !canvas) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background
    ctx.fillStyle = '#2c2c2c';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Calculate visible area
    const startX = horizontalScroll;
    const endX = horizontalScroll + width;
    
    // Calculate visible measures
    const startMeasure = Math.floor(startX / pixelsPerMeasure);
    const endMeasure = Math.ceil(endX / pixelsPerMeasure);
    
    // Get current snap settings
    const subdivs = getSubdivisionsFromSnapSetting();
    
    // Draw measure numbers and division lines
    for (let measure = startMeasure; measure <= endMeasure; measure++) {
      const measureX = measure * pixelsPerMeasure - horizontalScroll;
      
      // Draw measure number
      ctx.fillStyle = '#FFFFFF';
      ctx.font = '10px Arial';
      ctx.textAlign = 'center';
      ctx.fillText((measure + 1).toString(), measureX + pixelsPerMeasure / 2, 12);
      
      // Draw measure line
      ctx.strokeStyle = '#AAAAAA';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(measureX, 0);
      ctx.lineTo(measureX, timelineHeight);
      ctx.stroke();
      
      // Draw beat lines within measure
      for (let beat = 1; beat < beatsPerMeasure; beat++) {
        const beatX = measureX + beat * pixelsPerBeat;
        
        ctx.strokeStyle = '#777777';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(beatX, timelineHeight - 15);
        ctx.lineTo(beatX, timelineHeight);
        ctx.stroke();
      }
      
      // For 1/1 snap setting, don't show additional subdivision lines
      if (snapSetting === '1/1') {
        // Just draw beat lines, no subdivisions
        continue;
      }
      
      // Calculate the number of divisions per measure based on snap setting
      let divisionsPerMeasure = 0;
      let pixelsPerDivision = 0;
      
      switch (snapSetting) {
        case '1/2':
          divisionsPerMeasure = beatsPerMeasure * 2; // 8 divisions in 4/4
          pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
          break;
        case '1/4':
          divisionsPerMeasure = beatsPerMeasure * 4; // 16 divisions in 4/4
          pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
          break;
        case '1/8':
          divisionsPerMeasure = beatsPerMeasure * 8; // 32 divisions in 4/4
          pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
          break;
        case '1/16':
          divisionsPerMeasure = beatsPerMeasure * 16; // 64 divisions in 4/4
          pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
          break;
        case '1/32':
          divisionsPerMeasure = beatsPerMeasure * 32; // 128 divisions in 4/4
          pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
          break;
        default:
          divisionsPerMeasure = beatsPerMeasure * 4; // Default to quarter notes
          pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
      }
      
      // Draw subdivision lines
      for (let division = 1; division < divisionsPerMeasure; division++) {
        // Skip if this is already a beat line
        if (division % (divisionsPerMeasure / beatsPerMeasure) === 0) {
          continue; // This is a beat line, already drawn
        }
        
        const divisionX = measureX + division * pixelsPerDivision;
        
        ctx.strokeStyle = '#555555';
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(divisionX, timelineHeight - 10);
        ctx.lineTo(divisionX, timelineHeight);
        ctx.stroke();
      }
    }
    
    // Draw playhead or other markers if needed
    // (Playback functionality could be added here)
  }
  
  // Handle timeline click to seek
  function handleTimelineClick(event: MouseEvent) {
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left + horizontalScroll;
    
    // Convert x position to flicks using direct conversion for higher precision
    const flicks = pixelsToFlicks(x, pixelsPerBeat, tempo);
    
    // Dispatch position change event
    dispatch('positionChange', { flicks });
  }
  
  // Set up the component
  onMount(() => {
    // Get canvas context
    ctx = canvas.getContext('2d');
    
    // Set up canvas size
    canvas.width = width;
    canvas.height = timelineHeight;
    
    // Draw initial timeline
    drawTimeline();
  });
  
  // Update when props change (width, height, etc.)
  $: {
    if (ctx && canvas) {
      canvas.width = width;
      canvas.height = timelineHeight;
      drawTimeline();
    }
  }
  
  // Redraw when time signature changes
  $: if (timeSignature && ctx && canvas) {
    // This will reactively update when timeSignature.numerator or denominator changes
    drawTimeline();
  }
  
  // Specifically redraw when horizontal scroll changes
  $: if (horizontalScroll !== undefined && ctx && canvas) {
    drawTimeline();
  }
  
  // Redraw when zoom level (pixelsPerBeat) changes
  $: if (pixelsPerBeat && ctx && canvas) {
    // This will reactively update when pixelsPerBeat changes
    drawTimeline();
  }
</script>

<div class="timeline-container" style="width: {width}px; height: {timelineHeight}px;">
  <!-- Zoom controls -->
  <div class="zoom-controls">
    <button class="zoom-button zoom-out" on:click={() => dispatch('zoomChange', { action: 'zoom-out' })} aria-label="Zoom out">
      <svg viewBox="0 0 24 24" width="16" height="16">
        <path d="M15,3C8.373,3,3,8.373,3,15c0,6.627,5.373,12,12,12s12-5.373,12-12C27,8.373,21.627,3,15,3z M21,16H9v-2h12V16z" fill="currentColor"/>
      </svg>
    </button>
    <button class="zoom-button zoom-in" on:click={() => dispatch('zoomChange', { action: 'zoom-in' })} aria-label="Zoom in">
      <svg viewBox="0 0 24 24" width="16" height="16">
        <path d="M15,3C8.373,3,3,8.373,3,15c0,6.627,5.373,12,12,12s12-5.373,12-12C27,8.373,21.627,3,15,3z M21,16h-5v5h-2v-5H9v-2h5V9h2v5h5V16z" fill="currentColor"/>
      </svg>
    </button>
  </div>
  
  <canvas 
    bind:this={canvas} 
    width={width} 
    height={timelineHeight}
    on:click={handleTimelineClick}
    style="cursor: pointer;"
  ></canvas>
</div>

<style>
  .timeline-container {
    position: relative;
    overflow: hidden;
    background-color: #2a2a2a;
  }
  
  .zoom-controls {
    position: absolute;
    right: 10px;
    top: 5px;
    display: flex;
    gap: 5px;
    z-index: 10;
  }
  
  .zoom-button {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    background-color: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .zoom-button:hover {
    background-color: rgba(0, 0, 0, 0.5);
  }
  
  .zoom-button:active {
    background-color: rgba(0, 0, 0, 0.7);
  }
</style>
