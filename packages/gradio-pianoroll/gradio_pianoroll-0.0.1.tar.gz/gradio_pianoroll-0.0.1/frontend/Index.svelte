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

	// 기본 샘플 노트 데이터
	const defaultNotes = [
		{
			id: 'note-1',
			start: 80, // 1st beat of measure 1
			duration: 80, // Quarter note
			pitch: 60, // Middle C
			velocity: 100,
			lyric: '안녕'
		},
		{
			id: 'note-2',
			start: 160, // 1st beat of measure 2
			duration: 160, // Half note
			pitch: 64, // E
			velocity: 90,
			lyric: '하세요'
		},
		{
			id: 'note-3',
			start: 320, // 1st beat of measure 3
			duration: 80, // Quarter note
			pitch: 67, // G
			velocity: 95,
			lyric: '반가워요'
		}
	];

	export let value = {
		notes: defaultNotes,
		tempo: 120,
		timeSignature: { numerator: 4, denominator: 4 },
		editMode: 'select',
		snapSetting: '1/4'
	};
	export let container = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus;
	export let gradio: Gradio<{
		change: never;
		select: SelectData;
		input: never;
		clear_status: LoadingStatus;
	}>;

	export let width = 800;
	export let height = 400;



	// value가 초기화되지 않았거나 note가 비어있을 때 기본값 설정
	$: if (!value || !value.notes) {
		value = {
			notes: defaultNotes,
			tempo: value?.tempo || 120,
			timeSignature: value?.timeSignature || { numerator: 4, denominator: 4 },
			editMode: value?.editMode || 'select',
			snapSetting: value?.snapSetting || '1/4'
		};
	}

	// 피아노롤에서 데이터 변경 시 호출되는 핸들러
	function handlePianoRollChange(event: CustomEvent) {
		const { notes, tempo, timeSignature, editMode, snapSetting } = event.detail;

		// value 전체 업데이트
		value = {
			notes: notes,
			tempo,
			timeSignature,
			editMode,
			snapSetting
		};

		// Gradio로 변경사항 전달
		gradio.dispatch("change");
		gradio.dispatch("input");
	}

	// 노트만 변경되었을 때 호출되는 핸들러
	function handleNotesChange(event: CustomEvent) {
		const { notes } = event.detail;

		// 노트만 업데이트
		value = {
			...value,
			notes: notes
		};

		// Gradio로 변경사항 전달
		gradio.dispatch("change");
		gradio.dispatch("input");
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
		on:dataChange={handlePianoRollChange}
		on:noteChange={handleNotesChange}
	/>
</Block>
