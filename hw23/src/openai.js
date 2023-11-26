const key = "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"

const chatString = async (message) => {
    let response = 'dne'
    const url = "https://api.openai.com/v1/chat/completions"
    // get api key from .env file
    const bearer = 'Bearer ' + key

    await fetch(url, {
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

        response = data.choices[0].message.content
    })
    .catch(error => {
        console.log(error)
    })
    return response
}

const chatVision = async (message, imageURLs = []) => {
    let response = 'dne'

    const url = "https://api.openai.com/v1/chat/completions"
    // get api key from .env file
    const bearer = 'Bearer ' + key

    const content = [
        {"type": "text", "text": message},
    ]

    imageURLs.forEach((imageURL) => {
        content.push({
            "type": "image_url",
            "image_url": imageURL,
        })
    })

    await fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': bearer,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model:"gpt-4-vision-preview",
            messages:[
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens:300,
        })

    })
    .then((response) => {return response.json()})
    .then((data)=>{
        // console.log(Object.keys(data))
        // console.log(data)

        response = data.choices[0].message.content
        // console.log(response)
    })
    .catch(error => {
        console.log(error)
    })

    return response
}

export {chatString, chatVision};