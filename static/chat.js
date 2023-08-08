const { createApp, watch, ref, onMounted, computed } = Vue

const placeholder="Instruction:\n\
You are a natural language generation system that generates well written sentences from given data. \
You generate sentences only based on the given data.\
\n\n\
Data:\n\
\n\
Place name: Mudipon\n\
Country: Thailand\n\
Area: 2,034 km\n\
Known for : tourism\n\
vistitors: 6 million per year.\n\
popular resorts: Puerto de la Cruz and Playa de las Américas.\n\
Climate: Tropical\n\
\n\
The above data can be written in paragraph as:"

const app = createApp({
    delimiters: ['[[', ']]'],
    setup() {
        let prompt = ref(placeholder)
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
