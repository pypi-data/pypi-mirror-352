# Timing Conversions in Gradio Piano Roll

## Overview

The Gradio Piano Roll component now provides comprehensive timing data in multiple formats to support various audio processing and generation needs. Each note contains timing information in 6 different formats for maximum compatibility with audio libraries and MIDI standards.

## Available Timing Formats

### 1. Pixel-based (UI Coordinates)
- `start`: Start position in pixels
- `duration`: Duration in pixels
- Used for: UI positioning and user interactions

### 2. Flicks-based (High Precision)
- `startFlicks`: Start time in flicks (1/705,600,000 second units)
- `durationFlicks`: Duration in flicks
- Used for: High-precision timing calculations without floating-point errors

### 3. Seconds-based (Audio Processing)
- `startSeconds`: Start time in seconds (decimal)
- `durationSeconds`: Duration in seconds (decimal)
- `endSeconds`: End time in seconds (startSeconds + durationSeconds)
- Used for: Direct audio file generation, librosa, soundfile, pydub

### 4. Beats-based (Musical)
- `startBeats`: Start position in musical beats (decimal)
- `durationBeats`: Duration in musical beats (decimal)
- Used for: Musical analysis and tempo-relative operations

### 5. MIDI Ticks-based (MIDI Standard)
- `startTicks`: Start position in MIDI ticks (integer)
- `durationTicks`: Duration in MIDI ticks (integer)
- Used for: MIDI file generation, mido library

### 6. Sample-based (Digital Audio)
- `startSample`: Start position in audio samples (integer, 44.1kHz)
- `durationSamples`: Duration in audio samples (integer, 44.1kHz)
- Used for: Low-level audio processing, numpy/scipy

## Configuration Parameters

### Global Settings
- `sampleRate`: Audio sample rate (default: 44100 Hz)
- `ppqn`: Pulses Per Quarter Note for MIDI (default: 480)
- `tempo`: Beats per minute
- `pixelsPerBeat`: Zoom level (pixels per beat)

## Example Note Data Structure

```python
note = {
    "id": "note-1234567890-abcde",
    
    # Pixel-based (UI)
    "start": 80,
    "duration": 80,
    
    # Flicks-based (High precision)
    "startFlicks": 17640000000,
    "durationFlicks": 17640000000,
    
    # Seconds-based (Audio)
    "startSeconds": 0.25,
    "durationSeconds": 0.25,
    "endSeconds": 0.5,
    
    # Beats-based (Musical)
    "startBeats": 0.5,
    "durationBeats": 0.5,
    
    # MIDI Ticks-based (MIDI)
    "startTicks": 240,
    "durationTicks": 240,
    
    # Sample-based (Digital Audio)
    "startSample": 11025,
    "durationSamples": 11025,
    
    # Musical properties
    "pitch": 60,      # MIDI note number (0-127)
    "velocity": 100,  # MIDI velocity (0-127)
    "lyric": "안녕"    # Optional text
}
```

## Python Audio Generation Examples

### Using librosa/soundfile (seconds-based)
```python
import librosa
import soundfile as sf
import numpy as np

def generate_audio_from_notes(notes, tempo, sample_rate=44100):
    # Find total duration from notes
    max_end = max(note['endSeconds'] for note in notes)
    
    # Create audio buffer
    audio = np.zeros(int(max_end * sample_rate))
    
    for note in notes:
        # Use seconds-based timing directly
        start_sample = int(note['startSeconds'] * sample_rate)
        duration_samples = int(note['durationSeconds'] * sample_rate)
        
        # Generate tone
        frequency = 440 * (2 ** ((note['pitch'] - 69) / 12))
        t = np.linspace(0, note['durationSeconds'], duration_samples)
        tone = np.sin(2 * np.pi * frequency * t) * (note['velocity'] / 127)
        
        # Add to audio buffer
        audio[start_sample:start_sample + duration_samples] += tone
    
    return audio

# Usage
audio = generate_audio_from_notes(notes_data['notes'], notes_data['tempo'])
sf.write('output.wav', audio, 44100)
```

### Using mido (MIDI ticks-based)
```python
import mido

def create_midi_from_notes(notes, tempo, ppqn=480):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo
    tempo_msg = mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo))
    track.append(tempo_msg)
    
    # Sort notes by start time
    sorted_notes = sorted(notes, key=lambda n: n['startTicks'])
    
    current_tick = 0
    for note in sorted_notes:
        # Calculate delta time from last event
        delta_time = note['startTicks'] - current_tick
        
        # Note on
        note_on = mido.Message('note_on', 
                              channel=0, 
                              note=note['pitch'], 
                              velocity=note['velocity'], 
                              time=delta_time)
        track.append(note_on)
        
        # Note off
        note_off = mido.Message('note_off', 
                               channel=0, 
                               note=note['pitch'], 
                               velocity=0, 
                               time=note['durationTicks'])
        track.append(note_off)
        
        current_tick = note['startTicks'] + note['durationTicks']
    
    return mid

# Usage
mid = create_midi_from_notes(notes_data['notes'], notes_data['tempo'], notes_data['ppqn'])
mid.save('output.mid')
```

### Using numpy (sample-based)
```python
import numpy as np

def generate_raw_audio(notes, sample_rate=44100):
    # Find total length in samples
    max_end_sample = max(note['startSample'] + note['durationSamples'] for note in notes)
    
    # Create audio buffer
    audio = np.zeros(max_end_sample, dtype=np.float32)
    
    for note in notes:
        # Use sample-based timing directly - no conversion needed
        start_idx = note['startSample']
        end_idx = start_idx + note['durationSamples']
        
        # Generate tone
        frequency = 440 * (2 ** ((note['pitch'] - 69) / 12))
        samples = np.arange(note['durationSamples'])
        tone = np.sin(2 * np.pi * frequency * samples / sample_rate)
        tone *= note['velocity'] / 127
        
        # Add to buffer
        audio[start_idx:end_idx] += tone
    
    return audio

# Usage
audio = generate_raw_audio(notes_data['notes'], notes_data['sampleRate'])
```

### Using pydub (seconds-based with millisecond conversion)
```python
from pydub import AudioSegment
from pydub.generators import Sine

def create_pydub_audio(notes, tempo):
    # Find total duration in milliseconds
    max_end_ms = max(note['endSeconds'] * 1000 for note in notes)
    
    # Create silent base track
    audio = AudioSegment.silent(duration=int(max_end_ms))
    
    for note in notes:
        # Convert seconds to milliseconds for pydub
        start_ms = int(note['startSeconds'] * 1000)
        duration_ms = int(note['durationSeconds'] * 1000)
        
        # Generate tone
        frequency = 440 * (2 ** ((note['pitch'] - 69) / 12))
        tone = Sine(frequency).to_audio_segment(duration=duration_ms)
        
        # Apply velocity (volume)
        volume_db = (note['velocity'] / 127) * 20 - 20  # Convert to dB
        tone = tone + volume_db
        
        # Overlay at correct position
        audio = audio.overlay(tone, position=start_ms)
    
    return audio

# Usage
audio = create_pydub_audio(notes_data['notes'], notes_data['tempo'])
audio.export("output.wav", format="wav")
```

## Benefits

1. **No Conversion Required**: Choose the timing format that matches your audio library
2. **Precision**: Use flicks for high-precision calculations, samples for exact sample alignment
3. **Compatibility**: Works with all major Python audio libraries
4. **Efficiency**: Avoid repeated conversions in audio processing loops
5. **MIDI Standard**: Direct MIDI tick support for professional music software

## Automatic Generation

All timing data is automatically calculated and maintained by the piano roll component:
- When notes are created, moved, or resized
- When tempo or zoom level changes
- When importing existing note data (backward compatibility)

The system ensures all timing formats stay synchronized and accurate.

## Additional Audio Generation Examples

### Real-time Audio with Custom Synthesis
```python
def synthesize_note_with_envelope(note, sample_rate=44100):
    """Generate audio for a single note with ADSR envelope"""
    duration_samples = note['durationSamples']
    frequency = 440 * (2 ** ((note['pitch'] - 69) / 12))
    velocity = note['velocity'] / 127
    
    # Generate samples
    t = np.arange(duration_samples) / sample_rate
    audio = np.sin(2 * np.pi * frequency * t)
    
    # Apply ADSR envelope
    attack_samples = int(0.01 * sample_rate)  # 10ms attack
    decay_samples = int(0.1 * sample_rate)    # 100ms decay
    sustain_level = 0.7
    release_samples = int(0.2 * sample_rate)  # 200ms release
    
    envelope = np.ones_like(audio)
    
    # Attack
    if len(envelope) > attack_samples:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay
    if len(envelope) > attack_samples + decay_samples:
        envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain_level, decay_samples)
    
    # Release
    if len(envelope) > release_samples:
        envelope[-release_samples:] = np.linspace(sustain_level, 0, release_samples)
    
    return audio * envelope * velocity

def render_full_song(notes, sample_rate=44100):
    """Render complete song with polyphonic synthesis"""
    max_end_sample = max(note['startSample'] + note['durationSamples'] for note in notes)
    final_audio = np.zeros(max_end_sample, dtype=np.float32)
    
    for note in notes:
        note_audio = synthesize_note_with_envelope(note, sample_rate)
        start_idx = note['startSample']
        end_idx = start_idx + len(note_audio)
        final_audio[start_idx:end_idx] += note_audio
    
    # Normalize to prevent clipping
    max_amplitude = np.max(np.abs(final_audio))
    if max_amplitude > 0:
        final_audio = final_audio / max_amplitude * 0.8
    
    return final_audio
```

This comprehensive timing system enables seamless integration with any Python audio processing workflow while maintaining precision and performance.

## Additional Timing Data

The system now includes additional timing formats specifically designed for audio file generation:

### Audio Processing Formats
All timing data is automatically calculated and synchronized:

1. **Seconds**: Direct compatibility with librosa, soundfile, scipy.io.wavfile
2. **Beats**: Musical timing for tempo-based operations  
3. **MIDI Ticks**: Standard MIDI compatibility for mido, pretty_midi
4. **Samples**: Raw audio sample positioning for numpy, low-level processing
5. **Flicks**: High-precision timing to avoid floating-point errors

### Use Case Examples
- **librosa/soundfile**: Use `startSeconds`, `durationSeconds`
- **mido MIDI**: Use `startTicks`, `durationTicks` with `ppqn`
- **numpy audio**: Use `startSample`, `durationSamples` with `sampleRate`
- **pydub**: Convert `startSeconds * 1000` to milliseconds
- **scipy.signal**: Use sample-based timing for filtering/processing

All formats are automatically maintained and synchronized when notes are created, edited, or when tempo/zoom changes occur. 