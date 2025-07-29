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
 * Convert seconds to flicks
 */
export function secondsToFlicks(seconds: number): number {
  return Math.round(seconds * FLICKS_PER_SECOND);
}

/**
 * Convert flicks to seconds
 */
export function flicksToSeconds(flicks: number): number {
  return flicks / FLICKS_PER_SECOND;
}

/**
 * Convert beats to flicks based on tempo
 */
export function beatsToFlicks(beats: number, tempo: number): number {
  // beats * 60 seconds per minute / tempo = seconds
  // then convert seconds to flicks
  const seconds = (beats * 60) / tempo;
  return secondsToFlicks(seconds);
}

/**
 * Convert flicks to beats based on tempo
 */
export function flicksToBeats(flicks: number, tempo: number): number {
  // Convert flicks to seconds
  const seconds = flicksToSeconds(flicks);
  // Convert seconds to beats: seconds * tempo / 60
  return seconds * tempo / 60;
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
 * Format flicks to a human-readable string (useful for debugging)
 */
export function formatFlicks(flicks: number): string {
  const seconds = flicksToSeconds(flicks);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toFixed(3)}`;
}
