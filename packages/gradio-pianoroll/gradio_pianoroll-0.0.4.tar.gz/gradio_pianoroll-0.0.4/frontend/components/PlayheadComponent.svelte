<!--
  PlayheadComponent.svelte
  Displays a vertical line indicating the current playback position
-->
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { flicksToBeats, flicksToPixels } from '../utils/flicks';

  // Props
  export let width = 880;
  export let height = 520;
  export let horizontalScroll = 0;
  export let pixelsPerBeat = 80;
  export let tempo = 120;
  export let currentFlicks = 0;
  export let isPlaying = false;

  // Calculated position using more precise flicks conversion
  $: positionInBeats = flicksToBeats(currentFlicks, tempo);
  $: positionInPixels = flicksToPixels(currentFlicks, pixelsPerBeat, tempo);
  $: visiblePosition = positionInPixels - horizontalScroll;
  $: isVisible = visiblePosition >= 0 && visiblePosition <= width;

  // Animation state
  let animationId: number | null = null;

  // Playhead colors
  const PLAYHEAD_COLOR = '#ff5252';
  const PLAYHEAD_COLOR_SHADOW = 'rgba(255, 82, 82, 0.3)';

  // Animation function for smooth playhead movement
  function animatePlayhead() {
    if (!isPlaying) {
      if (animationId) {
        cancelAnimationFrame(animationId);
        animationId = null;
      }
      return;
    }

    // Continue animation loop
    animationId = requestAnimationFrame(animatePlayhead);
  }

  // Start/stop animation based on isPlaying status
  $: if (isPlaying && !animationId) {
    animationId = requestAnimationFrame(animatePlayhead);
  } else if (!isPlaying && animationId) {
    cancelAnimationFrame(animationId);
    animationId = null;
  }

  onDestroy(() => {
    if (animationId) {
      cancelAnimationFrame(animationId);
    }
  });
</script>

{#if isVisible}
  <div
    class="playhead"
    style="
      left: {visiblePosition}px;
      height: {height}px;
      border-color: {PLAYHEAD_COLOR};
      box-shadow: 0 0 6px {PLAYHEAD_COLOR_SHADOW};
    "
  ></div>
{/if}

<style>
  .playhead {
    position: absolute;
    top: 0;
    width: 0;
    z-index: 5; /* Above all other elements */
    border-left: 2px solid;
    pointer-events: none; /* Allow interactions to pass through */
    transition: border-color 0.2s ease;
  }
</style>
