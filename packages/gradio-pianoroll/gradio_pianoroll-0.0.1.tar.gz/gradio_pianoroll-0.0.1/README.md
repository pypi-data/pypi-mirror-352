---
tags: [gradio-custom-component, ]
title: gradio_pianoroll
short_description: A PianoRoll Component for
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_pianoroll`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  

A PianoRoll Component for Gradio.

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

## `PianoRoll`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
dict | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">default MIDI notes data to provide in piano roll. If a function is provided, the function will be called each time the app loads to set the initial value of this component.</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
"Timer | float | None"
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.</td>
</tr>

<tr>
<td align="left"><code>inputs</code></td>
<td align="left" style="width: 25%;">

```python
Component | Sequence[Component] | set[Component] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, will display label.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>160</code></td>
<td align="left">minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, will be rendered as an editable piano roll; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>

<tr>
<td align="left"><code>key</code></td>
<td align="left" style="width: 25%;">

```python
int | str | tuple[int | str, ...] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.</td>
</tr>

<tr>
<td align="left"><code>preserved_by_key</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>"value"</code></td>
<td align="left">A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.</td>
</tr>

<tr>
<td align="left"><code>width</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>1000</code></td>
<td align="left">width of the piano roll component in pixels.</td>
</tr>

<tr>
<td align="left"><code>height</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>600</code></td>
<td align="left">height of the piano roll component in pixels.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` | Triggered when the value of the PianoRoll changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `input` | This listener is triggered when the user changes the value of the PianoRoll. |



