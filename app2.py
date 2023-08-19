from flask import Flask ,request ,jsonify ,render_template

import openai

import os

app=Flask(__name__)

#set your ai api key

openai.api_key ='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'

#define the api endpoint for receiving user input  and generating responses

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input =request.json['message']
    
    #send user input to chat gpt api
    response =openai.Completion.create(
        engine= 'text-davinci-003',
        prompt=user_input,
        max_token =4030,
        n=1,
        stop=None,
        temperature=0.7
    )
    
    #extract the generated responses from responses
    reply =response.choices[0].text.strip()
    
    return jsonify({'reply': reply})


@app.route('/')
def index():
    return render_template('index.html')


if __name__=='__main__':
    app.run()