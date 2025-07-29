
import gradio as gr
from app import demo as app
import os

_docs = {'PianoRoll': {'description': 'A base class for defining methods that all input/output components should have.', 'members': {'__init__': {'value': {'type': 'dict | None', 'default': 'None', 'description': 'default MIDI notes data to provide in piano roll. If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.'}, 'every': {'type': '"Timer | float | None"', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display label.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will be rendered as an editable piano roll; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': "in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}, 'width': {'type': 'int | None', 'default': '1000', 'description': 'width of the piano roll component in pixels.'}, 'height': {'type': 'int | None', 'default': '600', 'description': 'height of the piano roll component in pixels.'}}, 'postprocess': {}, 'preprocess': {}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the PianoRoll changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'input': {'type': None, 'default': None, 'description': 'This listener is triggered when the user changes the value of the PianoRoll.'}}}, '__meta__': {'additional_interfaces': {}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_pianoroll`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

A PianoRoll Component for Gradio.
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_pianoroll
```

## Usage

```python
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

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `PianoRoll`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["PianoRoll"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["PianoRoll"]["events"], linkify=['Event'])







    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {};
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
