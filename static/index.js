const { createApp, watch, ref, onMounted, computed } = Vue

const app = createApp({
    delimiters: ['[[', ']]'],
    setup() {
        let query = ref('What is water?')
        let language = ref('en')
        let title = ref('')
        let waiting = ref(false)
        let answer = ref('')
        let contexts = ref([])


        const getAnswer = async (query, context) => {
            waiting.value = true
            const decoder = new TextDecoder("utf-8");
            const response = await fetch('/api/q', {
                method: "POST",
                body: JSON.stringify({
                    query,
                    language: language.value,
                    context,
                }),
                headers: {
                    "Content-type": "application/json; charset=UTF-8"
                }
            })

            const reader = response.body.getReader();
            let done, value;
            answer.value = ""
            while (!done) {
                ({ value, done } = await reader.read());
                if (done) {
                    return;
                }
                if (value) {
                    waiting.value = false
                }
                value = decoder.decode(value);
                answer.value += value
            }
        }

        const getContexts = (query) => {
            return fetch('/api/r', {
                method: "POST",
                body: JSON.stringify({
                    query,
                    language: language.value,
                    title: title.value,
                }),
                headers: {
                    "Content-type": "application/json; charset=UTF-8"
                }
            }).then((response) => response.json())
        }

        const onQuery = () => {
            answer.value = ''
            contexts.value = []
            document.body.classList.add("wait")
            return getContexts(query.value).then((contextObjs) => {
                contexts.value = contextObjs
                if (contextObjs.length) {
                    const bestContext = contextObjs[0];
                    if (bestContext.score < 0.75) {
                        getAnswer(query.value, bestContext.context);
                    } else {
                        answer.value = '';
                        waiting.value = false;
                    }
                }
            }).finally(() => {
                document.body.classList.remove("wait")
            });
        }


        return {
            query,
            language,
            title,
            onQuery,
            contexts,
            answer,
            waiting,

        }
    }
})

app.mount('#app')
