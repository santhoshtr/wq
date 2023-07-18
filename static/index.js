const { createApp, watch, ref, onMounted, computed } = Vue

const app = createApp({
    delimiters: ['[[', ']]'],
    setup() {
        let query = ref('What is water?')
        let language = ref('en')
        let title = ref('')
        let pageInfos = ref([])

        const getAnswer = async (query, context) => {
            answer.value.waiting = true
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
            answer.value.answer = ""
            while (!done) {
              ({ value, done } = await reader.read());
              if (done) {
                return;
              }
              if(value){
                answer.value.waiting = false
              }
              value = decoder.decode(value);
              answer.value.answer += value
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
            pageInfos.value = []
            answer.value = {}
            document.body.classList.add("wait")
            return getContexts(query.value).then((contextObj) => {
                answer.value = contextObj
                getAnswer(query.value, contextObj.context);
            }).finally(() => {
                document.body.classList.remove("wait")
                let titles = [answer.value.title];
                for (let i = 0; i < titles.length; i++) {
                    let title = titles[i];
                    getPageInfo(language.value || 'en', title).then(pageInfo => {
                        pageInfos.value.push({
                            url: pageInfo.content_urls?.desktop?.page,
                            title: pageInfo.title,
                            summary: pageInfo.extract || pageInfo.description,
                            image: pageInfo.thumbnail?.source || "https://upload.wikimedia.org/wikipedia/en/8/80/Wikipedia-logo-v2.svg",
                        })
                    })
                }
            });
        }

        let answer = ref('')
        const getPageInfo = (language, title) => {
            return fetch(`https://${language}.wikipedia.org/api/rest_v1/page/summary/${title}`)
                .then((response) => response.json())
        };

        return {
            query,
            language,
            title,
            onQuery,
            answer,
            pageInfos
        }
    }
})

app.mount('#app')
