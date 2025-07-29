/**
 * Flicks utility module based on Facebook's Flicks timing library
 * 
 * A flick is a unit of time that is 1/705600000 of a second (705.6 million flicks per second).
 * It's designed to provide a common timing reference that can evenly represent many common 
 * audio sample rates and frame rates.
 * 
 * @see https://github.com/facebookarchive/Flicks
 */

// The number of flicks in one second
export const FLICKS_PER_SECOND = 705600000;

/**
 * Convert seconds to flicks with higher precision
 * Removed Math.round() to maintain precision
 */
export function secondsToFlicks(seconds: number): number {
  return seconds * FLICKS_PER_SECOND;
}

/**
 * Convert flicks to seconds
 */
export function flicksToSeconds(flicks: number): number {
  return flicks / FLICKS_PER_SECOND;
}

/**
 * Convert beats to flicks based on tempo with higher precision
 * Direct calculation to avoid intermediate rounding
 */
export function beatsToFlicks(beats: number, tempo: number): number {
  // Optimized formula: beats * 60 * FLICKS_PER_SECOND / tempo
  return (beats * 60 * FLICKS_PER_SECOND) / tempo;
}

/**
 * Convert flicks to beats based on tempo
 */
export function flicksToBeats(flicks: number, tempo: number): number {
  // Direct calculation: flicks * tempo / (60 * FLICKS_PER_SECOND)
  return (flicks * tempo) / (60 * FLICKS_PER_SECOND);
}

/**
 * Convert pixels to flicks directly
 * This avoids the pixel -> beats -> flicks conversion chain
 */
export function pixelsToFlicks(pixels: number, pixelsPerBeat: number, tempo: number): number {
  // Formula: pixels * 60 * FLICKS_PER_SECOND / (pixelsPerBeat * tempo)
  return (pixels * 60 * FLICKS_PER_SECOND) / (pixelsPerBeat * tempo);
}

/**
 * Convert flicks to pixels directly
 */
export function flicksToPixels(flicks: number, pixelsPerBeat: number, tempo: number): number {
  // Formula: flicks * pixelsPerBeat * tempo / (60 * FLICKS_PER_SECOND)
  return (flicks * pixelsPerBeat * tempo) / (60 * FLICKS_PER_SECOND);
}

/**
 * Convert pixels to beats with higher precision
 */
export function pixelsToBeats(pixels: number, pixelsPerBeat: number): number {
  return pixels / pixelsPerBeat;
}

/**
 * Convert beats to pixels
 */
export function beatsToPixels(beats: number, pixelsPerBeat: number): number {
  return beats * pixelsPerBeat;
}

/**
 * Convert a note duration in beats to flicks
 */
export function noteDurationToFlicks(duration: number, tempo: number): number {
  return beatsToFlicks(duration, tempo);
}

/**
 * Convert time signature and snap setting to flicks
 */
export function snapToFlicks(snapSetting: string, timeSignature: { numerator: number, denominator: number }, tempo: number): number {
  if (snapSetting === 'none') {
    return 0;
  }
  
  const [numerator, denominator] = snapSetting.split('/').map(Number);
  const beatsPerSnap = 1 / denominator;
  return beatsToFlicks(beatsPerSnap, tempo);
}

/**
 * Round flicks to nearest integer when precision is not critical
 */
export function roundFlicks(flicks: number): number {
  return Math.round(flicks);
}

/**
 * Format flicks to a human-readable string (useful for debugging)
 */
export function formatFlicks(flicks: number): string {
  const seconds = flicksToSeconds(flicks);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toFixed(3)}`;
}

/**
 * Get the exact flicks value for common note divisions
 * This ensures precise timing for standard musical divisions
 */
export function getExactNoteFlicks(noteDivision: string, tempo: number): number {
  const divisions: { [key: string]: number } = {
    '1/1': 4,     // Whole note = 4 beats
    '1/2': 2,     // Half note = 2 beats
    '1/4': 1,     // Quarter note = 1 beat
    '1/8': 0.5,   // Eighth note = 0.5 beats
    '1/16': 0.25, // Sixteenth note = 0.25 beats
    '1/32': 0.125 // Thirty-second note = 0.125 beats
  };
  
  const beats = divisions[noteDivision];
  if (beats === undefined) {
    throw new Error(`Unknown note division: ${noteDivision}`);
  }
  
  return beatsToFlicks(beats, tempo);
}

/**
 * Convert pixels to seconds for direct audio processing
 */
export function pixelsToSeconds(pixels: number, pixelsPerBeat: number, tempo: number): number {
  return (pixels * 60) / (pixelsPerBeat * tempo);
}

/**
 * Convert seconds to pixels
 */
export function secondsToPixels(seconds: number, pixelsPerBeat: number, tempo: number): number {
  return (seconds * pixelsPerBeat * tempo) / 60;
}

/**
 * Convert pixels to MIDI ticks
 */
export function pixelsToTicks(pixels: number, pixelsPerBeat: number, ppqn: number = 480): number {
  const beats = pixelsToBeats(pixels, pixelsPerBeat);
  return Math.round(beats * ppqn);
}

/**
 * Convert MIDI ticks to pixels
 */
export function ticksToPixels(ticks: number, pixelsPerBeat: number, ppqn: number = 480): number {
  const beats = ticks / ppqn;
  return beatsToPixels(beats, pixelsPerBeat);
}

/**
 * Convert pixels to audio samples
 */
export function pixelsToSamples(pixels: number, pixelsPerBeat: number, tempo: number, sampleRate: number = 44100): number {
  const seconds = pixelsToSeconds(pixels, pixelsPerBeat, tempo);
  return Math.round(seconds * sampleRate);
}

/**
 * Convert audio samples to pixels
 */
export function samplesToPixels(samples: number, pixelsPerBeat: number, tempo: number, sampleRate: number = 44100): number {
  const seconds = samples / sampleRate;
  return secondsToPixels(seconds, pixelsPerBeat, tempo);
}

/**
 * Calculate all timing representations for a given pixel value
 */
export function calculateAllTimingData(pixels: number, pixelsPerBeat: number, tempo: number, 
                                     sampleRate: number = 44100, ppqn: number = 480) {
  return {
    seconds: pixelsToSeconds(pixels, pixelsPerBeat, tempo),
    beats: pixelsToBeats(pixels, pixelsPerBeat),
    flicks: pixelsToFlicks(pixels, pixelsPerBeat, tempo),
    ticks: pixelsToTicks(pixels, pixelsPerBeat, ppqn),
    samples: pixelsToSamples(pixels, pixelsPerBeat, tempo, sampleRate)
  };
}
