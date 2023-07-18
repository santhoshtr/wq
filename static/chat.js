const { createApp, watch, ref, onMounted, computed } = Vue

const app = createApp({
    delimiters: ['[[', ']]'],
    setup() {
        let prompt = ref('What is water?')
        let reply = ref('')
        let waiting = ref(false)
        const getReply = async () => {
            waiting.value = true
            const decoder = new TextDecoder("utf-8");
            reply.value = ""
            const response = await fetch('/api/chat', {
                method: "POST",
                body: JSON.stringify({
                    prompt: prompt.value,
                }),
                headers: {
                    "Content-type": "application/json; charset=UTF-8"
                }
            })

            const reader = response.body.getReader();
            let done, value;
            while (!done) {
                ({ value, done } = await reader.read());
                if (done) {
                    return;
                }
                if (value) {
                    waiting.value = false
                }
                value = decoder.decode(value);
                reply.value += value
            }
        }

        const onPrompt = () => {

            return getReply()
        }
        return {
            prompt,
            reply,
            onPrompt,
            waiting,
        }
    }
})

app.mount('#chatapp')
