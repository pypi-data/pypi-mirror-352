/**
 * Audio Engine for rendering and playing notes
 * Uses Web Audio API to synthesize sounds based on note data
 */
import { flicksToSeconds, beatsToFlicks, secondsToFlicks } from './flicks';

// MIDI note to frequency conversion (A4 = 69 = 440Hz)
function midiToFreq(midi: number): number {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

class AudioEngine {
  private audioContext: AudioContext | null = null;
  private gainNode: GainNode | null = null;
  private analyserNode: AnalyserNode | null = null;
  private renderBuffer: AudioBuffer | null = null;
  private renderSource: AudioBufferSourceNode | null = null;
  private isPlaying = false;
  private startTime = 0;
  private playbackStartFlicks = 0;
  private currentPlaybackFlicks = 0;
  private onPlayheadUpdate: ((flicks: number) => void) | null = null;
  private rafId: number | null = null;
  
  // Initialize the audio context
  initialize(): void {
    if (this.audioContext) return;
    
    this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    this.gainNode = this.audioContext.createGain();
    this.analyserNode = this.audioContext.createAnalyser();
    
    // Configure analyzer for waveform visualization
    this.analyserNode.fftSize = 2048;
    
    // Connect nodes
    this.gainNode.connect(this.analyserNode);
    this.analyserNode.connect(this.audioContext.destination);
    
    // Set initial volume
    this.gainNode.gain.value = 0.7;
  }
  
  // Clean up resources
  dispose(): void {
    this.stop();
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
      this.gainNode = null;
      this.analyserNode = null;
      this.renderBuffer = null;
    }
  }
  
  // Create a basic synth tone for a note
  private createNoteTone(
    ctx: BaseAudioContext, // Changed from AudioContext to BaseAudioContext to work with both regular and offline contexts
    time: number,
    duration: number,
    frequency: number,
    velocity: number,
    destination: AudioNode
  ): void {
    // Create oscillator and gain nodes
    const oscillator = ctx.createOscillator();
    const noteGain = ctx.createGain();
    
    // Configure oscillator
    oscillator.type = 'sine';
    oscillator.frequency.value = frequency;
    
    // Configure envelope
    const velocityGain = velocity / 127; // MIDI velocity is 0-127
    noteGain.gain.value = 0;
    
    // Attack
    noteGain.gain.setValueAtTime(0, time);
    noteGain.gain.linearRampToValueAtTime(velocityGain, time + 0.02);
    
    // Decay and sustain
    noteGain.gain.linearRampToValueAtTime(velocityGain * 0.7, time + 0.05);
    
    // Release
    noteGain.gain.linearRampToValueAtTime(velocityGain * 0.7, time + duration - 0.05);
    noteGain.gain.linearRampToValueAtTime(0, time + duration);
    
    // Connect nodes
    oscillator.connect(noteGain);
    noteGain.connect(destination);
    
    // Schedule note
    oscillator.start(time);
    oscillator.stop(time + duration);
  }
  
  // Render notes to an audio buffer
  async renderNotes(
    notes: Array<{
      id: string;
      start: number;
      duration: number;
      pitch: number;
      velocity: number;
    }>,
    tempo: number,
    totalLengthInBeats: number,
    pixelsPerBeat: number = 80 // Add pixelsPerBeat parameter with default value
  ): Promise<AudioBuffer> {
    this.initialize();
    if (!this.audioContext) throw new Error('Audio context not initialized');
    
    // Calculate total duration in seconds
    const totalDurationFlicks = beatsToFlicks(totalLengthInBeats, tempo);
    const totalDuration = flicksToSeconds(totalDurationFlicks);
    
    // Create an offline audio context for rendering
    const offlineCtx = new OfflineAudioContext(
      2, // stereo
      this.audioContext.sampleRate * totalDuration,
      this.audioContext.sampleRate
    );
    
    // Create a gain node in the offline context
    const offlineGain = offlineCtx.createGain();
    offlineGain.connect(offlineCtx.destination);
    
    // Render each note
    notes.forEach(note => {
      // Convert from pixels to beats using pixelsPerBeat as the conversion factor
      const noteStartBeats = note.start / pixelsPerBeat;
      const noteDurationBeats = note.duration / pixelsPerBeat;
      
      // Convert from beats to flicks
      const noteStartFlicks = beatsToFlicks(noteStartBeats, tempo);
      const noteDurationFlicks = beatsToFlicks(noteDurationBeats, tempo);
      
      const noteStartTime = flicksToSeconds(noteStartFlicks);
      const noteDuration = flicksToSeconds(noteDurationFlicks);
      
      // Create the note tone
      this.createNoteTone(
        offlineCtx,
        noteStartTime,
        noteDuration,
        midiToFreq(note.pitch),
        note.velocity,
        offlineGain
      );
    });
    
    // Render the audio
    const renderedBuffer = await offlineCtx.startRendering();
    this.renderBuffer = renderedBuffer;
    
    return renderedBuffer;
  }
  
  // Play the rendered audio buffer
  play(startPositionInFlicks: number = 0): void {
    if (!this.audioContext || !this.renderBuffer || this.isPlaying) return;
    
    // Resume audio context if suspended
    if (this.audioContext.state === 'suspended') {
      this.audioContext.resume();
    }
    
    // Create a new source for the audio buffer
    this.renderSource = this.audioContext.createBufferSource();
    this.renderSource.buffer = this.renderBuffer;
    this.renderSource.connect(this.gainNode!);
    
    // Calculate start position in seconds
    const startPositionInSeconds = flicksToSeconds(startPositionInFlicks);
    const currentTime = this.audioContext.currentTime;
    
    // Start playback
    this.renderSource.start(currentTime, startPositionInSeconds);
    this.startTime = currentTime - startPositionInSeconds;
    this.playbackStartFlicks = startPositionInFlicks;
    this.isPlaying = true;
    
    // Start updating playhead position
    this.updatePlayhead();
    
    // Set up ended event
    this.renderSource.onended = () => {
      this.isPlaying = false;
      this.renderSource = null;
      if (this.rafId) {
        cancelAnimationFrame(this.rafId);
        this.rafId = null;
      }
    };
  }
  
  // Stop playback
  stop(): void {
    if (!this.isPlaying || !this.renderSource) return;
    
    this.renderSource.stop();
    this.renderSource = null;
    this.isPlaying = false;
    
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }
  
  // Pause playback
  pause(): void {
    if (!this.isPlaying) return;
    
    // Store current position
    this.currentPlaybackFlicks = this.getCurrentPositionInFlicks();
    this.stop();
  }
  
  // Resume playback from paused position
  resume(): void {
    if (this.isPlaying) return;
    this.play(this.currentPlaybackFlicks);
  }
  
  // Toggle play/pause
  togglePlayback(): void {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.resume();
    }
  }
  
  // Get current playback position in flicks
  getCurrentPositionInFlicks(): number {
    if (!this.audioContext || !this.isPlaying) {
      return this.currentPlaybackFlicks;
    }
    
    const elapsedSeconds = this.audioContext.currentTime - this.startTime;
    return this.playbackStartFlicks + secondsToFlicks(elapsedSeconds);
  }
  
  // Update playhead position
  private updatePlayhead(): void {
    if (!this.isPlaying || !this.onPlayheadUpdate) {
      if (this.rafId) {
        cancelAnimationFrame(this.rafId);
        this.rafId = null;
      }
      return;
    }
    
    const currentFlicks = this.getCurrentPositionInFlicks();
    this.onPlayheadUpdate(currentFlicks);
    
    this.rafId = requestAnimationFrame(() => this.updatePlayhead());
  }
  
  // Set callback for playhead updates
  setPlayheadUpdateCallback(callback: (flicks: number) => void): void {
    this.onPlayheadUpdate = callback;
  }
  
  // Get analyzer node for waveform visualization
  getAnalyserNode(): AnalyserNode | null {
    return this.analyserNode;
  }
  
  // Get current waveform data
  getWaveformData(): Float32Array | null {
    if (!this.analyserNode) return null;
    
    const bufferLength = this.analyserNode.frequencyBinCount;
    const dataArray = new Float32Array(bufferLength);
    this.analyserNode.getFloatTimeDomainData(dataArray);
    
    return dataArray;
  }
  
  // Check if currently playing
  isCurrentlyPlaying(): boolean {
    return this.isPlaying;
  }
  
  // Get rendered buffer
  getRenderedBuffer(): AudioBuffer | null {
    return this.renderBuffer;
  }
}

// Export singleton instance
export const audioEngine = new AudioEngine();
