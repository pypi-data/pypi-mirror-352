<script lang="ts">
    import { onMount } from "svelte";
    import Index from "./Index.svelte";

    let value = JSON.stringify({
        "participants": ["Claude", "GPT-4", "Mistral"],
        "messages": [
            {"speaker": "Claude", "text": "Welcome to the roundtable!"}
        ],
        "currentSpeaker": "Claude",
        "thinking": []
    });
</script>

<Index 
    {value}
    label="Example Roundtable"
    visible={true}
    elem_id="example"
    elem_classes={[]}
    scale={null}
    min_width={600}
    interactive={true}
    gradio={{}}
    loading_status={{}}
    show_label={true}
/>