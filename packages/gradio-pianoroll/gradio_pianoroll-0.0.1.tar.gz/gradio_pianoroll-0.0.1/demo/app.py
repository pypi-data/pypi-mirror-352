import gradio as gr
from gradio_pianoroll import PianoRoll

def convert(piano_roll):
    print("=== Convert function called ===")
    print("Received piano_roll:")
    print(piano_roll)
    print("Type:", type(piano_roll))
    return piano_roll
with gr.Blocks() as demo:
    gr.Markdown("# Gradio PianoRoll: Gradio에서 피아노롤 컴포넌트 사용")

    with gr.Row():
        with gr.Column():
            # 초기값을 명시적으로 설정
            initial_value = {
                "notes": [
                    {
                        "id": "note-1",
                        "start": 80,
                        "duration": 80,
                        "pitch": 60,
                        "velocity": 100,
                        "lyric": "테스트"
                    }
                ],
                "tempo": 140,
                "timeSignature": {"numerator": 4, "denominator": 4},
                "editMode": "select",
                "snapSetting": "1/4"
            }
            piano_roll = PianoRoll(height=600, width=1000, value=initial_value)

    with gr.Row():
        with gr.Column():
            output_json = gr.JSON()

    with gr.Row():
        with gr.Column():
            btn = gr.Button("Convert & Debug")

    # 버튼 클릭 이벤트
    btn.click(
        fn=convert,
        inputs=piano_roll,
        outputs=output_json,
        show_progress=True
    )

if __name__ == "__main__":
    demo.launch()
