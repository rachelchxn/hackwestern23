const chat = (message) => {
    const url = "https://api.openai.com/v1/chat/completions"
    // get api key from .env file
    const key = 
        // process.env.OPENAI_API_KEY
        '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'
    const bearer = 'Bearer ' + key

    fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': bearer,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: "gpt-4",
            // prompt: prompt,
            messages: [
                {
                  "role": "user",
                  "content": message
                }
              ],
            temperature: 0.9,
            max_tokens: 256,
            top_p: 1,
            frequency_penalty: 0,
            presence_penalty: 0,
            stream: false,
        })

    })
    .then((response) => {return response.json()})
    .then((data)=>{
        // console.log(Object.keys(data))
        console.log(data)

        const message = data.choices[0].message.content
        console.log(message)
    })
    .catch(error => {
        console.log(error)
    })
}

export default chat;