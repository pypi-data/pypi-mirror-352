<!--
  GridComponent for displaying and editing notes and lyrics.
  This component uses canvas to render the grid, notes, and lyrics.
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { pixelsToFlicks, flicksToPixels, getExactNoteFlicks, roundFlicks, calculateAllTimingData } from '../utils/flicks';

  // Props
  export let width = 880;  // Width of the grid (total width - keyboard width)
  export let height = 520;  // Height of the grid
  export let notes: Array<{
    id: string,
    start: number,
    duration: number,
    startFlicks?: number,      // Optional for backward compatibility
    durationFlicks?: number,   // Optional for backward compatibility
    startSeconds?: number,     // Optional - seconds timing
    durationSeconds?: number,  // Optional - seconds timing
    endSeconds?: number,       // Optional - end time in seconds
    startBeats?: number,       // Optional - beats timing
    durationBeats?: number,    // Optional - beats timing
    startTicks?: number,       // Optional - MIDI ticks timing
    durationTicks?: number,    // Optional - MIDI ticks timing
    startSample?: number,      // Optional - sample timing
    durationSamples?: number,  // Optional - sample timing
    pitch: number,
    velocity: number,
    lyric?: string,
    phoneme?: string
  }> = [];
  // Tempo is used to calculate timing and note positioning
  export let tempo = 120;  // BPM

  // Calculate pixels per second based on tempo
  $: pixelsPerSecond = (tempo / 60) * pixelsPerBeat;
  export let timeSignature = { numerator: 4, denominator: 4 };
  export let editMode = 'draw';  // Current edit mode
  export let snapSetting = '1/8';  // Snap grid setting (1/1, 1/2, 1/4, 1/8, 1/16, 1/32, none)
  export let horizontalScroll = 0;  // Horizontal scroll position
  export let verticalScroll = 0;  // Vertical scroll position
  export let currentFlicks = 0;  // Current playback position in flicks (added for playhead tracking)
  export let isPlaying = false;  // Whether playback is active

  // Audio metadata
  export let sampleRate = 44100; // Audio sample rate
  export let ppqn = 480;         // MIDI pulses per quarter note

  // Constants
  const NOTE_HEIGHT = 20;  // Height of a note row (same as white key height)
  const GRID_COLOR = '#444444';
  const BEAT_COLOR = '#555555';
  const MEASURE_COLOR = '#666666';
  const NOTE_COLOR = '#2196F3';
  const NOTE_SELECTED_COLOR = '#03A9F4';
  const LYRIC_COLOR = '#FFFFFF';

  // Sizing and grid constants
  const TOTAL_NOTES = 128;  // Total MIDI notes
  const GRID_LINE_INTERVAL = NOTE_HEIGHT;  // Distance between horizontal grid lines
  export let pixelsPerBeat = 80;  // How many pixels wide a beat is (controls zoom level)

  // Get subdivisions based on time signature denominator
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
        return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 };
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
        case 1: // Whole note - 1 division per measure (4 beats in 4/4)
          return { count: 1, pixelsPerSubdivision: pixelsPerBeat };
        case 2: // Half note - 2 divisions per beat
          return { count: 2, pixelsPerSubdivision: pixelsPerBeat / 2 };
        case 4: // Quarter note - 4 divisions per beat
          return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 };
        case 8: // Eighth note - 8 divisions per beat
          return { count: 8, pixelsPerSubdivision: pixelsPerBeat / 8 };
        case 16: // Sixteenth note - 16 divisions per beat
          return { count: 16, pixelsPerSubdivision: pixelsPerBeat / 16 };
        case 32: // Thirty-second note - 32 divisions per beat
          return { count: 32, pixelsPerSubdivision: pixelsPerBeat / 32 };
        default:
          return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 };
      }
    }

    // Default to quarter note subdivisions
    return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 };
  }

  // Derived grid constants based on time signature and snap setting
  $: subdivisions = getSubdivisionsFromSnapSetting();
  $: snapChanged = snapSetting; // Reactive variable to trigger redraw when snap changes

  // State
  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null = null;
  let isDragging = false;
  let isResizing = false;
  let isCreatingNote = false;
  let selectedNotes: Set<string> = new Set();
  let dragStartX = 0;
  let dragStartY = 0;
  let lastMouseX = 0;
  let lastMouseY = 0;
  let draggedNoteId: string | null = null;
  let resizedNoteId: string | null = null;
  let creationStartTime = 0;
  let creationPitch = 0;
  let noteOffsetX = 0; // Offset from mouse to note start for natural movement
  let noteOffsetY = 0; // Vertical offset for pitch adjustment
  let accumulatedDeltaX = 0; // Accumulated horizontal mouse movement
  let accumulatedDeltaY = 0; // Accumulated vertical mouse movement
  let isNearNoteEdge = false; // Track if mouse is near a note edge for resize cursor

  // Current mouse position info (for position display)
  let currentMousePosition = {
    x: 0,
    y: 0,
    measure: 0,
    beat: 0,
    tick: 0,
    pitch: 0,
    noteName: ''
  }

  // Keep track of the previous zoom level for scaling
  let previousPixelsPerBeat = pixelsPerBeat;

  // Lyric editing state
  let isEditingLyric = false;
  let editedNoteId: string | null = null;
  let lyricInputValue = '';
  let lyricInputPosition = { x: 0, y: 0, width: 0 };

  const dispatch = createEventDispatcher();

  // Calculate various dimensions and metrics
  $: totalGridHeight = TOTAL_NOTES * NOTE_HEIGHT;
  $: beatsPerMeasure = timeSignature.numerator;
  $: pixelsPerMeasure = beatsPerMeasure * pixelsPerBeat;

  // Calculate how many measures to show based on width
  $: totalMeasures = 32;  // Adjustable
  $: totalGridWidth = totalMeasures * pixelsPerMeasure;

  // Handle scrolling
  function handleScroll(event: WheelEvent) {
    event.preventDefault();

    // Vertical scrolling with mouse wheel
    if (event.deltaY !== 0) {
      const newVerticalScroll = Math.max(
        0,
        Math.min(
          totalGridHeight - height,
          verticalScroll + event.deltaY
        )
      );

      if (newVerticalScroll !== verticalScroll) {
        verticalScroll = newVerticalScroll;
        dispatch('scroll', { horizontalScroll, verticalScroll });
      }
    }

    // Horizontal scrolling with shift+wheel or trackpad
    if (event.deltaX !== 0 || event.shiftKey) {
      const deltaX = event.deltaX || event.deltaY;
      const newHorizontalScroll = Math.max(
        0,
        Math.min(
          totalGridWidth - width,
          horizontalScroll + deltaX
        )
      );

      if (newHorizontalScroll !== horizontalScroll) {
        horizontalScroll = newHorizontalScroll;
        dispatch('scroll', { horizontalScroll, verticalScroll });
      }
    }

    // Redraw with new scroll positions
    drawGrid();
  }

  // Mouse events for note manipulation
  function handleMouseDown(event: MouseEvent) {
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left + horizontalScroll;
    const y = event.clientY - rect.top + verticalScroll;

    // Store initial position for drag operations
    dragStartX = x;
    dragStartY = y;
    lastMouseX = x;
    lastMouseY = y;

    // Reset accumulated deltas when starting a new drag operation
    accumulatedDeltaX = 0;
    accumulatedDeltaY = 0;

    // For drag operations, store the offset from the mouse to the note start
    // This will help position notes more naturally when dragging
    if (editMode === 'select') {
      const clickedNote = findNoteAtPosition(x, y);
      if (clickedNote && Math.abs(x - (clickedNote.start + clickedNote.duration)) >= 10) {
        // Store the offset from mouse position to note start
        // This will be used to maintain the same relative position during dragging
        noteOffsetX = clickedNote.start - x;
        noteOffsetY = (TOTAL_NOTES - 1 - clickedNote.pitch) * NOTE_HEIGHT - y;
      }
    }

    // Check if clicking on a note
    const clickedNote = findNoteAtPosition(x, y);

    if (editMode === 'draw' && !clickedNote) {
      // Start note creation process
      const pitch = Math.floor(y / NOTE_HEIGHT);
      const time = snapToGrid(x);

      // Store the starting position and pitch for the new note
      creationStartTime = time;
      creationPitch = TOTAL_NOTES - 1 - pitch;

      // Calculate initial note duration based on snap setting (one beat divided by n)
      let initialDuration = pixelsPerBeat / 4; // Default: quarter note (1/4)

      // Parse the snap setting to determine initial note duration
      if (snapSetting !== 'none') {
        const [numerator, denominator] = snapSetting.split('/');
        if (numerator === '1' && denominator) {
          const divisionValue = parseInt(denominator);
          // Calculate duration in pixels based on snap setting
          // For 1/1: one full beat (pixelsPerBeat)
          // For 1/2: half beat (pixelsPerBeat / 2)
          // For 1/4: quarter beat (pixelsPerBeat / 4)
          // etc.
          initialDuration = pixelsPerBeat / divisionValue;
        }
      } else {
        // When snap is 'none', use a small default size
        initialDuration = pixelsPerBeat / 8;
      }

      // Calculate timing data for start position and duration
      const startTiming = calculateAllTimingData(time, pixelsPerBeat, tempo, sampleRate, ppqn);
      const durationTiming = calculateAllTimingData(initialDuration, pixelsPerBeat, tempo, sampleRate, ppqn);

      // Create a new note with duration based on snap setting
      const newNote = {
        id: `note-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
        start: time,
        duration: initialDuration,
        pitch: creationPitch,
        velocity: 100,
        lyric: '라',  // Default lyric is '라'
        startFlicks: startTiming.flicks,
        durationFlicks: durationTiming.flicks,
        startSeconds: startTiming.seconds,
        durationSeconds: durationTiming.seconds,
        endSeconds: startTiming.seconds + durationTiming.seconds,
        startBeats: startTiming.beats,
        durationBeats: durationTiming.beats,
        startTicks: startTiming.ticks,
        durationTicks: durationTiming.ticks,
        startSample: startTiming.samples,
        durationSamples: durationTiming.samples
      };

      // Add note to the collection
      notes = [...notes, newNote];

      // Set note as selected and being resized
      selectedNotes = new Set([newNote.id]);
      resizedNoteId = newNote.id;  // We're resizing, not dragging
      isCreatingNote = true;       // Flag that we're in note creation mode
      isResizing = true;          // Enable resizing mode

      dispatch('noteChange', { notes });
    }
    else if (editMode === 'erase' && clickedNote) {
      // Erase clicked note
      notes = notes.filter(note => note.id !== clickedNote.id);
      selectedNotes.delete(clickedNote.id);

      dispatch('noteChange', { notes });
    }
    else if (editMode === 'select') {
      if (clickedNote) {
        // Check if clicking near the end of the note (for resizing)
        const noteEndX = clickedNote.start + clickedNote.duration;
        // Edge detection threshold scales with zoom level
        const edgeDetectionThreshold = Math.max(5, Math.min(15, pixelsPerBeat / 8));
        if (Math.abs(x - noteEndX) < edgeDetectionThreshold) {
          // Start resizing - similar to draw mode
          isResizing = true;
          resizedNoteId = clickedNote.id;
          // Store the original note start position for absolute resizing calculation
          creationStartTime = clickedNote.start;
        } else {
          // Select and drag note
          if (!event.shiftKey) {
            // If not holding shift, clear previous selection
            if (!selectedNotes.has(clickedNote.id)) {
              selectedNotes = new Set([clickedNote.id]);
            }
          } else {
            // Add to selection with shift key
            selectedNotes.add(clickedNote.id);
          }

          isDragging = true;
          draggedNoteId = clickedNote.id;
        }
      } else {
        // Clicked empty space, clear selection unless shift is held
        if (!event.shiftKey) {
          selectedNotes = new Set();
        }
      }
    }

    // Redraw
    drawGrid();
  }

  function handleMouseMove(event: MouseEvent) {
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left + horizontalScroll;
    const y = event.clientY - rect.top + verticalScroll;

    const deltaX = x - lastMouseX;
    const deltaY = y - lastMouseY;

    lastMouseX = x;
    lastMouseY = y;

    // Update mouse position information
    updateMousePositionInfo(x, y);

    // Check if mouse is near any note edge for resize cursor
    if (editMode === 'select' && !isDragging && !isResizing) {
      const clickedNote = findNoteAtPosition(x, y);
      if (clickedNote) {
        const noteEndX = clickedNote.start + clickedNote.duration;
        // Edge detection threshold scales with zoom level
        const edgeDetectionThreshold = Math.max(5, Math.min(15, pixelsPerBeat / 8));
        // If mouse is within threshold pixels of the note edge, show resize cursor
        isNearNoteEdge = Math.abs(x - noteEndX) < edgeDetectionThreshold;
      } else {
        isNearNoteEdge = false;
      }
    }

    if (isDragging && draggedNoteId && editMode === 'select') {
      // Calculate grid size based on snap setting
      let gridSize;
      if (snapSetting === 'none') {
        // When snap is off, use a small default size for fine control
        gridSize = pixelsPerBeat / 32;
      } else {
        // Parse the snap setting fraction
        let divisionValue = 4; // Default to quarter note (1/4)
        const [numerator, denominator] = snapSetting.split('/');
        if (numerator === '1' && denominator) {
          divisionValue = parseInt(denominator);
        }
        gridSize = pixelsPerBeat / divisionValue;
      }

      // Accumulate mouse movement to handle slow movements
      accumulatedDeltaX += deltaX;
      accumulatedDeltaY += deltaY;

      // Calculate how many grid cells to move based on accumulated movement
      // For horizontal movement, scale according to the current zoom level
      const gridMovementX = Math.floor(Math.abs(accumulatedDeltaX) / gridSize) * Math.sign(accumulatedDeltaX);
      const gridMovementY = Math.floor(Math.abs(accumulatedDeltaY) / NOTE_HEIGHT) * Math.sign(accumulatedDeltaY);

      // Only move notes if we've accumulated enough movement to cross a grid boundary
      if (gridMovementX !== 0 || gridMovementY !== 0) {
        // Move selected notes using grid-relative movements
        notes = notes.map(note => {
          if (selectedNotes.has(note.id)) {
            // Apply movement in grid units
            const newStart = Math.max(0, note.start + (gridMovementX * gridSize));
            const newPitch = Math.max(0, Math.min(127, note.pitch - gridMovementY));

            // Calculate all timing data for new start position
            const newStartTiming = calculateAllTimingData(newStart, pixelsPerBeat, tempo, sampleRate, ppqn);

            return {
              ...note,
              start: newStart,
              pitch: newPitch,
              startFlicks: newStartTiming.flicks,
              startSeconds: newStartTiming.seconds,
              startBeats: newStartTiming.beats,
              startTicks: newStartTiming.ticks,
              startSample: newStartTiming.samples,
              endSeconds: newStartTiming.seconds + (note.durationSeconds || 0)
            };
          }
          return note;
        });

        // Reduce accumulated movement by the amount we just used
        accumulatedDeltaX -= gridMovementX * gridSize;
        accumulatedDeltaY -= gridMovementY * NOTE_HEIGHT;
      }

      dispatch('noteChange', { notes });
      drawGrid();
    }
    else if (isResizing && resizedNoteId) {
      // Resize note
      notes = notes.map(note => {
        if (note.id === resizedNoteId) {
          let newDuration;

          // Get the grid size based on snap setting
          let gridSize;
          if (snapSetting === 'none') {
            // If snap is off, use a small default size for fine control
            gridSize = pixelsPerBeat / 32; // Very fine control
          } else {
            // Parse the snap setting fraction
            let divisionValue = 4; // Default to quarter note (1/4)
            const [numerator, denominator] = snapSetting.split('/');
            if (numerator === '1' && denominator) {
              divisionValue = parseInt(denominator);
            }
            // Grid size based on beat division
            gridSize = pixelsPerBeat / divisionValue;
          }

          // Use the same approach for both note creation and resize in select mode
          // Calculate width from the start position to the current mouse position
          const width = Math.max(gridSize, x - creationStartTime);

          // Snap the width to the grid based on current snap setting
          const snappedWidth = snapSetting === 'none'
            ? width
            : Math.round(width / gridSize) * gridSize;

          // Ensure minimum size
          newDuration = Math.max(gridSize, snappedWidth);

          // Calculate all timing data for new duration
          const newDurationTiming = calculateAllTimingData(newDuration, pixelsPerBeat, tempo, sampleRate, ppqn);

          return {
            ...note,
            duration: newDuration,
            durationFlicks: newDurationTiming.flicks,
            durationSeconds: newDurationTiming.seconds,
            durationBeats: newDurationTiming.beats,
            durationTicks: newDurationTiming.ticks,
            durationSamples: newDurationTiming.samples,
            endSeconds: (note.startSeconds || 0) + newDurationTiming.seconds
          };
        }
        return note;
      });

      dispatch('noteChange', { notes });
      drawGrid();
    }
  }

  function handleMouseUp() {
    // Check if we're finalizing note creation
    if (isCreatingNote) {
      // If the note is too small, remove it, but base minimum size on current snap setting
      if (resizedNoteId) {
        const createdNote = notes.find(note => note.id === resizedNoteId);

        // Calculate minimum note size based on snap setting
        let minimumNoteSize;
        if (snapSetting === 'none') {
          minimumNoteSize = pixelsPerBeat / 32; // Tiny minimum size when snap is off
        } else {
          // Parse the snap setting fraction
          let divisionValue = 4; // Default to quarter note (1/4)
          const [numerator, denominator] = snapSetting.split('/');
          if (numerator === '1' && denominator) {
            divisionValue = parseInt(denominator);
          }
          // Set minimum size to half the grid size for the current snap setting
          // Scaled appropriately with zoom level
          minimumNoteSize = (pixelsPerBeat / divisionValue) / 2;
        }

        // Now check if the note is too small based on the dynamic minimum size
        if (createdNote && createdNote.duration < minimumNoteSize) {
          // Remove notes that are too small (likely accidental clicks)
          notes = notes.filter(note => note.id !== resizedNoteId);
          dispatch('noteChange', { notes });
        }
      }

      // Reset creation state
      isCreatingNote = false;
    }

    // Reset interaction states
    isDragging = false;
    isResizing = false;
    isNearNoteEdge = false; // Reset resize cursor state
    draggedNoteId = null;
    resizedNoteId = null;

    // Redraw the grid
    drawGrid();
  }

  // Handle double-click to edit lyrics
  function handleDoubleClick(event: MouseEvent) {
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left + horizontalScroll;
    const y = event.clientY - rect.top + verticalScroll;

    // Find the note that was double-clicked
    const clickedNote = findNoteAtPosition(x, y);

    if (clickedNote) {
      // Set up lyric editing state
      editedNoteId = clickedNote.id;
      lyricInputValue = clickedNote.lyric || '';

      // Calculate position for the input field
      const noteY = (TOTAL_NOTES - 1 - clickedNote.pitch) * NOTE_HEIGHT - verticalScroll;

      lyricInputPosition = {
        x: clickedNote.start - horizontalScroll,
        y: noteY,
        width: clickedNote.duration
      };

      isEditingLyric = true;

      // Set a timeout to focus the input element once it's rendered
      setTimeout(() => {
        const input = document.getElementById('lyric-input');
        if (input) {
          input.focus();
        }
      }, 10);
    }
  }

  // Save the edited lyric
  function saveLyric() {
    if (!editedNoteId) return;

    // 이전 가사와 새 가사 저장
    const oldNote = notes.find(note => note.id === editedNoteId);
    const oldLyric = oldNote?.lyric || '';
    const newLyric = lyricInputValue;

    // Update the note with the new lyric
    notes = notes.map(note => {
      if (note.id === editedNoteId) {
        return {
          ...note,
          lyric: newLyric
        };
      }
      return note;
    });

    // 가사가 실제로 변경된 경우에만 이벤트 발생
    if (oldLyric !== newLyric) {
      // 먼저 input 이벤트 발생 (G2P 실행용)
      dispatch('lyricInput', {
        notes,
        lyricData: {
          noteId: editedNoteId,
          oldLyric,
          newLyric,
          note: notes.find(note => note.id === editedNoteId)
        }
      });
    } else {
      // 가사가 변경되지 않은 경우 일반 노트 변경 이벤트만 발생
      dispatch('noteChange', { notes });
    }

    // Reset editing state
    isEditingLyric = false;
    editedNoteId = null;

    // Redraw with updated lyrics
    drawGrid();
  }

  // Handle keydown in the lyric input
  function handleLyricInputKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      saveLyric();
    } else if (event.key === 'Escape') {
      // Cancel editing
      isEditingLyric = false;
      editedNoteId = null;
    }
  }

  // Helper to find a note at a specific position
  function findNoteAtPosition(x: number, y: number) {
    const pitch = TOTAL_NOTES - 1 - Math.floor(y / NOTE_HEIGHT);

    return notes.find(note => {
      const noteY = (TOTAL_NOTES - 1 - note.pitch) * NOTE_HEIGHT;
      return (
        x >= note.start &&
        x <= note.start + note.duration &&
        y >= noteY &&
        y <= noteY + NOTE_HEIGHT
      );
    });
  }

  // Coordinate conversion utility functions

  // Convert X coordinate to measure, beat, tick information
  function xToMeasureInfo(x: number) {
    // Calculate measure
    const measureIndex = Math.floor(x / pixelsPerMeasure);

    // Calculate beat within measure
    const xWithinMeasure = x - (measureIndex * pixelsPerMeasure);
    const beatWithinMeasure = Math.floor(xWithinMeasure / pixelsPerBeat);

    // Calculate tick within beat (based on current snap setting)
    let divisionValue = 4; // Default to quarter note (1/4)
    if (snapSetting !== 'none') {
      const [numerator, denominator] = snapSetting.split('/');
      if (numerator === '1' && denominator) {
        divisionValue = parseInt(denominator);
      }
    }

    const ticksPerBeat = divisionValue;
    const xWithinBeat = xWithinMeasure - (beatWithinMeasure * pixelsPerBeat);
    const tickWithinBeat = Math.floor((xWithinBeat / pixelsPerBeat) * ticksPerBeat);

    return {
      measure: measureIndex + 1, // 1-based measure number
      beat: beatWithinMeasure + 1, // 1-based beat number
      tick: tickWithinBeat,
      measureFraction: `${beatWithinMeasure + 1}/${ticksPerBeat}` // e.g. 2/4 for second beat in 4/4
    };
  }

  // Convert measure, beat, tick to X coordinate
  function measureInfoToX(measure: number, beat: number, tick: number, ticksPerBeat: number) {
    // Convert to 0-based indices
    const measureIndex = measure - 1;
    const beatIndex = beat - 1;

    // Calculate x position
    const measureX = measureIndex * pixelsPerMeasure;
    const beatX = beatIndex * pixelsPerBeat;
    const tickX = (tick / ticksPerBeat) * pixelsPerBeat;

    return measureX + beatX + tickX;
  }

  // Convert Y coordinate to MIDI pitch
  function yToPitch(y: number) {
    const pitchIndex = Math.floor(y / NOTE_HEIGHT);
    const pitch = TOTAL_NOTES - 1 - pitchIndex;

    // Convert MIDI pitch to note name (e.g. C4, F#5)
    const noteName = getMidiNoteName(pitch);

    return { pitch, noteName };
  }

  // Convert MIDI pitch to Y coordinate
  function pitchToY(pitch: number) {
    return (TOTAL_NOTES - 1 - pitch) * NOTE_HEIGHT;
  }

  // Get note name from MIDI pitch
  function getMidiNoteName(pitch: number) {
    const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const noteName = noteNames[pitch % 12];
    const octave = Math.floor(pitch / 12) - 1; // MIDI standard: C4 is 60
    return `${noteName}${octave}`;
  }

  // Update mouse position info
  function updateMousePositionInfo(x: number, y: number) {
    // Get measure, beat, tick info from x coordinate
    const measureInfo = xToMeasureInfo(x);

    // Get pitch info from y coordinate
    const pitchInfo = yToPitch(y);

    // Update current mouse position
    currentMousePosition = {
      x,
      y,
      measure: measureInfo.measure,
      beat: measureInfo.beat,
      tick: measureInfo.tick,
      pitch: pitchInfo.pitch,
      noteName: pitchInfo.noteName
    };

    // Emit position info event for parent components to use
    dispatch('positionInfo', currentMousePosition);
  }

  // Snap value to grid based on selected snap setting with higher precision
  function snapToGrid(value: number) {
    // If snap is set to 'none', return the exact value
    if (snapSetting === 'none') {
      return value;
    }

    try {
      // Use the precise note flicks calculation for better accuracy
      const exactNoteFlicks = getExactNoteFlicks(snapSetting, tempo);
      const exactNotePixels = flicksToPixels(exactNoteFlicks, pixelsPerBeat, tempo);

      // Round to nearest grid position
      return Math.round(value / exactNotePixels) * exactNotePixels;
    } catch (error) {
      // Fallback to original calculation if snap setting is not recognized
      console.warn(`Unknown snap setting: ${snapSetting}, using fallback calculation`);

      // Parse the snap setting fraction
      let divisionValue = 4; // Default to quarter note (1/4)

      if (snapSetting !== 'none') {
        const [numerator, denominator] = snapSetting.split('/');
        if (numerator === '1' && denominator) {
          divisionValue = parseInt(denominator);
        }
      }

      // Calculate grid size based on the snap setting
      const gridSize = pixelsPerBeat / divisionValue;
      return Math.round(value / gridSize) * gridSize;
    }
  }

  // Convert beat position to pixel position
  function beatToPixel(beat: number) {
    return beat * pixelsPerBeat;
  }

  // Draw the grid with notes
  function drawGrid() {
    if (!ctx || !canvas) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background
    ctx.fillStyle = '#2c2c2c';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Calculate visible area
    const startX = horizontalScroll;
    const endX = horizontalScroll + width;
    const startY = verticalScroll;
    const endY = verticalScroll + height;

    // Draw vertical grid lines (beat and measure lines)
    const startMeasure = Math.floor(startX / pixelsPerMeasure);
    const endMeasure = Math.ceil(endX / pixelsPerMeasure);

    for (let measure = startMeasure; measure <= endMeasure; measure++) {
      const measureX = measure * pixelsPerMeasure - horizontalScroll;

      // Draw measure line
      ctx.strokeStyle = MEASURE_COLOR;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(measureX, 0);
      ctx.lineTo(measureX, height);
      ctx.stroke();

      // Draw beat lines within measure
      for (let beat = 1; beat < beatsPerMeasure; beat++) {
        const beatX = measureX + beat * pixelsPerBeat;

        ctx.strokeStyle = BEAT_COLOR;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(beatX, 0);
        ctx.lineTo(beatX, height);
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

        ctx.strokeStyle = GRID_COLOR;
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(divisionX, 0);
        ctx.lineTo(divisionX, height);
        ctx.stroke();
      }
    }

    // Draw horizontal grid lines
    const startRow = Math.floor(startY / GRID_LINE_INTERVAL);
    const endRow = Math.ceil(endY / GRID_LINE_INTERVAL);

    for (let row = startRow; row <= endRow; row++) {
      const rowY = row * GRID_LINE_INTERVAL - verticalScroll;

      // Draw row background for black keys (C#, D#, F#, G#, A#)
      const midiNote = TOTAL_NOTES - 1 - row;
      const noteIndex = midiNote % 12;

      if ([1, 3, 6, 8, 10].includes(noteIndex)) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
        ctx.fillRect(0, rowY, width, GRID_LINE_INTERVAL);
      }

      // Draw grid line
      ctx.strokeStyle = GRID_COLOR;
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(0, rowY);
      ctx.lineTo(width, rowY);
      ctx.stroke();
    }

    // Draw notes
    for (const note of notes) {
      const noteX = note.start - horizontalScroll;
      const noteY = (TOTAL_NOTES - 1 - note.pitch) * NOTE_HEIGHT - verticalScroll;

      // Skip notes outside of visible area
      if (
        noteX + note.duration < 0 ||
        noteX > width ||
        noteY + NOTE_HEIGHT < 0 ||
        noteY > height
      ) {
        continue;
      }

      // Draw note rectangle
      ctx.fillStyle = selectedNotes.has(note.id) ? NOTE_SELECTED_COLOR : NOTE_COLOR;
      ctx.fillRect(noteX, noteY, note.duration, NOTE_HEIGHT);

      // Draw border
      ctx.strokeStyle = '#1a1a1a';
      ctx.lineWidth = 1;
      ctx.strokeRect(noteX, noteY, note.duration, NOTE_HEIGHT);

      // Draw velocity indicator (brightness of note)
      const velocityHeight = (NOTE_HEIGHT - 4) * (note.velocity / 127);
      ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.fillRect(noteX + 2, noteY + 2 + (NOTE_HEIGHT - 4 - velocityHeight), note.duration - 4, velocityHeight);

      // Draw lyric text if present and note is wide enough
      if (note.lyric && note.duration > 20) {
        ctx.fillStyle = LYRIC_COLOR;
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        // Create text that fits within note width
        let text = note.lyric;

        // Add phoneme if available
        if (note.phoneme) {
          text += ` [${note.phoneme}]`;
        }

        const maxWidth = note.duration - 6;
        let textWidth = ctx.measureText(text).width;

        if (textWidth > maxWidth) {
          // Try to fit as much text as possible
          if (note.phoneme && text.length > note.lyric.length) {
            // If phoneme makes it too long, try without phoneme
            text = note.lyric;
            textWidth = ctx.measureText(text).width;

            if (textWidth > maxWidth) {
              text = text.substring(0, Math.floor(text.length * (maxWidth / textWidth))) + '...';
            }
          } else {
            text = text.substring(0, Math.floor(text.length * (maxWidth / textWidth))) + '...';
          }
        }

        ctx.fillText(text, noteX + note.duration / 2, noteY + NOTE_HEIGHT / 2);
      }
    }
  }

  // Calculate the initial scroll position to center A3
  function calculateInitialScrollPosition() {
    // MIDI note number for A3 is 57 (9 semitones above C3 which is 48)
    const A3_MIDI_NOTE = 57;

    // Calculate the position of A3 in the grid
    const A3_INDEX = TOTAL_NOTES - 1 - A3_MIDI_NOTE;
    const A3_POSITION = A3_INDEX * NOTE_HEIGHT;

    // Calculate scroll position to center A3 vertically
    // Subtract half the grid height to center it
    const centeredScrollPosition = Math.max(0, A3_POSITION - (height / 2));

    return centeredScrollPosition;
  }

  // Set up the component
  onMount(() => {
    // Get canvas context
    ctx = canvas.getContext('2d');

    // Set up canvas size
    canvas.width = width;
    canvas.height = height;

    // Set initial scroll position to center C3
    verticalScroll = calculateInitialScrollPosition();

    // Notify parent of scroll position
    dispatch('scroll', { horizontalScroll, verticalScroll });

    // Draw initial grid
    drawGrid();

    // Set initial mouse position info for the center of the viewport
    const centerX = horizontalScroll + width / 2;
    const centerY = verticalScroll + height / 2;
    updateMousePositionInfo(centerX, centerY);

    // Expose coordinate conversion utilities to parent components
    dispatch('utilsReady', {
      xToMeasureInfo,
      measureInfoToX,
      yToPitch,
      pitchToY,
      getMidiNoteName
    });
  });

  // Update when props change
  $: {
    if (ctx && canvas) {
      canvas.width = width;
      canvas.height = height;
      drawGrid();
    }
  }

  // Re-render grid when playhead position changes during playback
  $: if (isPlaying && currentFlicks) {
    drawGrid();
  }

  // Redraw when time signature changes
  $: if (timeSignature && ctx && canvas) {
    // This will reactively update when timeSignature.numerator or denominator changes
    drawGrid();
  }

  // Redraw when snap setting changes
  $: if (snapChanged && ctx && canvas) {
    // This will reactively update when snapSetting changes
    drawGrid();
  }

  // Redraw and scale notes when zoom level (pixelsPerBeat) changes
  $: {
    if (pixelsPerBeat !== previousPixelsPerBeat) {
      // Scale existing notes when zoom level changes
      scaleNotesForZoom();
      previousPixelsPerBeat = pixelsPerBeat;
    }
    drawGrid();
  }

  // Re-render grid when playhead position changes during playback
  $: if (isPlaying && currentFlicks) {
    // This reactive statement will trigger a redraw whenever currentFlicks changes during playback
    drawGrid();
  }

  // Scale the position of notes when the zoom level (pixelsPerBeat) changes
  function scaleNotesForZoom() {
    if (notes.length === 0 || !previousPixelsPerBeat) return;

    const scaleFactor = pixelsPerBeat / previousPixelsPerBeat;

    // Scale the start positions of all notes
    notes = notes.map(note => ({
      ...note,
      // Maintain relative position by scaling the start time
      start: note.start * scaleFactor,
      // Scale the duration proportionally
      duration: note.duration * scaleFactor,
      // Update flicks values to match the new pixel positions
      startFlicks: pixelsToFlicks(note.start * scaleFactor, pixelsPerBeat, tempo),
      durationFlicks: pixelsToFlicks(note.duration * scaleFactor, pixelsPerBeat, tempo)
    }));

    // Notify parent of note changes
    dispatch('noteChange', { notes });
  }
</script>

<div class="grid-container">
  <canvas
    bind:this={canvas}
    width={width}
    height={height}
    on:wheel={handleScroll}
    on:mousedown={handleMouseDown}
    on:mousemove={handleMouseMove}
    on:mouseup={handleMouseUp}
    on:mouseleave={handleMouseUp}
    on:dblclick={handleDoubleClick}
    class="grid-canvas
      {editMode === 'select' ? 'select-mode' : ''}
      {editMode === 'draw' ? 'draw-mode' : ''}
      {editMode === 'erase' ? 'erase-mode' : ''}
      {isNearNoteEdge || isResizing ? (editMode !== 'draw' ? 'resize-possible' : '') : ''}"
  ></canvas>

  {#if isEditingLyric}
    <div
      class="lyric-input-container"
      style="
        left: {lyricInputPosition.x}px;
        top: {lyricInputPosition.y}px;
        width: {lyricInputPosition.width}px;
      "
    >
      <input
        id="lyric-input"
        type="text"
        bind:value={lyricInputValue}
        on:keydown={handleLyricInputKeydown}
        on:blur={saveLyric}
        class="lyric-input"
        aria-label="노트 가사 편집"
      />
    </div>
  {/if}

  <!-- Position info display -->
  <div class="position-info" aria-live="polite">
    <div class="position-measure">Measure: {currentMousePosition.measure}, Beat: {currentMousePosition.beat}, Tick: {currentMousePosition.tick}</div>
    <div class="position-note">Note: {currentMousePosition.noteName} (MIDI: {currentMousePosition.pitch})</div>
  </div>
</div>

<style>
  .grid-container {
    position: relative;
    height: 100%;
  }

  .position-info {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background-color: rgba(0, 0, 0, 0.75);
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-family: 'Roboto Mono', monospace, sans-serif;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    pointer-events: none; /* Allow clicks to pass through */
    z-index: 10;
    transition: opacity 0.2s ease;
  }

  .position-measure {
    margin-bottom: 3px;
    opacity: 0.9;
  }

  .position-note {
    font-weight: 500;
    color: #90caf9;
  }

  .grid-canvas {
    display: block;
    cursor: crosshair; /* Default cursor for generic mode */
  }

  /* Cursor styles based on edit mode and interactions */
  .grid-canvas.select-mode {
    cursor: default; /* Normal cursor for select mode */
  }

  .grid-canvas.draw-mode {
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' stroke='%23000000' stroke-width='0.5' d='M21.1,2.9c-0.8-0.8-2.1-0.8-2.9,0L6.9,15.2l-1.8,5.3l5.3-1.8L22.6,6.5c0.8-0.8,0.8-2.1,0-2.9L21.1,2.9z M6.7,19.3l1-2.9l1.9,1.9L6.7,19.3z'/%3E%3C/svg%3E") 0 24, auto; /* Pencil cursor for draw mode */
  }

  /* Draw mode cursor takes precedence over resize cursor */
  .grid-canvas.draw-mode.resize-possible {
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' stroke='%23000000' stroke-width='0.5' d='M21.1,2.9c-0.8-0.8-2.1-0.8-2.9,0L6.9,15.2l-1.8,5.3l5.3-1.8L22.6,6.5c0.8-0.8,0.8-2.1,0-2.9L21.1,2.9z M6.7,19.3l1-2.9l1.9,1.9L6.7,19.3z'/%3E%3C/svg%3E") 0 24, auto !important; /* Pencil cursor with higher specificity */
  }

  .grid-canvas.erase-mode {
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' stroke='%23000000' stroke-width='0.5' d='M18.3,8.3L15.7,5.7c-0.4-0.4-1-0.4-1.4,0L3.7,16.3c-0.4,0.4-0.4,1,0,1.4l2.6,2.6c0.4,0.4,1,0.4,1.4,0L18.3,9.7C18.7,9.3,18.7,8.7,18.3,8.3z M6.3,18.9L5.1,17.7l9.9-9.9l1.2,1.2L6.3,18.9z'/%3E%3C/svg%3E") 0 24, auto; /* Eraser cursor for erase mode */
  }

  .grid-canvas.resize-possible {
    cursor: ew-resize; /* Left-right resize cursor when hovering over note edges */
  }

  .lyric-input-container {
    position: absolute;
    z-index: 10;
  }

  .lyric-input {
    width: 100%;
    height: 18px;
    background-color: #fff;
    border: 1px solid #1976D2;
    border-radius: 2px;
    font-size: 10px;
    padding: 0 4px;
    color: #333;
    box-sizing: border-box;
  }

  .lyric-input:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.4);
  }
</style>
