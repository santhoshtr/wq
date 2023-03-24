import { createApp, watch, ref, onMounted, computed } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
import debounce from './debounce.js'

const app = createApp({
    delimiters: ['[[', ']]'],
    setup() {
        let query = ref('Who built the Charminar?')
        let language = ref('en')
        let selectedIndex = ref(0)
        let title = ref('')
        let pageInfos = ref([])
        const fetchQuestions = () => {
            fetch(`/api/qa/${language.value || 'en'}/${title.value}`).then((response) => response.json()).then((r) => qas.value = r)
        }

        const getAnswer = (question) => {
            return fetch(`/api/q/${language.value || 'en'}/${title.value}`, {
                method: "POST",
                body: JSON.stringify({
                    question
                }),
                headers: {
                    "Content-type": "application/json; charset=UTF-8"
                }
            }).then((response) => response.json())
        }

        const selectQuestion = (qa) => {
            pageInfos.value = []
            answer.value = {}
            selectedQuestion.value = query.value
            if (!qa) {
                document.body.classList.add("wait")
                return getAnswer(query.value).then((answerObj) => {
                    answer.value = answerObj
                    selectedQuestion.value = query.value
                    searchResults.value = []
                }).finally(() => {
                    document.body.classList.remove("wait")
                    let titles = answer.value.searched_in || [title.value];
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
            selectedQuestion.value = qa.question
            query.value = qa.question
            answer.value = qa
            searchResults.value = []
            getPageInfo(language.value || 'en', title.value).then(pageInfo => {
                pageInfos.value.push({
                    url: pageInfo.content_urls?.desktop?.page,
                    title: pageInfo.title,
                    summary: pageInfo.extract || pageInfo.description,
                    image: pageInfo.thumbnail?.source,
                })
            })
        }

        let qas = ref([])
        let searchResults = ref([])
        let resultCount = 0
        const searchQuestions = () => {
            if (query.value === '') {
                return []
            }
            searchResults.value = qas.value.filter(qa => {
                if (
                    qa.question.toLowerCase().includes(query.value.toLowerCase()) &&
                    resultCount < 10
                ) {
                    resultCount++
                    return qa
                }
            })
            resultCount = 0;
        };
        watch(title, debounce(fetchQuestions, 300))
        watch(language, debounce(fetchQuestions, 300))
        watch(query, debounce(searchQuestions, 300))
        onMounted(() => fetchQuestions())
        let selectedQuestion = ref('')
        let answer = ref('')
        const moveDown = () => {
            if (selectedIndex.value < searchResults.value.length - 1) {
                selectedIndex.value++;
            }
            console.log(selectedIndex.value)
        };
        const moveUp = () => {
            if (selectedIndex.value !== -1) {
                selectedIndex.value--;
            }
        };
        const selectItem = (index) => {
            selectedIndex.value = index;
            selectQuestion(searchResults.value[selectedIndex.value]);
        };
        const chooseItem = (e) => {
            selectQuestion(searchResults.value[selectedIndex.value]);
        };
        const focusout = (e) => {
            setTimeout(() => {
                // handle focusout
            }, 100);
        };

        const getPageInfo = (language, title) => {
            return fetch(`https://${language}.wikipedia.org/api/rest_v1/page/summary/${title}`)
                .then((response) => response.json())
        };

        return {
            qas,
            query,
            language,
            title,
            searchQuestions,
            selectQuestion,
            selectedQuestion,
            searchResults,
            answer,
            chooseItem,
            moveDown,
            moveUp,
            selectedIndex,
            focusout,
            pageInfos
        }
    }
})

app.mount('#app')
