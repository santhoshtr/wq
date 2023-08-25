const { createApp, watch, ref, onMounted, computed } = Vue

const app = createApp({
    delimiters: ['[[', ']]'],
    setup() {
        let query = ref('Is Dodo a type of pigeon?')
        let language = ref('en')
        let title = ref('')
        let waiting = ref(false)
        let contexts = ref([])
        let pageInfos = ref({})

        const getPageInfo = (language, title) => {
            return fetch(`https://${language}.wikipedia.org/api/rest_v1/page/summary/${title}`)
                .then((response) => response.json())
        };


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
            contexts.value = []
            document.body.classList.add("wait")
            return getContexts(query.value).then((contextObjs) => {
                contexts.value = contextObjs
                for (let i = 0; i < contextObjs.length; i++) {
                    let title = contextObjs[i].title;
                    getPageInfo(contextObjs[i].wikicode || 'en', title).then(pageInfo => {
                        pageInfos.value[pageInfo.title]={
                        "url" : pageInfo.content_urls?.desktop?.page,
                        "imageurl": pageInfo.thumbnail?.source || "https://upload.wikimedia.org/wikipedia/en/8/80/Wikipedia-logo-v2.svg"
                        }
                    })
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
            waiting,
            pageInfos,

        }
    }
})

app.mount('#app')
