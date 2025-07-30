import gradio as gr
import numpy as np
import io
import base64
import wave
import tempfile
import os
from gradio_pianoroll import PianoRoll

# 신디사이저 설정
SAMPLE_RATE = 44100
MAX_DURATION = 10.0  # 최대 10초

# 사용자 정의 phoneme 매핑 (전역 상태)
user_phoneme_map = {}

def initialize_phoneme_map():
    """기본 한국어 phoneme 매핑으로 초기화"""
    global user_phoneme_map
    user_phoneme_map = {
        '가': 'g a',
        '나': 'n a',
        '다': 'd a',
        '라': 'l aa',
        '마': 'm a',
        '바': 'b a',
        '사': 's a',
        '아': 'aa',
        '자': 'j a',
        '차': 'ch a',
        '카': 'k a',
        '타': 't a',
        '파': 'p a',
        '하': 'h a',
        '도': 'd o',
        '레': 'l e',
        '미': 'm i',
        '파': 'p aa',
        '솔': 's o l',
        '라': 'l aa',
        '시': 's i',
        '안녕': 'aa n ny eo ng',
        '하세요': 'h a s e y o',
        '노래': 'n o l ae',
        '사랑': 's a l a ng',
        '행복': 'h ae ng b o k',
        '음악': 'eu m a k',
        '피아노': 'p i a n o'
    }

# 프로그램 시작 시 phoneme 매핑 초기화
initialize_phoneme_map()

def get_phoneme_mapping_list():
    """현재 phoneme 매핑 리스트 반환 (UI 표시용)"""
    global user_phoneme_map
    return [{"lyric": k, "phoneme": v} for k, v in user_phoneme_map.items()]

def get_phoneme_mapping_for_dataframe():
    """Dataframe용 phoneme 매핑 리스트 반환"""
    global user_phoneme_map
    return [[k, v] for k, v in user_phoneme_map.items()]

def add_phoneme_mapping(lyric: str, phoneme: str):
    """새로운 phoneme 매핑 추가"""
    global user_phoneme_map
    user_phoneme_map[lyric.strip()] = phoneme.strip()
    return get_phoneme_mapping_for_dataframe(), f"'{lyric}' → '{phoneme}' 매핑이 추가되었습니다."

def update_phoneme_mapping(old_lyric: str, new_lyric: str, new_phoneme: str):
    """기존 phoneme 매핑 수정"""
    global user_phoneme_map

    # 기존 매핑 삭제
    if old_lyric in user_phoneme_map:
        del user_phoneme_map[old_lyric]

    # 새 매핑 추가
    user_phoneme_map[new_lyric.strip()] = new_phoneme.strip()
    return get_phoneme_mapping_for_dataframe(), f"매핑이 '{new_lyric}' → '{new_phoneme}'로 수정되었습니다."

def delete_phoneme_mapping(lyric: str):
    """phoneme 매핑 삭제"""
    global user_phoneme_map
    if lyric in user_phoneme_map:
        del user_phoneme_map[lyric]
        return get_phoneme_mapping_for_dataframe(), f"'{lyric}' 매핑이 삭제되었습니다."
    else:
        return get_phoneme_mapping_for_dataframe(), f"'{lyric}' 매핑을 찾을 수 없습니다."

def reset_phoneme_mapping():
    """phoneme 매핑을 기본값으로 리셋"""
    initialize_phoneme_map()
    return get_phoneme_mapping_for_dataframe(), "Phoneme 매핑이 기본값으로 리셋되었습니다."

def midi_to_frequency(midi_note):
    """MIDI 노트 번호를 주파수로 변환 (A4 = 440Hz)"""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def create_adsr_envelope(attack, decay, sustain, release, duration, sample_rate):
    """ADSR 엔벨로프를 생성"""
    total_samples = int(duration * sample_rate)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples

    # 지속 구간이 음수가 되지 않도록 조정
    if sustain_samples < 0:
        sustain_samples = 0
        total_samples = attack_samples + decay_samples + release_samples

    envelope = np.zeros(total_samples)

    # Attack phase
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay phase
    if decay_samples > 0:
        start_idx = attack_samples
        end_idx = attack_samples + decay_samples
        envelope[start_idx:end_idx] = np.linspace(1, sustain, decay_samples)

    # Sustain phase
    if sustain_samples > 0:
        start_idx = attack_samples + decay_samples
        end_idx = start_idx + sustain_samples
        envelope[start_idx:end_idx] = sustain

    # Release phase
    if release_samples > 0:
        start_idx = attack_samples + decay_samples + sustain_samples
        envelope[start_idx:] = np.linspace(sustain, 0, release_samples)

    return envelope

def generate_sine_wave(frequency, duration, sample_rate):
    """사인파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sin(2 * np.pi * frequency * t)

def generate_sawtooth_wave(frequency, duration, sample_rate):
    """톱니파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    # 2 * (t * frequency - np.floor(0.5 + t * frequency))
    return 2 * (t * frequency % 1) - 1

def generate_square_wave(frequency, duration, sample_rate):
    """사각파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sign(np.sin(2 * np.pi * frequency * t))

def generate_triangle_wave(frequency, duration, sample_rate):
    """삼각파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return 2 * np.abs(2 * (t * frequency % 1) - 1) - 1

def generate_harmonic_wave(frequency, duration, sample_rate, harmonics=5):
    """하모닉을 포함한 복합 파형 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    wave = np.zeros_like(t)

    # 기본 주파수
    wave += np.sin(2 * np.pi * frequency * t)

    # 하모닉 추가 (각 하모닉의 진폭은 1/n로 감소)
    for n in range(2, harmonics + 1):
        amplitude = 1.0 / n
        wave += amplitude * np.sin(2 * np.pi * frequency * n * t)

    # 정규화
    wave = wave / np.max(np.abs(wave))
    return wave

def generate_fm_wave(frequency, duration, sample_rate, mod_freq=5.0, mod_depth=2.0):
    """FM 합성 파형 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)

    # Modulator
    modulator = mod_depth * np.sin(2 * np.pi * mod_freq * t)

    # Carrier with frequency modulation
    carrier = np.sin(2 * np.pi * frequency * t + modulator)

    return carrier

def generate_complex_wave(frequency, duration, sample_rate, wave_type='complex'):
    """복합적인 파형 생성 (여러 기법 조합)"""
    if wave_type == 'sine':
        return generate_sine_wave(frequency, duration, sample_rate)
    elif wave_type == 'sawtooth':
        return generate_sawtooth_wave(frequency, duration, sample_rate)
    elif wave_type == 'square':
        return generate_square_wave(frequency, duration, sample_rate)
    elif wave_type == 'triangle':
        return generate_triangle_wave(frequency, duration, sample_rate)
    elif wave_type == 'harmonic':
        return generate_harmonic_wave(frequency, duration, sample_rate, harmonics=7)
    elif wave_type == 'fm':
        return generate_fm_wave(frequency, duration, sample_rate, mod_freq=frequency * 0.1, mod_depth=3.0)
    else:  # 'complex' - 여러 파형 조합
        # 기본 sawtooth + 하모닉 + 약간의 FM
        base = generate_sawtooth_wave(frequency, duration, sample_rate) * 0.6
        harmonic = generate_harmonic_wave(frequency, duration, sample_rate, harmonics=4) * 0.3
        fm = generate_fm_wave(frequency, duration, sample_rate, mod_freq=frequency * 0.05, mod_depth=1.0) * 0.1

        return base + harmonic + fm

def synthesize_audio(piano_roll_data, attack=0.01, decay=0.1, sustain=0.7, release=0.3, wave_type='complex'):
    """피아노롤 데이터로부터 오디오를 합성"""
    if not piano_roll_data or 'notes' not in piano_roll_data or not piano_roll_data['notes']:
        return None

    notes = piano_roll_data['notes']
    tempo = piano_roll_data.get('tempo', 120)
    pixels_per_beat = piano_roll_data.get('pixelsPerBeat', 80)

    # 전체 길이 계산 (마지막 노트의 끝까지)
    max_end_time = 0
    for note in notes:
        # 픽셀을 초로 변환 (템포와 픽셀당 비트 수 고려)
        start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
        duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)
        end_time = start_seconds + duration_seconds
        max_end_time = max(max_end_time, end_time)

    # 최대 길이 제한
    total_duration = min(max_end_time + 1.0, MAX_DURATION)  # 1초 여유 추가
    total_samples = int(total_duration * SAMPLE_RATE)

    # 최종 오디오 버퍼
    audio_buffer = np.zeros(total_samples)

    # 각 노트 처리
    for i, note in enumerate(notes):
        try:
            # 노트 속성
            pitch = note['pitch']
            velocity = note.get('velocity', 100)

            # 시간 계산
            start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
            duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)

            # 범위 체크
            if start_seconds >= total_duration:
                continue

            # 지속 시간이 전체 길이를 초과하지 않도록 조정
            if start_seconds + duration_seconds > total_duration:
                duration_seconds = total_duration - start_seconds

            if duration_seconds <= 0:
                continue

            # 주파수 계산
            frequency = midi_to_frequency(pitch)

            # 볼륨 계산 (velocity를 0-1로 정규화)
            volume = velocity / 127.0

            # 모든 노트에 동일한 파형 타입 사용 (일관성 유지)
            # 복합 파형 생성
            base_wave = generate_complex_wave(frequency, duration_seconds, SAMPLE_RATE, wave_type)

            # 추가 효과: 비브라토 (주파수 변조)
            t = np.linspace(0, duration_seconds, len(base_wave), False)
            vibrato_freq = 4.5  # 4.5Hz 비브라토
            vibrato_depth = 0.02  # 2% 주파수 변조
            vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t)

            # 비브라토를 파형에 적용 (간단한 근사)
            vibrato_wave = base_wave * vibrato

            # 추가 효과: 트레몰로 (진폭 변조)
            tremolo_freq = 3.0  # 3Hz 트레몰로
            tremolo_depth = 0.1  # 10% 진폭 변조
            tremolo = 1 + tremolo_depth * np.sin(2 * np.pi * tremolo_freq * t)

            # 트레몰로 적용
            final_wave = vibrato_wave * tremolo

            # ADSR 엔벨로프 적용
            envelope = create_adsr_envelope(attack, decay, sustain, release, duration_seconds, SAMPLE_RATE)

            # 엔벨로프와 파형 길이 맞춤
            min_length = min(len(final_wave), len(envelope))
            note_audio = final_wave[:min_length] * envelope[:min_length] * volume * 0.25  # 볼륨 조절

            # 오디오 버퍼에 추가
            start_sample = int(start_seconds * SAMPLE_RATE)
            end_sample = start_sample + len(note_audio)

            # 버퍼 범위 내에서만 추가
            if start_sample < total_samples:
                end_sample = min(end_sample, total_samples)
                audio_length = end_sample - start_sample
                if audio_length > 0:
                    audio_buffer[start_sample:end_sample] += note_audio[:audio_length]

        except Exception as e:
            print(f"노트 처리 중 오류: {e}")
            continue

    # 클리핑 방지 (normalize)
    max_amplitude = np.max(np.abs(audio_buffer))
    if max_amplitude > 0:
        audio_buffer = audio_buffer / max_amplitude * 0.9  # 90%로 제한

    return audio_buffer

def audio_to_base64_wav(audio_data, sample_rate):
    """오디오 데이터를 base64 인코딩된 WAV로 변환"""
    if audio_data is None or len(audio_data) == 0:
        return None

    # 16비트 PCM으로 변환
    audio_16bit = (audio_data * 32767).astype(np.int16)

    # WAV 파일을 메모리에 생성
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # 모노
        wav_file.setsampwidth(2)  # 16비트
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_16bit.tobytes())

    # base64 인코딩
    buffer.seek(0)
    wav_data = buffer.read()
    base64_data = base64.b64encode(wav_data).decode('utf-8')

    return f"data:audio/wav;base64,{base64_data}"

def calculate_waveform_data(audio_data, pixels_per_beat, tempo, target_width=1000):
    """오디오 데이터로부터 웨이브폼 시각화 데이터를 계산"""
    if audio_data is None or len(audio_data) == 0:
        return None

    # 오디오 총 길이 (초)
    audio_duration = len(audio_data) / SAMPLE_RATE

    # 총 픽셀 길이 계산 (템포와 픽셀당 비트 기반)
    total_pixels = (tempo / 60) * pixels_per_beat * audio_duration

    # 각 픽셀당 샘플 수 계산
    samples_per_pixel = len(audio_data) / total_pixels

    waveform_points = []

    # 각 픽셀에 대해 min/max 값 계산
    for pixel in range(int(total_pixels)):
        start_sample = int(pixel * samples_per_pixel)
        end_sample = int((pixel + 1) * samples_per_pixel)
        end_sample = min(end_sample, len(audio_data))

        if start_sample >= len(audio_data):
            break

        if start_sample < end_sample:
            # 해당 픽셀 범위의 오디오 데이터
            pixel_data = audio_data[start_sample:end_sample]

            # min, max 값 계산
            min_val = float(np.min(pixel_data))
            max_val = float(np.max(pixel_data))

            # 시간 정보 (픽셀 위치)
            time_position = pixel

            waveform_points.append({
                'x': time_position,
                'min': min_val,
                'max': max_val
            })

    return waveform_points

def convert_basic(piano_roll):
    """기본 변환 함수 (첫 번째 탭용)"""
    print("=== Basic Convert function called ===")
    print("Received piano_roll:")
    print(piano_roll)
    print("Type:", type(piano_roll))
    return piano_roll

def synthesize_and_play(piano_roll, attack, decay, sustain, release, wave_type='complex'):
    """신디사이저로 오디오를 생성하고 피아노롤에 전달"""
    print("=== Synthesize function called ===")
    print("Piano roll data:", piano_roll)
    print(f"ADSR: A={attack}, D={decay}, S={sustain}, R={release}")
    print(f"Wave Type: {wave_type}")

    # 오디오 합성
    audio_data = synthesize_audio(piano_roll, attack, decay, sustain, release, wave_type)

    if audio_data is None:
        print("오디오 생성 실패")
        return piano_roll, "오디오 생성 실패", None

    # base64로 변환 (피아노롤용)
    audio_base64 = audio_to_base64_wav(audio_data, SAMPLE_RATE)

    # gradio Audio 컴포넌트용 WAV 파일 생성
    gradio_audio_path = create_temp_wav_file(audio_data, SAMPLE_RATE)

    # 피아노롤 데이터에 오디오 추가
    updated_piano_roll = piano_roll.copy() if piano_roll else {}
    updated_piano_roll['audio_data'] = audio_base64
    updated_piano_roll['use_backend_audio'] = True

    print(f"🔊 [synthesize_and_play] Setting backend audio data:")
    print(f"   - audio_data length: {len(audio_base64) if audio_base64 else 0}")
    print(f"   - use_backend_audio: {updated_piano_roll['use_backend_audio']}")
    print(f"   - audio_base64 preview: {audio_base64[:50] + '...' if audio_base64 else 'None'}")

    # 웨이브폼 데이터 계산
    pixels_per_beat = updated_piano_roll.get('pixelsPerBeat', 80)
    tempo = updated_piano_roll.get('tempo', 120)
    waveform_data = calculate_waveform_data(audio_data, pixels_per_beat, tempo)

    # 곡선 데이터 예시 (피치 곡선 + 웨이브폼 데이터)
    curve_data = {}

    # 웨이브폼 데이터 추가
    if waveform_data:
        curve_data['waveform_data'] = waveform_data
        print(f"웨이브폼 데이터 생성: {len(waveform_data)} 포인트")

    # 피치 곡선 데이터 (기존)
    if 'notes' in updated_piano_roll and updated_piano_roll['notes']:
        pitch_curve = []
        for note in updated_piano_roll['notes']:
            # 간단한 예시: 노트의 피치를 기반으로 곡선 생성
            base_pitch = note['pitch']
            # 약간의 비브라토 효과
            curve_points = [base_pitch + 0.5 * np.sin(i * 0.5) for i in range(10)]
            pitch_curve.extend(curve_points)

        curve_data['pitch_curve'] = pitch_curve[:100]  # 최대 100개 포인트로 제한

    updated_piano_roll['curve_data'] = curve_data

    # 세그먼트 데이터 예시 (발음 타이밍)
    if 'notes' in updated_piano_roll and updated_piano_roll['notes']:
        segment_data = []

        for i, note in enumerate(updated_piano_roll['notes']):
            start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
            duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)

            segment_data.append({
                'start': start_seconds,
                'end': start_seconds + duration_seconds,
                'type': 'note',
                'value': note.get('lyric', f"Note_{i+1}"),
                'confidence': 0.95
            })

        updated_piano_roll['segment_data'] = segment_data

    print(f"오디오 생성 완료: {len(audio_data)} 샘플")
    if waveform_data:
        print(f"웨이브폼 포인트: {len(waveform_data)}개")

    status_message = f"오디오 생성 완료 ({wave_type} 파형): {len(audio_data)} 샘플, 길이: {len(audio_data)/SAMPLE_RATE:.2f}초"

    return updated_piano_roll, status_message, gradio_audio_path

def create_temp_wav_file(audio_data, sample_rate):
    """gradio Audio 컴포넌트용 임시 WAV 파일 생성"""
    if audio_data is None or len(audio_data) == 0:
        return None

    try:
        # 16비트 PCM으로 변환
        audio_16bit = (audio_data * 32767).astype(np.int16)

        # 임시 파일 생성
        temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')

        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 모노
            wav_file.setsampwidth(2)  # 16비트
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_16bit.tobytes())

        # 파일 디스크립터 닫기
        os.close(temp_fd)

        return temp_path
    except Exception as e:
        print(f"임시 WAV 파일 생성 오류: {e}")
        return None

def clear_and_regenerate_waveform(piano_roll, attack, decay, sustain, release, wave_type='complex'):
    """웨이브폼을 지우고 다시 생성"""
    print("=== Clear and Regenerate Waveform ===")

    # 먼저 웨이브폼 데이터를 지움
    cleared_piano_roll = piano_roll.copy() if piano_roll else {}
    cleared_piano_roll['curve_data'] = {}  # 곡선 데이터 초기화
    cleared_piano_roll['audio_data'] = None  # 오디오 데이터 초기화
    cleared_piano_roll['use_backend_audio'] = False  # 백엔드 오디오 비활성화

    # 잠시 대기를 위한 메시지
    yield cleared_piano_roll, "웨이브폼을 지우는 중...", None

    # 그 다음 새로운 웨이브폼 생성
    result_piano_roll, status_message, gradio_audio_path = synthesize_and_play(piano_roll, attack, decay, sustain, release, wave_type)

    yield result_piano_roll, f"재생성 완료! {status_message}", gradio_audio_path

# G2P (Grapheme-to-Phoneme) 함수 (사용자 정의 매핑 사용)
def mock_g2p(text: str) -> str:
    """
    사용자 정의 매핑을 사용하는 한국어 G2P 함수
    """
    global user_phoneme_map

    # 텍스트를 소문자로 변환하고 공백 제거
    text = text.strip()

    # 사용자 정의 매핑에서 찾기
    if text in user_phoneme_map:
        return user_phoneme_map[text]

    # 매핑에 없으면 글자별로 처리
    result = []
    for char in text:
        if char in user_phoneme_map:
            result.append(user_phoneme_map[char])
        else:
            # 알 수 없는 글자는 그대로 반환
            result.append(char)

    return ' '.join(result)

def process_lyric_input(piano_roll, lyric_data):
    """
    가사 입력 이벤트를 처리하고 G2P를 실행하여 phoneme을 생성
    """
    print("=== G2P Processing ===")
    print("Piano roll data:", piano_roll)
    print("Lyric data:", lyric_data)

    if not piano_roll or not lyric_data:
        return piano_roll, "가사 데이터가 없습니다."

    # 새로운 가사에 대해 G2P 실행
    new_lyric = lyric_data.get('newLyric', '')
    if new_lyric:
        # G2P 실행 (모킹 함수 사용)
        phoneme = mock_g2p(new_lyric)
        print(f"G2P 결과: '{new_lyric}' -> '{phoneme}'")

        # 해당 노트의 phoneme 업데이트
        note_id = lyric_data.get('noteId')
        if note_id and 'notes' in piano_roll:
            notes = piano_roll['notes'].copy()
            for note in notes:
                if note.get('id') == note_id:
                    note['phoneme'] = phoneme
                    print(f"노트 {note_id}의 phoneme 업데이트: {phoneme}")
                    break

            # 업데이트된 피아노롤 데이터 반환
            updated_piano_roll = piano_roll.copy()
            updated_piano_roll['notes'] = notes

            return updated_piano_roll, f"G2P 완료: '{new_lyric}' -> [{phoneme}]"

    return piano_roll, "G2P 처리 완료"

def manual_phoneme_update(piano_roll, note_index, phoneme_text):
    """
    수동으로 특정 노트의 phoneme을 업데이트
    """
    print(f"=== Manual Phoneme Update ===")
    print(f"Note index: {note_index}, Phoneme: '{phoneme_text}'")

    if not piano_roll or 'notes' not in piano_roll:
        return piano_roll, "피아노롤 데이터가 없습니다."

    notes = piano_roll['notes'].copy()

    if 0 <= note_index < len(notes):
        notes[note_index]['phoneme'] = phoneme_text

        updated_piano_roll = piano_roll.copy()
        updated_piano_roll['notes'] = notes

        lyric = notes[note_index].get('lyric', '?')
        return updated_piano_roll, f"노트 {note_index + 1} ('{lyric}')의 phoneme을 '{phoneme_text}'로 설정했습니다."
    else:
        return piano_roll, f"잘못된 노트 인덱스: {note_index}"

def clear_all_phonemes(piano_roll):
    """
    모든 노트의 phoneme을 지우기
    """
    print("=== Clear All Phonemes ===")

    if not piano_roll or 'notes' not in piano_roll:
        return piano_roll, "피아노롤 데이터가 없습니다."

    notes = piano_roll['notes'].copy()

    for note in notes:
        note['phoneme'] = None

    updated_piano_roll = piano_roll.copy()
    updated_piano_roll['notes'] = notes

    return updated_piano_roll, "모든 phoneme이 지워졌습니다."

def auto_generate_all_phonemes(piano_roll):
    """
    모든 노트의 가사에 대해 자동으로 phoneme 생성
    """
    print("=== Auto Generate All Phonemes ===")

    if not piano_roll or 'notes' not in piano_roll:
        return piano_roll, "피아노롤 데이터가 없습니다."

    notes = piano_roll['notes'].copy()

    updated_count = 0
    for note in notes:
        lyric = note.get('lyric')
        if lyric:
            phoneme = mock_g2p(lyric)
            note['phoneme'] = phoneme
            updated_count += 1
            print(f"자동 생성: '{lyric}' -> '{phoneme}'")

    updated_piano_roll = piano_roll.copy()
    updated_piano_roll['notes'] = notes

    return updated_piano_roll, f"{updated_count}개 노트의 phoneme이 자동 생성되었습니다."

# Gradio 인터페이스
with gr.Blocks(title="PianoRoll with Synthesizer Demo") as demo:
    gr.Markdown("# 🎹 Gradio PianoRoll with Synthesizer")
    gr.Markdown("피아노롤 컴포넌트와 신디사이저 기능을 테스트해보세요!")

    with gr.Tabs():
        # 첫 번째 탭: 기본 데모
        with gr.TabItem("🎼 Basic Demo"):
            gr.Markdown("## 기본 피아노롤 데모")

            with gr.Row():
                with gr.Column():
                    # 초기값 설정
                    initial_value_basic = {
                        "notes": [
                            {
                                "start": 80,
                                "duration": 80,
                                "pitch": 60,
                                "velocity": 100,
                                "lyric": "안녕"
                            },
                            {
                                "start": 160,
                                "duration": 160,
                                "pitch": 64,
                                "velocity": 90,
                                "lyric": "하세요"
                            }
                        ],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4"
                    }
                    piano_roll_basic = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_basic,
                        elem_id="piano_roll_basic",  # 고유 ID 부여
                        use_backend_audio=False  # 프론트엔드 오디오 엔진 사용
                    )

            with gr.Row():
                with gr.Column():
                    output_json_basic = gr.JSON()

            with gr.Row():
                with gr.Column():
                    btn_basic = gr.Button("🔄 Convert & Debug", variant="primary")

            # 기본 탭 이벤트
            btn_basic.click(
                fn=convert_basic,
                inputs=piano_roll_basic,
                outputs=output_json_basic,
                show_progress=True
            )

        # 두 번째 탭: 신디사이저 데모
        with gr.TabItem("🎵 Synthesizer Demo"):
            gr.Markdown("## 신디사이저가 포함된 피아노롤 데모")
            gr.Markdown("노트를 편집한 후 '🎶 Synthesize Audio' 버튼을 클릭하면 오디오가 생성되어 재생됩니다!")

            with gr.Row():
                with gr.Column(scale=3):
                    # 신디사이저용 초기값
                    initial_value_synth = {
                        "notes": [
                            {
                                "start": 0,
                                "duration": 160,
                                "pitch": 60,  # C4
                                "velocity": 100,
                                "lyric": "도"
                            },
                            {
                                "start": 160,
                                "duration": 160,
                                "pitch": 62,  # D4
                                "velocity": 100,
                                "lyric": "레"
                            },
                            {
                                "start": 320,
                                "duration": 160,
                                "pitch": 64,  # E4
                                "velocity": 100,
                                "lyric": "미"
                            },
                            {
                                "start": 480,
                                "duration": 160,
                                "pitch": 65,  # F4
                                "velocity": 100,
                                "lyric": "파"
                            }
                        ],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4",
                        "curve_data": {},  # 초기에는 빈 곡선 데이터
                        "use_backend_audio": False  # 초기에는 백엔드 오디오 비활성화
                    }
                    piano_roll_synth = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_synth,
                        elem_id="piano_roll_synth",  # 고유 ID 부여
                        use_backend_audio=False  # 초기에는 프론트엔드 엔진 사용, synthesize 시 백엔드로 전환
                    )

                with gr.Column(scale=1):
                    gr.Markdown("### 🎛️ ADSR 설정")
                    attack_slider = gr.Slider(
                        minimum=0.001,
                        maximum=1.0,
                        value=0.01,
                        step=0.001,
                        label="Attack (초)"
                    )
                    decay_slider = gr.Slider(
                        minimum=0.001,
                        maximum=1.0,
                        value=0.1,
                        step=0.001,
                        label="Decay (초)"
                    )
                    sustain_slider = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.7,
                        step=0.01,
                        label="Sustain (레벨)"
                    )
                    release_slider = gr.Slider(
                        minimum=0.001,
                        maximum=2.0,
                        value=0.3,
                        step=0.001,
                        label="Release (초)"
                    )

                    gr.Markdown("### 🎵 파형 설정")
                    wave_type_dropdown = gr.Dropdown(
                        choices=[
                            ("복합 파형 (Complex)", "complex"),
                            ("하모닉 합성 (Harmonic)", "harmonic"),
                            ("FM 합성 (FM)", "fm"),
                            ("톱니파 (Sawtooth)", "sawtooth"),
                            ("사각파 (Square)", "square"),
                            ("삼각파 (Triangle)", "triangle"),
                            ("사인파 (Sine)", "sine")
                        ],
                        value="complex",
                        label="파형 타입",
                        info="각 노트는 순환적으로 다른 파형을 사용합니다"
                    )

            with gr.Row():
                with gr.Column():
                    btn_synthesize = gr.Button("🎶 Synthesize Audio", variant="primary", size="lg")
                    status_text = gr.Textbox(label="상태", interactive=False)

            with gr.Row():
                with gr.Column():
                    btn_regenerate = gr.Button("🔄 웨이브폼 재생성", variant="secondary", size="lg")

            # 비교용 gradio Audio 컴포넌트 추가
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🔊 비교용 Gradio Audio 재생")
                    gradio_audio_output = gr.Audio(
                        label="백엔드에서 생성된 오디오 (비교용)",
                        type="filepath",
                        interactive=False
                    )

            with gr.Row():
                with gr.Column():
                    output_json_synth = gr.JSON(label="결과 데이터")

            # 신디사이저 탭 이벤트
            btn_synthesize.click(
                fn=synthesize_and_play,
                inputs=[
                    piano_roll_synth,
                    attack_slider,
                    decay_slider,
                    sustain_slider,
                    release_slider,
                    wave_type_dropdown
                ],
                outputs=[piano_roll_synth, status_text, gradio_audio_output],
                show_progress=True
            )

            # 웨이브폼 재생성 버튼 이벤트
            btn_regenerate.click(
                fn=clear_and_regenerate_waveform,
                inputs=[
                    piano_roll_synth,
                    attack_slider,
                    decay_slider,
                    sustain_slider,
                    release_slider,
                    wave_type_dropdown
                ],
                outputs=[piano_roll_synth, status_text, gradio_audio_output],
                show_progress=True
            )

            # 이벤트 리스너 설정
            def log_play_event(event_data=None):
                print("🎵 Play event triggered:", event_data)
                return f"재생 시작됨: {event_data if event_data else '재생 중'}"

            def log_pause_event(event_data=None):
                print("⏸️ Pause event triggered:", event_data)
                return f"일시정지됨: {event_data if event_data else '일시정지'}"

            def log_stop_event(event_data=None):
                print("⏹️ Stop event triggered:", event_data)
                return f"정지됨: {event_data if event_data else '정지'}"

            piano_roll_synth.play(log_play_event, outputs=status_text)
            piano_roll_synth.pause(log_pause_event, outputs=status_text)
            piano_roll_synth.stop(log_stop_event, outputs=status_text)

            # input 이벤트 처리 추가 (G2P 처리)
            def handle_synth_input(lyric_data):
                print("🎵 Synthesizer tab - Input event triggered:", lyric_data)
                return f"가사 입력 감지: {lyric_data if lyric_data else '입력됨'}"

            piano_roll_synth.input(handle_synth_input, outputs=status_text)

            # 노트 변경 시 JSON 출력 업데이트
            piano_roll_synth.change(lambda x: x, inputs=piano_roll_synth, outputs=output_json_synth)

        # 세 번째 탭: Phoneme 데모
        with gr.TabItem("🗣️ Phoneme Demo"):
            gr.Markdown("## 📢 음소(Phoneme) 기능 데모")
            gr.Markdown("가사를 수정하면 자동으로 G2P(Grapheme-to-Phoneme)가 실행되어 음소가 표시됩니다. 또한 수동으로 음소를 편집할 수도 있습니다.")

            with gr.Row():
                with gr.Column(scale=3):
                    # Phoneme용 초기값
                    initial_value_phoneme = {
                        "notes": [
                            {
                                "id": "note_0",
                                "start": 0,
                                "duration": 160,
                                "pitch": 60,  # C4
                                "velocity": 100,
                                "lyric": "안녕",
                                "phoneme": "aa n ny eo ng"  # 미리 설정된 음소
                            },
                            {
                                "id": "note_1",
                                "start": 160,
                                "duration": 160,
                                "pitch": 62,  # D4
                                "velocity": 100,
                                "lyric": "하세요",
                                "phoneme": "h a s e y o"
                            },
                            {
                                "id": "note_2",
                                "start": 320,
                                "duration": 160,
                                "pitch": 64,  # E4
                                "velocity": 100,
                                "lyric": "음악",
                                "phoneme": "eu m a k"
                            },
                            {
                                "id": "note_3",
                                "start": 480,
                                "duration": 160,
                                "pitch": 65,  # F4
                                "velocity": 100,
                                "lyric": "피아노"
                            }
                        ],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4"
                    }
                    piano_roll_phoneme = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_phoneme,
                        elem_id="piano_roll_phoneme",  # 고유 ID 부여
                        use_backend_audio=False  # 프론트엔드 오디오 엔진 사용
                    )

                with gr.Column(scale=1):
                    gr.Markdown("### 📝 Phoneme 매핑 관리")

                    # 현재 매핑 리스트 표시
                    phoneme_mapping_dataframe = gr.Dataframe(
                        headers=["가사", "Phoneme"],
                        datatype=["str", "str"],
                        value=get_phoneme_mapping_for_dataframe(),
                        label="현재 Phoneme 매핑",
                        interactive=True,
                        wrap=True
                    )

                    gr.Markdown("#### ➕ 새 매핑 추가")
                    with gr.Row():
                        add_lyric_input = gr.Textbox(
                            label="가사",
                            placeholder="예: 라",
                            scale=1
                        )
                        add_phoneme_input = gr.Textbox(
                            label="Phoneme",
                            placeholder="예: l aa",
                            scale=1
                        )
                    btn_add_mapping = gr.Button("➕ 매핑 추가", variant="primary", size="sm")

                    gr.Markdown("### 🔧 일괄 작업")
                    with gr.Row():
                        btn_auto_generate = gr.Button("🤖 모든 Phoneme 자동 생성", variant="primary")
                        btn_clear_phonemes = gr.Button("🗑️ 모든 Phoneme 지우기", variant="secondary")

                    btn_reset_mapping = gr.Button("🔄 매핑 기본값으로 리셋", variant="secondary")

            with gr.Row():
                with gr.Column():
                    phoneme_status_text = gr.Textbox(label="상태", interactive=False)

            with gr.Row():
                with gr.Column():
                    output_json_phoneme = gr.JSON(label="Phoneme 데이터")

            # Phoneme 탭 이벤트 처리

            # 매핑 추가
            btn_add_mapping.click(
                fn=add_phoneme_mapping,
                inputs=[add_lyric_input, add_phoneme_input],
                outputs=[phoneme_mapping_dataframe, phoneme_status_text],
                show_progress=False
            ).then(
                fn=lambda: ["", ""],  # 입력 필드 초기화
                outputs=[add_lyric_input, add_phoneme_input]
            )

            # 매핑 리셋
            btn_reset_mapping.click(
                fn=reset_phoneme_mapping,
                outputs=[phoneme_mapping_dataframe, phoneme_status_text],
                show_progress=False
            )

            # 가사 입력 시 자동 G2P 처리
            def handle_phoneme_input_event(piano_roll_data):
                """가사 입력 이벤트 처리 - 피아노롤 변경사항을 감지하여 phoneme 생성"""
                print("🗣️ Phoneme tab - Input event triggered")
                print(f"   - Piano roll data: {type(piano_roll_data)}")

                if not piano_roll_data or 'notes' not in piano_roll_data:
                    return piano_roll_data, "피아노롤 데이터가 없습니다."

                return auto_generate_missing_phonemes(piano_roll_data)

            def auto_generate_missing_phonemes(piano_roll_data):
                """가사가 있지만 phoneme이 없는 노트들에 대해 자동으로 phoneme 생성"""
                if not piano_roll_data or 'notes' not in piano_roll_data:
                    return piano_roll_data, "피아노롤 데이터가 없습니다."

                # 현재 notes를 복사
                notes = piano_roll_data['notes'].copy()
                updated_notes = []
                changes_made = 0

                for note in notes:
                    note_copy = note.copy()

                    # 가사가 있는 경우 처리
                    lyric = note.get('lyric', '').strip()
                    current_phoneme = note.get('phoneme', '').strip()

                    if lyric:
                        # G2P 실행하여 새로운 phoneme 생성
                        new_phoneme = mock_g2p(lyric)

                        # 기존 phoneme과 다르거나 없으면 업데이트
                        if not current_phoneme or current_phoneme != new_phoneme:
                            note_copy['phoneme'] = new_phoneme
                            changes_made += 1
                            print(f"   - G2P 적용: '{lyric}' -> '{new_phoneme}'")
                    else:
                        # 가사가 없으면 phoneme도 제거
                        if current_phoneme:
                            note_copy['phoneme'] = None
                            changes_made += 1
                            print(f"   - Phoneme 제거 (가사 없음)")

                    updated_notes.append(note_copy)

                if changes_made > 0:
                    # 업데이트된 피아노롤 데이터 반환
                    updated_piano_roll = piano_roll_data.copy()
                    updated_piano_roll['notes'] = updated_notes
                    return updated_piano_roll, f"자동 G2P 완료: {changes_made}개 노트 업데이트"
                else:
                    return piano_roll_data, "G2P 적용할 변경사항이 없습니다."

            piano_roll_phoneme.input(
                fn=handle_phoneme_input_event,
                inputs=[piano_roll_phoneme],
                outputs=[piano_roll_phoneme, phoneme_status_text],
                show_progress=False
            )

            # 노트 변경 시에도 자동 phoneme 생성
            def handle_phoneme_change_event(piano_roll_data):
                """피아노롤 변경 시 자동 phoneme 처리"""
                return auto_generate_missing_phonemes(piano_roll_data)

            piano_roll_phoneme.change(
                fn=handle_phoneme_change_event,
                inputs=[piano_roll_phoneme],
                outputs=[piano_roll_phoneme, phoneme_status_text],
                show_progress=False
            )

            # 자동 phoneme 생성 (수동 버튼)
            btn_auto_generate.click(
                fn=auto_generate_all_phonemes,
                inputs=[piano_roll_phoneme],
                outputs=[piano_roll_phoneme, phoneme_status_text],
                show_progress=True
            )

            # 모든 phoneme 지우기
            btn_clear_phonemes.click(
                fn=clear_all_phonemes,
                inputs=[piano_roll_phoneme],
                outputs=[piano_roll_phoneme, phoneme_status_text],
                show_progress=False
            )

            # 노트 변경 시 JSON 출력 업데이트 (자동 phoneme 처리와 별도로)
            def update_json_output(piano_roll_data):
                return piano_roll_data

            piano_roll_phoneme.change(
                fn=update_json_output,
                inputs=[piano_roll_phoneme],
                outputs=[output_json_phoneme],
                show_progress=False
            )

            # 재생 이벤트 로깅
            def log_phoneme_play_event(event_data=None):
                print("🗣️ Phoneme Play event triggered:", event_data)
                return f"재생 시작: {event_data if event_data else '재생 중'}"

            def log_phoneme_pause_event(event_data=None):
                print("🗣️ Phoneme Pause event triggered:", event_data)
                return f"일시정지: {event_data if event_data else '일시정지'}"

            def log_phoneme_stop_event(event_data=None):
                print("🗣️ Phoneme Stop event triggered:", event_data)
                return f"정지: {event_data if event_data else '정지'}"

            piano_roll_phoneme.play(log_phoneme_play_event, outputs=phoneme_status_text)
            piano_roll_phoneme.pause(log_phoneme_pause_event, outputs=phoneme_status_text)
            piano_roll_phoneme.stop(log_phoneme_stop_event, outputs=phoneme_status_text)

if __name__ == "__main__":
    demo.launch()
