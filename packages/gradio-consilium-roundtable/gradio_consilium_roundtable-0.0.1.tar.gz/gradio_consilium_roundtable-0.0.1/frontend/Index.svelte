<script lang="ts">
    export let gradio: any;
    export let elem_id: string = "";
    export let elem_classes: string[] = [];
    export let visible: boolean = true;
    export let value: string = "{}";
    export let label: string = "Consilium Roundtable";
    export let show_label: boolean = true;
    export let scale: number | null = null;
    export let min_width: number | undefined = undefined;
    export let loading_status: any;
    export let interactive: boolean = true;

    $: containerClasses = `wrapper ${elem_classes.join(' ')}`;
    $: containerStyle = scale ? `--scale: ${scale}` : '';
    $: minWidthStyle = min_width ? `min-width: ${min_width}px` : '';
    $: isInteractive = interactive;

    let participants = [];
    let messages = [];
    let currentSpeaker = null;
    let thinking = [];
    
    function updateFromValue() {
		try {
			const parsedValue = JSON.parse(value);
			
			participants = parsedValue.participants || [];
			messages = parsedValue.messages || [];
			currentSpeaker = parsedValue.currentSpeaker || null;
			thinking = parsedValue.thinking || [];
			
			console.log("Clean JSON parsed:", {participants, messages, currentSpeaker, thinking});
		} catch (e) {
			console.error("Invalid JSON:", value, e);
		}
	}
    
    $: value, updateFromValue();
    
    const avatarEmojis = {
        "Claude": "🤖",
        "GPT-4": "🧠", 
        "Mistral": "🦾",
        "Gemini": "💎",
        "Search": "🔍",
        "OpenAI": "🧠",
        "Anthropic": "🤖",
        "Google": "💎"
    };
    
    function getEmoji(name: string) {
        return avatarEmojis[name] || "🤖";
    }
    
    function getLatestMessage(speaker: string) {
        if (thinking.includes(speaker)) {
            return `${speaker} is thinking...`;
        }
        if (currentSpeaker === speaker) {
            return `${speaker} is responding...`;
        }
        
        const speakerMessages = messages.filter(m => m.speaker === speaker);
        if (speakerMessages.length === 0) {
            return `${speaker} is ready to discuss...`;
        }
        return speakerMessages[speakerMessages.length - 1].text || `${speaker} responded`;
    }
    
    function isBubbleVisible(speaker: string) {
        const isThinking = thinking.includes(speaker);
        const isSpeaking = currentSpeaker === speaker;
        const visible = isThinking || isSpeaking;
        
        console.log(`${speaker} bubble visible:`, visible, {isThinking, isSpeaking});
        return visible;
    }
    
    function isAvatarActive(speaker: string) {
        return thinking.includes(speaker) || currentSpeaker === speaker;
    }
    
    function getPosition(index: number, total: number) {
        const angle = (360 / total) * index;
        const radians = (angle - 90) * (Math.PI / 180);
        
        const radiusX = 260;
        const radiusY = 180;
        
        const x = Math.cos(radians) * radiusX;
        const y = Math.sin(radians) * radiusY;
        
        return {
            left: `calc(50% + ${x}px)`,
            top: `calc(50% + ${y}px)`,
            transform: 'translate(-50%, -50%)'
        };
    }
</script>

<div 
    class={containerClasses} 
    class:hidden={!visible} 
    id={elem_id}
    style="{containerStyle}; {minWidthStyle}"
>
    {#if show_label && label}
        <label class="block-title" for="consilium-roundtable">{label}</label>
    {/if}
    
    <div class="consilium-container" id="consilium-roundtable">
        <div class="table-center">
            <div class="consensus-flame">🎭</div>
            <div class="table-label">CONSILIUM</div>
        </div>
        
        <div class="participants-circle">
            {#each participants as participant, index}
                <div 
                    class="participant-seat" 
                    style="left: {getPosition(index, participants.length).left}; top: {getPosition(index, participants.length).top}; transform: {getPosition(index, participants.length).transform};"
                >
                    <div class="speech-bubble" class:visible={isBubbleVisible(participant)}>
                        <div class="bubble-content">{getLatestMessage(participant)}</div>
                        <div class="bubble-arrow"></div>
                    </div>
                    
                    <div 
                        class="avatar" 
                        class:speaking={isAvatarActive(participant)}
                        class:thinking={thinking.includes(participant)}
                        class:responding={currentSpeaker === participant}
                        role="button"
                        tabindex="0"
                    >
                        {getEmoji(participant)}
                    </div>
                    <div class="participant-name">{participant}</div>
                </div>
            {/each}
        </div>
    </div>
</div>

<style>
    .hidden {
        display: none;
    }
    
    .block-title {
        display: block;
        margin-bottom: 10px;
        padding: 10px;
        font-weight: bold;
        color: #ffd700;
    }

    .wrapper {
        width: 600px;
        height: 500px;
        position: relative;
    }

    .consilium-container {
        top: 50px;
        position: relative;
        width: 450px;
        height: 300px;
        margin: 20px auto;
        border-radius: 50%;
        background: linear-gradient(135deg, #0f5132, #198754);
        border: 8px solid #8b4513;
        box-shadow: 
            0 8px 32px rgba(0,0,0,0.4),
            inset 0 0 20px rgba(0,0,0,0.2);
    }

    .table-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        background: rgba(0,0,0,0.3);
        border-radius: 50%;
        width: 140px;
        height: 100px; 
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 2px solid #8b4513;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }

    .consensus-flame {
        font-size: 2rem;
        margin-bottom: 5px;
    }

    .table-label {
        color: #ffd700;
        font-size: 0.7rem;
        font-weight: bold;
        letter-spacing: 2px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }

    .participant-seat {
        position: absolute;
    }

    .avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        background: linear-gradient(145deg, #ffffff, #e6e6e6);
        border: 3px solid #8b4513;
        box-shadow: 
            0 6px 15px rgba(0,0,0,0.3),
            inset 0 2px 5px rgba(255,255,255,0.5);
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        z-index: 10;
    }

    .avatar:hover {
        transform: scale(1.05);
        box-shadow: 
            0 8px 20px rgba(0,0,0,0.4),
            inset 0 2px 5px rgba(255,255,255,0.5);
    }

    .avatar.thinking {
        border-color: #ff6b35;
        animation: thinking-pulse 1.5s infinite;
    }

    .avatar.responding {
        border-color: #ffd700;
        animation: speaking-glow 1s infinite;
    }

    .avatar.speaking {
        border-color: #ffd700;
    }

    .participant-name {
        font-size: 0.75rem;
        font-weight: bold;
        color: #ffd700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.8);
        text-align: center;
        white-space: nowrap;
        background: rgba(0,0,0,0.3);
        padding: 2px 8px;
        border-radius: 10px;
        border: 1px solid #8b4513;
    }

    .speech-bubble {
        position: absolute;
        bottom: 85px;
        left: 50%;
        transform: translateX(-50%) translateY(20px);
        background: white;
        border-radius: 15px;
        padding: 10px 14px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        z-index: 20;
        opacity: 0;
        transition: all 0.4s ease;
        pointer-events: none;
        border: 2px solid #8b4513;
        max-width: 200px;
        word-wrap: break-word;
        white-space: normal;
    }

    .speech-bubble.visible {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
        pointer-events: auto;
    }

    .bubble-content {
        font-size: 0.8rem;
        color: #333;
        line-height: 1.3;
        text-align: center;
    }

    .bubble-arrow {
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-top: 10px solid white;
    }

    .bubble-arrow::before {
        content: '';
        position: absolute;
        bottom: 2px;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 12px solid transparent;
        border-right: 12px solid transparent;
        border-top: 12px solid #8b4513;
    }

    @keyframes thinking-pulse {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 0 6px 15px rgba(0,0,0,0.3), 0 0 15px rgba(255, 107, 53, 0.4);
        }
        50% { 
            transform: scale(1.03);
            box-shadow: 0 8px 20px rgba(0,0,0,0.4), 0 0 25px rgba(255, 107, 53, 0.6);
        }
    }

    @keyframes speaking-glow {
        0%, 100% { 
            box-shadow: 0 6px 15px rgba(0,0,0,0.3), 0 0 20px rgba(255, 215, 0, 0.5);
        }
        50% { 
            box-shadow: 0 8px 20px rgba(0,0,0,0.4), 0 0 30px rgba(255, 215, 0, 0.8);
        }
    }
</style>