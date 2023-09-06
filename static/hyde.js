const { createApp, watch, ref, onMounted, computed } = Vue

const app = createApp({
    delimiters: ['[[', ']]'],
    setup() {
        let query = ref('What happened to Titan submersible?')
        let language = ref('en')
        let title = ref('')
        let contexts = ref([])

        const getAnswer = (query) => {
            return fetch('/api/hyde', {
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
            contexts.value = []
            document.body.classList.add("wait")
            return getAnswer(query.value).then((contextObjs) => {
                contexts.value = contextObjs;
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
        }
    }
})

app.mount('#app')
