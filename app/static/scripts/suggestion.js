// Set up inputs
const ai_input = document.getElementById("ai-input");
const ai_output = document.getElementById("ai-output");
const ai_button = document.getElementById("ai-button");

// Call Gemini Endpoint
async function query_suggest(user_question) {
    try {
        if (user_question) {
            console.log("Calling AI...")
            const response = await fetch('api/query-suggestion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: user_question })
            });
            if (!response.ok) throw new Error(`AI Error: ${response.status}`);
            const response_data = await response.json();
            console.log(response_data)
            return response_data;
        } else {
            console.log("Empty question")
        }
    } catch (error) {
        return { "message": "We experienced an error, please try again." }
    }
}



// Output Response 
function output_response(response) {
    if (response.message) {
        ai_output.innerHTML = response.message;
    }
    
}

// Button
ai_button.addEventListener("click", async () => {
    const ai_response = await query_suggest(ai_input.value);
    output_response(ai_response)
})
