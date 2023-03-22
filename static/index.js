import { createApp, watch, ref, onMounted, computed } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
import debounce from './debounce.js'

const app = createApp({
    delimiters: ['[[', ']]'],
    setup() {
        let query = ref('')
        let language = ref('')
        let selectedIndex = ref(0)
        let title = ref('')

        const fetchQuestions = ()=> {
            fetch(`/api/qa/${language.value||'en'}/${title.value}`).then((response) => response.json()).then((r)=>qas.value=r)
        }

        const getAnswer = (question)=> {
            return fetch(`/api/q/${language.value||'en'}/${title.value}`,{
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
            if(!qa){
                document.body.classList.add("wait")
                return getAnswer(query.value).then((answerObj)=>{
                    answer.value = answerObj
                    selectedQuestion.value = query.value
                    searchResults.value=[]
                }).finally(()=>{
                    document.body.classList.remove("wait")
                });
            }
            selectedQuestion.value = qa.question
            query.value = qa.question
            answer.value = qa
            searchResults.value=[]
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
        const moveDown = ()=> {
			if (selectedIndex.value < searchResults.value.length - 1) {
				selectedIndex.value++;
			}
            console.log(selectedIndex.value)
		};
		const  moveUp=()=> {
			if (selectedIndex.value !== -1) {
				selectedIndex.value--;
			}
		};
		const selectItem=(index) =>{
			selectedIndex.value = index;
			selectQuestion(searchResults.value[selectedIndex.value]);
		};
		const chooseItem=(e) =>{
			selectQuestion(searchResults.value[selectedIndex.value]);
		};
		const focusout=(e)=> {
			setTimeout(() => {
				// if (!this.clickedChooseItem) {
				// 	this.searchMatch = [];
				// 	this.selectedIndex = -1;
				// }
				// this.clickedChooseItem = false;
			}, 100);
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
            focusout
        }
    }
})

app.mount('#app')
