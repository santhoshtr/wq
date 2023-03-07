import { createApp, watch, ref, onMounted, computed } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
import debounce from './debounce.js'

const app = createApp({
    delimiters: ['[[', ']]'],
    setup() {
        let query = ref('')
        let language = ref('en')
        let title = ref('Charminar')
        const selectQuestion = (qa) => {
            selectedQuestion.value = qa.question
            query.value = qa.question
            answer.value = qa.answer
            searchResults.value=[]
        }
        const fetchQuestions = ()=> {
            fetch(`/api/qa/${language.value}/${title.value}`).then((response) => response.json()).then((r)=>qas.value=r)
        }
        let qas = ref([])
        let searchResults = ref([])
        let resultCount=0
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
            resultCount=0;
        };
        watch(title, debounce (fetchQuestions, 300 ))
        watch(language, debounce (fetchQuestions, 300 ))
        watch(query, debounce (searchQuestions, 300 ))
        onMounted(()=>fetchQuestions())
        let selectedQuestion = ref('')
        let answer = ref('')
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
        }
    }
})

app.mount('#app')
