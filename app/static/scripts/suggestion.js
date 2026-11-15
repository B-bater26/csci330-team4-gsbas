// Set up inputs
let ai_input = document.getElementById("ai-input");
let ai_output = document.getElementById("ai-output");
let ai_button = document.getElementById("ai-button");

// Set up AI Input Area
let ai_area = [ai_input, ai_output, ai_button];
let ai_open_button = document.getElementById("ai-icon");
let opened_ai = false;
ai_open_button.addEventListener("click", async () => {
    if (opened_ai) {
        opened_ai = false;
        ai_area.forEach(item => {
            item.style.display = "none";
        })
    } else {
        opened_ai = true;
        ai_area.forEach(item => {
            item.style.display = "block";
        })
    }
})

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
    checkbox_ai(ai_response);
    output_response(ai_response);

})

// Check the Boxes
function checkbox_ai(response) {
    if (response.codes && !response.codes.includes("-111222333")) {
        const checked_boxes = [];
        for (const checkbox of document.querySelectorAll(".check")) {
            if (checkbox.value.split(",").some(b_code => response.codes.includes(b_code))) {
                checkbox.checked = true;
                checked_boxes.push(checkbox)
            } else {
                checkbox.checked = false;
            }
        }
    }

}
