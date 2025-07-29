import gradio as gr
from gradio_consilium_roundtable import consilium_roundtable
import time
import random
import json

def simulate_discussion():
    """Simulate a live AI discussion"""
    
    # Initial state - everyone ready
    initial_state = {
        "participants": ["Claude", "GPT-4", "Mistral", "Gemini", "Search"],
        "messages": [],
        "currentSpeaker": None,
        "thinking": []
    }
    
    # Discussion states to cycle through
    states = [
        # 1. Claude starts thinking
        {
            "participants": ["Claude", "GPT-4", "Mistral", "Gemini", "Search"],
            "messages": [],
            "currentSpeaker": None,
            "thinking": ["Claude"]
        },
        
        # 2. Claude responds
        {
            "participants": ["Claude", "GPT-4", "Mistral", "Gemini", "Search"],
            "messages": [
                {"speaker": "Claude", "text": "I think we should approach this problem from multiple angles. Let me analyze the key factors..."}
            ],
            "currentSpeaker": "Claude",
            "thinking": []
        },
        
        # 3. GPT-4 and Search start thinking
        {
            "participants": ["Claude", "GPT-4", "Mistral", "Gemini", "Search"],
            "messages": [
                {"speaker": "Claude", "text": "I think we should approach this problem from multiple angles. Let me analyze the key factors..."}
            ],
            "currentSpeaker": None,
            "thinking": ["GPT-4", "Search"]
        },
        
        # 4. GPT-4 responds
        {
            "participants": ["Claude", "GPT-4", "Mistral", "Gemini", "Search"],
            "messages": [
                {"speaker": "Claude", "text": "I think we should approach this problem from multiple angles. Let me analyze the key factors..."},
                {"speaker": "GPT-4", "text": "That's a solid foundation, Claude. However, I'd like to add some statistical analysis to your reasoning..."}
            ],
            "currentSpeaker": "GPT-4",
            "thinking": []
        },
        
        # 5. Multiple models thinking
        {
            "participants": ["Claude", "GPT-4", "Mistral", "Gemini", "Search"],
            "messages": [
                {"speaker": "Claude", "text": "I think we should approach this problem from multiple angles. Let me analyze the key factors..."},
                {"speaker": "GPT-4", "text": "That's a solid foundation, Claude. However, I'd like to add some statistical analysis to your reasoning..."}
            ],
            "currentSpeaker": None,
            "thinking": ["Mistral", "Gemini"]
        },
        
        # 6. Search agent responds with data
        {
            "participants": ["Claude", "GPT-4", "Mistral", "Gemini", "Search"],
            "messages": [
                {"speaker": "Claude", "text": "I think we should approach this problem from multiple angles. Let me analyze the key factors..."},
                {"speaker": "GPT-4", "text": "That's a solid foundation, Claude. However, I'd like to add some statistical analysis to your reasoning..."},
                {"speaker": "Search", "text": "I found relevant data: According to recent studies, 73% of experts agree with this approach..."}
            ],
            "currentSpeaker": "Search",
            "thinking": []
        }
    ]
    
    return initial_state, states

def update_discussion_state(state_index, states):
    """Get the next state in the discussion"""
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