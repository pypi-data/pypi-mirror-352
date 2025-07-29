<script lang="ts">
	import { JsonView } from "@zerodevx/svelte-json-view";

	import type { Gradio } from "@gradio/utils";
	import { Block, Info } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import type { SelectData } from "@gradio/utils";

	import PianoRoll from "./components/PianoRoll.svelte";

	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;

	export let value = {
		notes: [],
		tempo: 120,
		timeSignature: { numerator: 4, denominator: 4 },
		editMode: 'select',
		snapSetting: '1/4',
		pixelsPerBeat: 80,
		sampleRate: 44100,
		ppqn: 480
	};
	export let container = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus;
	export let gradio: Gradio<{
		change: never;
		input: never;  // 가사 수정 시 발생 (G2P 실행용)
		play: never;   // 재생 버튼 클릭 시
		pause: never;  // 일시정지 버튼 클릭 시
		stop: never;   // 정지 버튼 클릭 시
		clear: never;  // 지우기 버튼 클릭 시
		select: SelectData;
		clear_status: LoadingStatus;
	}>;

	// 백엔드 데이터 속성들
	export let audio_data: string | null = null;
	export let curve_data: object | null = null;
	export let segment_data: Array<any> | null = null;
	export let use_backend_audio: boolean = false;

	export let width = 800;
	export let height = 400;

	// value가 초기화되지 않았거나 필수 속성이 누락된 경우 기본값 설정
	$: if (!value || typeof value !== 'object') {
		value = {
			notes: [],
			tempo: 120,
			timeSignature: { numerator: 4, denominator: 4 },
			editMode: 'select',
			snapSetting: '1/4',
			pixelsPerBeat: 80,
			sampleRate: 44100,
			ppqn: 480
		};
	} else {
		// 개별 속성이 없는 경우에만 기본값 설정
		if (!value.notes) value.notes = [];
		if (!value.tempo) value.tempo = 120;
		if (!value.timeSignature) value.timeSignature = { numerator: 4, denominator: 4 };
		if (!value.editMode) value.editMode = 'select';
		if (!value.snapSetting) value.snapSetting = '1/4';
		if (!value.pixelsPerBeat) value.pixelsPerBeat = 80;
		if (!value.sampleRate) value.sampleRate = 44100;
		if (!value.ppqn) value.ppqn = 480;
	}

	// 백엔드 데이터 추출 - value가 변경될 때마다 백엔드 데이터 props 업데이트
	$: if (value && typeof value === 'object') {
		// value에서 백엔드 데이터가 있으면 props 업데이트
		if ('audio_data' in value && value.audio_data !== undefined) {
			console.log("🎵 Audio data updated:", !!value.audio_data);
			audio_data = typeof value.audio_data === 'string' ? value.audio_data : null;
		}
		if ('curve_data' in value && value.curve_data !== undefined) {
			console.log("📊 Curve data updated:", value.curve_data);
			curve_data = value.curve_data && typeof value.curve_data === 'object' ? value.curve_data : null;
		}
		if ('segment_data' in value && value.segment_data !== undefined) {
			console.log("📍 Segment data updated:", value.segment_data);
			segment_data = Array.isArray(value.segment_data) ? value.segment_data : null;
		}
		if ('use_backend_audio' in value && value.use_backend_audio !== undefined) {
			console.log("🔊 Backend audio flag:", value.use_backend_audio);
			use_backend_audio = typeof value.use_backend_audio === 'boolean' ? value.use_backend_audio : false;
		}
	}

	// 피아노롤에서 데이터 변경 시 호출되는 핸들러 (tempo, 노트 정보 등)
	function handlePianoRollChange(event: CustomEvent) {
		const { notes, tempo, timeSignature, editMode, snapSetting, pixelsPerBeat, sampleRate, ppqn } = event.detail;

		// value 전체 업데이트
		value = {
			notes: notes,
			tempo,
			timeSignature,
			editMode,
			snapSetting,
			pixelsPerBeat,
			sampleRate: sampleRate || 44100,
			ppqn: ppqn || 480
		};

		// Gradio로 변경사항 전달
		gradio.dispatch("change");
	}

	// 가사 수정 시 호출되는 핸들러 (input 이벤트 먼저 발생)
	function handleLyricInput(event: CustomEvent) {
		const { notes, lyricData } = event.detail;

		// 노트 정보 업데이트
		value = {
			...value,
			notes: notes
		};

		// input 이벤트 먼저 발생 (G2P 실행용)
		gradio.dispatch("input", lyricData);

		// 그 다음 change 이벤트 발생
		setTimeout(() => {
			gradio.dispatch("change");
		}, 0);
	}

	// 노트만 변경되었을 때 호출되는 핸들러 (가사 외의 노트 변경)
	function handleNotesChange(event: CustomEvent) {
		const { notes } = event.detail;

		// 노트만 업데이트
		value = {
			...value,
			notes: notes
		};

		// Gradio로 변경사항 전달
		gradio.dispatch("change");
	}

	// 재생 제어 이벤트 핸들러들
	function handlePlay(event: CustomEvent) {
		gradio.dispatch("play", event.detail);
	}

	function handlePause(event: CustomEvent) {
		gradio.dispatch("pause", event.detail);
	}

	function handleStop(event: CustomEvent) {
		gradio.dispatch("stop", event.detail);
	}

	function handleClear(event: CustomEvent) {
		gradio.dispatch("clear", event.detail);
	}
</script>

<Block {visible} {elem_id} {elem_classes} {container} {scale} {min_width}>
	{#if loading_status}
		<StatusTracker
			autoscroll={gradio.autoscroll}
			i18n={gradio.i18n}
			{...loading_status}
			on:clear_status={() => gradio.dispatch("clear_status", loading_status)}
		/>
	{/if}

	<!-- 피아노롤 컴포넌트 -->
	<PianoRoll
		width={width}
		height={height}
		notes={value.notes}
		tempo={value.tempo}
		timeSignature={value.timeSignature}
		editMode={value.editMode}
		snapSetting={value.snapSetting}
		pixelsPerBeat={value.pixelsPerBeat || 80}
		sampleRate={value.sampleRate || 44100}
		ppqn={value.ppqn || 480}
		{audio_data}
		{curve_data}
		{segment_data}
		{use_backend_audio}
		{elem_id}
		on:dataChange={handlePianoRollChange}
		on:noteChange={handleNotesChange}
		on:lyricInput={handleLyricInput}
		on:play={handlePlay}
		on:pause={handlePause}
		on:stop={handleStop}
		on:clear={handleClear}
	/>
</Block>
