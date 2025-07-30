
import gradio as gr
from app import demo as app
import os

_docs = {'consilium_roundtable': {'description': 'Creates a visual roundtable component for AI consensus discussions.\n\nDisplays AI participants as avatars positioned around an oval table\nwith animated speech bubbles, thinking states, and real-time discussion updates.\nPerfect for multi-AI collaboration, decision-making processes, and consensus building.', 'members': {'__init__': {'value': {'type': 'str | Callable | None', 'default': 'None', 'description': 'JSON string containing the discussion state with participants, messages, current speaker, and thinking states. If a function is provided, it will be called each time the app loads to set the initial value.'}, 'placeholder': {'type': 'str | None', 'default': 'None', 'description': 'Not used in this component (roundtable displays participants instead).'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'The label for this component, displayed above the roundtable.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'Continuously calls `value` to recalculate it if `value` is a function (useful for live discussion updates).'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'If True, will display the label above the roundtable.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'Relative size compared to adjacent components in a Row or Blocks layout.'}, 'min_width': {'type': 'int', 'default': '600', 'description': 'Minimum pixel width for the component (default 600px for proper roundtable display).'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'If True, avatars can be clicked to show speech bubbles manually.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'rtl': {'type': 'bool', 'default': 'False', 'description': 'Not used in this component.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string assigned as the id of this component in the HTML DOM.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'Optional list of CSS classes assigned to this component.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not be rendered in the Blocks context initially.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': 'For gr.render() - components with the same key are treated as the same component across re-renders.'}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': 'Parameters preserved across re-renders when using keys.'}}, 'postprocess': {'value': {'type': 'Any', 'description': 'Discussion state as dict or JSON string containing:'}}, 'preprocess': {'return': {'type': 'str | None', 'description': 'Passes the JSON string value for processing.'}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the consilium_roundtable changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'input': {'type': None, 'default': None, 'description': 'This listener is triggered when the user changes the value of the consilium_roundtable.'}, 'submit': {'type': None, 'default': None, 'description': 'This listener is triggered when the user presses the Enter key while the consilium_roundtable is focused.'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'consilium_roundtable': []}}}

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
# `gradio_consilium_roundtable`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_consilium_roundtable/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_consilium_roundtable"></a>  
</div>

The roundtable for artificial minds
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_consilium_roundtable
```

## Usage

```python
import gradio as gr
from gradio_consilium_roundtable import consilium_roundtable
import time
import random
import json

def simulate_discussion():
    \"\"\"Simulate a live AI discussion\"\"\"
    
    # Initial state - everyone ready
    initial_state = {
        "participants": ["QwQ-32B", "DeepSeek-R1", "Mistral Large", "Meta-Llama-3.1-8B", "Web Search Agent"],
        "messages": [],
        "currentSpeaker": None,
        "thinking": [],
        "showBubbles": []
    }

    states = [
        # 1. QwQ-32B starts thinking
        {
            "participants": ["QwQ-32B", "DeepSeek-R1", "Mistral Large", "Meta-Llama-3.1-8B", "Web Search Agent"],
            "messages": [],
            "currentSpeaker": None,
            "thinking": ["QwQ-32B"],
            "showBubbles": []
        },
        
        # 2. DeepSeek-R1 and Search start thinking - QwQ-32B's bubble should stay visible
        {
            "participants": ["QwQ-32B", "DeepSeek-R1", "Mistral Large", "Meta-Llama-3.1-8B", "Web Search Agent"],
            "messages": [
                {"speaker": "QwQ-32B", "text": "This is a very long response that should demonstrate the scrolling functionality. I'm going to explain multiple points in detail. First, we need to consider the primary factors that influence this decision. Second, we must evaluate the potential risks and benefits. Third, there are several implementation strategies we could pursue. Fourth, the timeline and resource allocation are critical considerations. Finally, we should establish clear success metrics and monitoring procedures to ensure we achieve our objectives effectively."}
            ],
            "currentSpeaker": None,
            "thinking": ["DeepSeek-R1", "Web Search Agent"],
            "showBubbles": ["QwQ-32B"]  # KEEP CLAUDE'S BUBBLE VISIBLE
        },
        
        # 3. DeepSeek-R1 responds - both QwQ-32B and DeepSeek-R1 bubbles visible
        {
            "participants": ["QwQ-32B", "DeepSeek-R1", "Mistral Large", "Meta-Llama-3.1-8B", "Web Search Agent"],
            "messages": [
                {"speaker": "QwQ-32B", "text": "Here's my analysis:\n\n**Key Points:**\n- Point 1\n- Point 2\n\n`Code example` and [link](https://example.com)\n\n> This is a blockquote"},
                {"speaker": "DeepSeek-R1", "text": "That's a solid foundation, QwQ-32B. However, I'd like to add some statistical analysis to your reasoning..."}
            ],
            "currentSpeaker": "DeepSeek-R1",
            "thinking": [],
            "showBubbles": ["QwQ-32B"]  # CLAUDE'S BUBBLE STILL VISIBLE
        },
        
        # 4. Multiple models thinking - previous responses stay visible
        {
            "participants": ["QwQ-32B", "DeepSeek-R1", "Mistral Large", "Meta-Llama-3.1-8B", "Web Search Agent"],
            "messages": [
                {"speaker": "QwQ-32B", "text": "I think we should approach this problem from multiple angles. Let me analyze the key factors..."},
                {"speaker": "DeepSeek-R1", "text": "That's a solid foundation, QwQ-32B. However, I'd like to add some statistical analysis to your reasoning..."}
            ],
            "currentSpeaker": None,
            "thinking": ["Mistral Large", "Meta-Llama-3.1-8B"],
            "showBubbles": ["QwQ-32B", "DeepSeek-R1"]  # BOTH PREVIOUS RESPONSES VISIBLE
        },
        
        # 5. Search agent responds with data - all previous responses visible
        {
            "participants": ["QwQ-32B", "DeepSeek-R1", "Mistral Large", "Meta-Llama-3.1-8B", "Web Search Agent"],
            "messages": [
                {"speaker": "QwQ-32B", "text": "I think we should approach this problem from multiple angles. Let me analyze the key factors..."},
                {"speaker": "DeepSeek-R1", "text": "That's a solid foundation, QwQ-32B. However, I'd like to add some statistical analysis to your reasoning..."},
                {"speaker": "Web Search Agent", "text": "I found relevant data: According to recent studies, 73% of experts agree with this approach..."}
            ],
            "currentSpeaker": "Web Search Agent",
            "thinking": [],
            "showBubbles": ["QwQ-32B", "DeepSeek-R1"]  # PREVIOUS RESPONSES STAY VISIBLE
        }
    ]
    
    return initial_state, states

def update_discussion_state(state_index, states):
    \"\"\"Get the next state in the discussion\"\"\"
    if state_index >= len(states):
        state_index = 0
    return states[state_index], state_index + 1

# Initialize the discussion
initial_state, discussion_states = simulate_discussion()

with gr.Blocks() as demo:
    gr.Markdown("# 🎭 Consilium Roundtable Demo")
    gr.Markdown("**Watch the AI discussion unfold!** Click 'Next State' to see different phases of the discussion.")
    
    # State management
    state_counter = gr.State(0)
    
    # The roundtable component
    roundtable = consilium_roundtable(
        label="AI Discussion Roundtable",
        show_label=True,
        value=initial_state
    )
    
    with gr.Row():
        next_btn = gr.Button("▶️ Next Discussion State", variant="primary")
        reset_btn = gr.Button("🔄 Reset Discussion", variant="secondary")
    
    # Status display
    with gr.Row():
        status_display = gr.Markdown("**Status:** Discussion ready to begin")
    
    def next_state(current_counter):
        new_state, new_counter = update_discussion_state(current_counter, discussion_states)
        
        # Convert to proper JSON string
        json_state = json.dumps(new_state)
        
        # Create status message
        thinking_list = new_state.get("thinking", [])
        current_speaker = new_state.get("currentSpeaker")
        
        if thinking_list:
            status = f"**Status:** {', '.join(thinking_list)} {'is' if len(thinking_list) == 1 else 'are'} thinking..."
        elif current_speaker:
            status = f"**Status:** {current_speaker} is responding..."
        else:
            status = "**Status:** Discussion in progress..."
            
        return json_state, new_counter, status

    def reset_discussion():
        json_state = json.dumps(initial_state)
        return json_state, 0, "**Status:** Discussion reset - ready to begin"
    
    next_btn.click(
        next_state,
        inputs=[state_counter],
        outputs=[roundtable, state_counter, status_display]
    )
    
    reset_btn.click(
        reset_discussion,
        outputs=[roundtable, state_counter, status_display]
    )

if __name__ == "__main__":
    demo.launch()
```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `consilium_roundtable`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["consilium_roundtable"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["consilium_roundtable"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, passes the JSON string value for processing.
- **As output:** Should return, discussion state as dict or JSON string containing:.

 ```python
def predict(
    value: str | None
) -> Any:
    return value
```
""", elem_classes=["md-custom", "consilium_roundtable-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          consilium_roundtable: [], };
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
