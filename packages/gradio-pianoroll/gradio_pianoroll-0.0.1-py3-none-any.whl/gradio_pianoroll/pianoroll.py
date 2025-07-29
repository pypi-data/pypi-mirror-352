from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from gradio.components.base import Component
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer

class PianoRoll(Component):

    EVENTS = [
        Events.change,
        Events.input,
    ]

    def __init__(
        self,
        value: dict | None = None,
        *,
        label: str | I18nData | None = None,
        every: "Timer | float | None" = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        width: int | None = 1000,
        height: int | None = 600,
    ):
        """
        Parameters:
            value: default MIDI notes data to provide in piano roll. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will be rendered as an editable piano roll; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            width: width of the piano roll component in pixels.
            height: height of the piano roll component in pixels.
        """
        self.width = width
        self.height = height
        if value is None:
            self.value = {
                "notes": [],
                "tempo": 120,
                "timeSignature": { "numerator": 4, "denominator": 4 },
                "editMode": "select",
                "snapSetting": "1/4"
            }
        else:
            self.value = value

        self._attrs = {
            "width": width,
            "height": height,
            "value": self.value,
        }

        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            value=value,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )

    def preprocess(self, payload):
        """
        This docstring is used to generate the docs for this custom component.
        Parameters:
            payload: the MIDI notes data to be preprocessed, sent from the frontend
        Returns:
            the data after preprocessing, sent to the user's function in the backend
        """
        return payload

    def postprocess(self, value):
        """
        This docstring is used to generate the docs for this custom component.
        Parameters:
            value: the MIDI notes data to be postprocessed, sent from the user's function in the backend
        Returns:
            the data after postprocessing, sent to the frontend
        """
        return value

    def example_payload(self):
        return {
            "notes": [
                {
                    "id": "note-1",
                    "start": 80,
                    "duration": 80,
                    "pitch": 60,
                    "velocity": 100,
                    "lyric": "안녕"
                }
            ],
            "tempo": 120,
            "timeSignature": { "numerator": 4, "denominator": 4 },
            "editMode": "select",
            "snapSetting": "1/4"
        }

    def example_value(self):
        return {
            "notes": [
                {
                    "id": "note-1",
                    "start": 80,
                    "duration": 80,
                    "pitch": 60,
                    "velocity": 100,
                    "lyric": "안녕"
                },
                {
                    "id": "note-2",
                    "start": 160,
                    "duration": 160,
                    "pitch": 64,
                    "velocity": 90,
                    "lyric": "하세요"
                }
            ],
            "tempo": 120,
            "timeSignature": { "numerator": 4, "denominator": 4 },
            "editMode": "select",
            "snapSetting": "1/4"
        }

    def api_info(self):
        return {
            "type": "object",
            "properties": {
                "notes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "start": {"type": "number"},
                            "duration": {"type": "number"},
                            "pitch": {"type": "number"},
                            "velocity": {"type": "number"},
                            "lyric": {"type": "string"}
                        },
                        "required": ["id", "start", "duration", "pitch", "velocity"]
                    }
                },
                "tempo": {
                    "type": "number",
                    "description": "BPM tempo"
                },
                "timeSignature": {
                    "type": "object",
                    "properties": {
                        "numerator": {"type": "number"},
                        "denominator": {"type": "number"}
                    },
                    "required": ["numerator", "denominator"]
                },
                "editMode": {
                    "type": "string",
                    "description": "Current edit mode"
                },
                "snapSetting": {
                    "type": "string",
                    "description": "Note snap setting"
                }
            },
            "required": ["notes", "tempo", "timeSignature", "editMode", "snapSetting"],
            "description": "Piano roll data object containing notes array and settings"
        }
