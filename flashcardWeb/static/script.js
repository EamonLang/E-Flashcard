
// loads dates from backend

function get_dates(){
    fetch("/get_practice_dates")
    .then (response=>response.json())
    .then (data =>{
        if (data.status === "success"){
            const practiceDates = data.dates.map(d=>{
                const dateObj = new Date(d[0])
                const year = dateObj.getFullYear()
                const month = String(dateObj.getMonth() + 1).padStart(2, '0');
                const day = String(dateObj.getDate()).padStart(2, '0');
                return `${year}-${month}-${day}`

                // const formattedDate = dateObj.toISOString().split('T')[0]

                // return formattedDate
            })//takes the time off the date

            const today= new Date()
            for(let i=0; i<7; i++){
                const dayCirc = document.getElementById(`day${i+1}`)

                if (dayCirc){
                    const pastDate = new Date()
                    pastDate.setDate(today.getDate() - (7-i))//gets past 6 dates to today as it cycles through
                    
                    const checkDate = pastDate.toISOString().split('T')[0]//sets the past date to the date we wanna check and the right format

                    if(practiceDates.includes(checkDate)){
                        dayCirc.style.backgroundColor="green"
                    }else{
                        dayCirc.style.backgroundColor="red"
                    }
                }
            }

        }else{
            console.log("error")
        }
    })
    .catch(error =>{
        console.log("error",error)
    })
}

if (window.location.pathname === "/"){
    get_dates()
}

function getUrlFromSearch(){
    //write function to load the set onto the page

    const params = new URLSearchParams(window.location.search)
    return params.get("title")
}


function loadFlashcardFromUrl(){
    const title = getUrlFromSearch()
    if (!title) return

    fetch('api/load_flashcards',{
        method: 'POST',
        headers: {
            'Content-type':'application/json'
        },
        body: JSON.stringify({'title':title})
    })
    .then (response => response.json())
    .then (data => {
        if (data.status === "success"){
            displayFlashcards(data.flashcards)

        }
    })
}

function displayFlashcards(q_a){
    const cardText = document.getElementById("cardText")
    const cardButton = document.getElementById("card")
        
    
    if (cardButton){
            // indexes the pairs within q_a
            let index_pair = 0
        //   indexes the question and answer within each pair
            let index_indiv = 0
                cardButton.addEventListener("click",function(){
                    cardText.innerText = q_a[index_pair][index_indiv]
                    index_indiv =index_indiv%2
                    if (index_indiv === 1){
                        if(index_pair<q_a.length-1){
                        index_pair++
                        index_indiv = 0
                    }else{
                        index_pair=0
                        // here is where user score should go up by 1
                        index_indiv = 0
                        updateUserScore()
                    }
                    }else{
                        index_indiv++
                    }
                    
                    
                })
        
    }else{
        console.log('No flashcard data found')

    }}

// function to update score and last time practiced
function updateUserScore(){
    const data = {
        score:1,
        time: new Date().toISOString().split('T')[0]
    }
    fetch('/update_score',{
        method:'POST',
        headers:{
            'Content-type':'application/json'
        },
        body: JSON.stringify(data)
    })
    .then (response=> response.json())
    .then(data=> {
        if (data.status === "success"){
            console.log("update succesful")
        }else{
            console.log("error updating",data.message)
        }
    })
    .catch (error=>{
        console.error("Error",error)
    })
}

// function to load in sets and show them on the page
const load_title = function(){
    fetch('/api/flashcard_title')
        .then( response => response.json())
        .then( data =>{
            const list  = document.getElementById("user_sets")
            list.innerHTML = ''

            data.forEach(card =>{
                const listItem = document.createElement("li")

                const link = document.createElement("a")
                if (card==="Login to create sets"){
                    link.textContent = card
                    link.href="/login"

                }else if(card==="Create sets to begin practicing!"){
                    link.textContent=card
                    link.href="/create"
                }else{
                    link.textContent = card
                    link.href=link.href = `/set?title=${encodeURIComponent(card)}`
                }
                
                listItem.appendChild(link)
                list.appendChild(listItem)
        })
    })
}



const list =document.getElementById("user_sets")
if (list){
    document.addEventListener('DOMContentLoaded',load_title)
}
if (window.location.pathname === '/set'){
    document.addEventListener("DOMContentLoaded",loadFlashcardFromUrl)
}
            


// gets input and saves it to the database when creating sets       

if (window.location.pathname === '/create'){
        let set = null
        const enter = document.getElementById("enter_title")
        const titleInput = document.getElementById("title")
        const titleExample = document.getElementById("title-example")
        enter.addEventListener("click",function(){
            const titleText = titleInput.value.trim()
            if (titleText !== ""){
                titleExample.innerText = `Title: ${titleText}`
                set = {title:titleText,cards:[]}
                titleInput.value = ""
            }

        })
        titleInput.value = ""
        const qaEnter = document.getElementById("QA_button")//enter button

        const questionS = document.getElementById("question")//input boxes
        const answerS = document.getElementById("answer")//input boxes


        // the model cards on create page
        const cardQuestion = document.getElementById("create-cardText-question")
        const cardAnswer = document.getElementById("create-cardText-answer")
        
        qaEnter.addEventListener("click",function(){
            const questionText = questionS.value.trim()//value in text box
            const answerText=answerS.value.trim()//value in text box
            // makes sure sure enters something
            if (questionText !== "" && answerText !== "" && set){
                // now send to backend
                set.cards.push({question:questionText,answer:answerText})
                // display what the text will look like on the card
                cardQuestion.innerText = questionText
                cardAnswer.innerText = answerText
                // cardQuestion.value=questionText
                // cardAnswer.value= answerText
                // clears the text box
                questionS.value=""
                answerS.value=""
            }else{
                alert("Make sure you have entered a title and filled out something for both question and answer")
            }
        })
        const home = document.getElementById("home")
        home.addEventListener("click",function(){
            fetch('/add_set',{
                method: 'POST',
                headers: {
                    'Content-Type':'application/json',
                },
                body: JSON.stringify(set)
            })
            .then(response => response.json())
            .then(data => {
                console.log(data)
                alert("SAVED IT")
            })
            .catch(error => {
                console.error('Error',error)
                alert("THERE HAS BEEN AN ERROR")
            })
        })
        
}



const load_title_delete = function(){
    fetch('/api/flashcard_title')
        .then( response => response.json())
        .then( data =>{
            const list  = document.getElementById("del_sets")
            list.innerHTML = ''

            data.forEach(card =>{
                const listItem = document.createElement("li")
                
                const deleteItem = document.createElement("button")
                
                if (card==="Login to create sets"){
                    const link = document.createElement("a")
                    link.textContent = card
                    link.href="/login"
                    listItem.appendChild(link)

                }else if(card==="Create sets to begin practicing!"){
                    const link = document.createElement("a")
                    link.textContent=card
                    link.href="/create"
                    listItem.appendChild(link)
                }else{
                    listItem.textContent = card
                    deleteItem.textContent = "🗑️Delete"
                    deleteItem.classList.add("delete-button")
                    listItem.appendChild(deleteItem)

                    deleteItem.addEventListener("click",function(){
                        if (!confirm("Are you sure you want to delete this set")) return;
                        let delObj = {title: card}
                        fetch('/delete_flashcards',{
                            method: 'POST',
                            headers: {
                                'Content-type': 'application/json'
                            },
                            body: JSON.stringify(delObj)
                        })
                        .then (response => response.json())
                        .then (data =>{
                            if (data.status==="success"){
                                alert("set deleted")
                                load_title_delete()
                            }
                        })
                        .catch(error =>{
                            console.log(error)
                            alert("an error occured")
                        })

                    })
                }
                
                
                list.appendChild(listItem)
        })
    })
}
if (window.location.pathname === "/delete"){
    document.addEventListener('DOMContentLoaded',load_title_delete)
}



// feedback code
const feedbackButton = document.getElementById("feedback-button")
if (feedbackButton){
    feedbackButton.addEventListener("click",function(){
        const feedbackPanel = document.getElementById("feedback-panel")
        if (feedbackPanel.style.display==="block"){
            feedbackPanel.style.display="none"
        }else{
            feedbackPanel.style.display="block"
            feedbackButton.innerText="Close"
            const messageBox = document.getElementById("feedback-input")
            
            const submit = document.getElementById("submit-button")
            submit.addEventListener("click",function(){
                const message = messageBox.value.trim()
                if (message !== ""){
                    const feedback = {feedback:message}
                    fetch('/api/feedback',{
                        method:'POST',
                        headers:{
                            'Content-type':'application/json'
                        },
                        body: JSON.stringify(feedback)
                    })
                    .then (response => response.json())
                    .then (data=> {
                        if (data.status === "success"){
                            alert("Feedback Noted. Thank you!")
                            messageBox.value=""
                            feedbackPanel.style.display="none"
                        }else{
                            alert("Issue saving Feedback. Make sure you're logged in.")
                        }
                    })
                    .catch(error =>{
                        console.log(error)
                    })
                    

                }else{
                    alert("please enter something before submitting.")
                }
            })
        }

    })
}

const enter_button_val = document.getElementById("auto-input-button")
if (enter_button_val){
    const input = document.getElementById("auto-input")
    enter_button_val.addEventListener("click",function(){
        if (enter_button_val !== ""){
            const inputText= input.value.trim()
            input.value=""
            const user_request = {question:inputText}
            fetch('/api/ai_flashcards',{
                method:'POST',
                headers:{
                    'Content-type':'application/json'
                },
                body:JSON.stringify(user_request)
            })
            .then (response=>response.json())
            .then (data =>{
                if (data.status === "success"){
                    // get cards created from backend
                    const questions = data.questions
                    const answers = data.answers
                    console.log(questions)
                    console.log(answers)
                    const questionWrapper = document.getElementById('question-wrapper')
                    const answerWrapper = document.getElementById('answer-wrapper')
                    

                    questions.forEach((item,index)=>{
                        const questionBox = document.createElement('div')
                        questionBox.className = 'box'
                        
                        const questionBoxText = document.createElement('p')
                        questionBoxText.textContent = `${index+1}. ${item}`
                        // add text to box
                        questionBox.appendChild(questionBoxText)
                        // add box to wrapper
                        questionWrapper.appendChild(questionBox)
                    })
                    answers.forEach((item,index)=>{
                        const answerBox = document.createElement('div')
                        answerBox.className = 'box'
                        
                        const answerBoxText = document.createElement('p')
                        answerBoxText.textContent = `${index+1}. ${item}`
                        // add text to box
                        answerBox.appendChild(answerBoxText)
                        

                        const delete_button = document.createElement('button')
                        delete_button.id = `delete-button-${index}`
                        delete_button.innerHTML="🗑️"

                        answerBox.appendChild(delete_button)
                        // add box to wrapper
                        
                        answerWrapper.appendChild(answerBox)

                        delete_button.addEventListener("click",function(){
                            answerBox.remove()
                            
                        console.log(`delete-${index+1}`)
                        })
                        
                    })

                    
                    const saveButton = document.createElement('button')
                    saveButton.innerText = "Save"

                    const pageWrapper = document.getElementById("page-wrapper")

                    pageWrapper.appendChild(saveButton)
                    saveButton.addEventListener("click",function(){
                        if (questions.length >= 1 && questions.length === answers.length){
                            let allCards = {title:answers.slice(0,1)[0],cards:[]}
                            
                            for (let i=0; i<questions.length;i++){
                                let card = {question:questions.slice(i,i+1)[0],answer:answers.slice(i,i+1)[0]}
                                allCards.cards.push(card)

                            }
                            console.log(allCards)

                            fetch('/add_set',{
                                method:'POST',
                                headers:{
                                    'Content-type':'application/json'
                                },
                                body: JSON.stringify(allCards)
                            })
                            .then(response => response.json())
                            .then (data => {
                                if (data.status === "success"){
                                    alert(data.message)
                                }else{
                                    alert(data.message)
                                }
                            })
                            .catch(error =>{
                                alert(error)
                            })

                        }
                    })      
                       

                }else{
                    alert(`${data.message}`)
                    console.log("error",data.message)
                }
            })
            .catch(error =>{
                alert(error)
            })
        }
        
        

    })
    
}