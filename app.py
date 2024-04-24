'''
COMMANDS:
SPEECH:

FAN STATUS -> ON, OFF
FAN SPEED {0 - 5} -> fan speed [012345]

'''
#IMPORTS
from flask import Flask,render_template,request,jsonify
import cv2
from google.cloud import speech
import os
import io
from PIL import Image
import base64
import time
from dotenv import load_dotenv, dotenv_values
import google.generativeai as genai
from flask_cors import CORS


app = Flask(__name__,template_folder="./templates")
CORS(app)

generation_config = None
safety_settings = None
modelVision = None
modelText = None



#ENVIRONMENT VARIABLES
load_dotenv()
env_var = dotenv_values(".env")
geminiApiKey = env_var.get("GEMINI_API_KEY")


#GEMINI-SETUP
def setGemini():
    global generation_config,safety_settings, modelVision, modelText
    genai.configure(api_key=geminiApiKey)

    generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
    }

    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
    ]

    modelVision = genai.GenerativeModel(model_name="gemini-pro-vision",
                                generation_config=generation_config,
                                safety_settings=safety_settings)

    modelText = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                generation_config=generation_config,
                                safety_settings=safety_settings)
    

setGemini()

def sendVals(speed):
    # Define the value you want to write to the file
    value_to_write = str(speed)
    
    # Define the file path where you want to write the value
    file_path = "arduino_command.txt"
    
    # Check if the file exists, if not, create it
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write(value_to_write)
    else:
        # If the file exists, append the value to the end of the file
        with open(file_path, 'a') as file:
            file.write(value_to_write + '\n')
    
    # print(f"Value '{value_to_write}' written to {file_path}")

@app.route('/')
def process():
    return render_template("index.html")


@app.route('/predictimage', methods = ["POST"])
def process_image():
    
    if request.method == 'POST':
        data = request.json
        imgData = data.get("imageData","")

    decoded_image = io.BytesIO(base64.b64decode(imgData))
    img = Image.open(decoded_image)

    # imgPath = "./image.jpg"
    # img.save(imgPath)
    
    prompt = ['''how many fingers are being held up? Count based on total number of fingers fully stretched out. 
              If there are 0 fingers stretched out then 0, 1 finger out means 1, 2 fingers out means 2, 3 out means 3, 
              4 out means 4, 5 out means 5. If there are no hands in the image then 0.
              Give me the answer as a single number''',img]

    responseGen = modelVision.generate_content(prompt)
    # time.sleep(5)
    # os.remove('./image.jpg')
    value = responseGen.text
    sendVals(value)
    os.system('python fan.py')
    return jsonify({"repsonse":int(responseGen.text.lstrip().rstrip())}),200

    #here i will send the response to the arduino as a request and also try and render the response on the frontend
        
@app.route('/predictaudio',methods=['POST'])
def predict():
    if request.method == 'POST':
        data = request.json
        audioData = data.get("audioPath","")
        if audioData != "":
            pass
        else:
            return jsonify({"error:","Please enter valid audio"}),404

    return processSpeech(audioData)

def processSpeech(audioData):
    
    clientSpeech = speech.SpeechClient.from_service_account_file('key.json')
    inputAudio = audioData
    decoded_content = base64.b64decode(inputAudio)
    print(decoded_content)
    with open('./decodedAudio.webm','wb') as audioFile:
        audioFile.write(decoded_content)
    # with open(inputAudio,'rb') as file:
    #     data = file.read()
    os.system('ffmpeg -i ./decodedAudio.webm ./audio.mp3')
    with open('./audio.mp3','rb') as file:
        data = file.read()

    os.remove('./decodedAudio.webm')
    os.remove('./audio.mp3')
    
    audio_file = speech.RecognitionAudio(content=data)

    config_US = speech.RecognitionConfig(sample_rate_hertz=44100,
                                      enable_automatic_punctuation=True,
                                      language_code='en-US',
                                      profanity_filter=False)
    
    response_US = clientSpeech.recognize(config=config_US, audio=audio_file)

    config_UK = speech.RecognitionConfig(sample_rate_hertz=44100,
                                      enable_automatic_punctuation=True,
                                      language_code='en-UK',
                                      profanity_filter=False)
    
    response_UK = clientSpeech.recognize(config=config_UK, audio=audio_file)

    config_IN = speech.RecognitionConfig(sample_rate_hertz=44100,
                                      enable_automatic_punctuation=True,
                                      language_code='en-IN',
                                      profanity_filter=False)
    
    response_IN = clientSpeech.recognize(config=config_IN, audio=audio_file)

    transcript_US = response_US.results[0].alternatives[0].transcript if response_US.results else ""
    transcript_UK = response_UK.results[0].alternatives[0].transcript if response_UK.results else ""
    transcript_IN = response_IN.results[0].alternatives[0].transcript if response_IN.results else ""

    # Split transcripts into lists of words
    transcripts = [transcript_IN, transcript_US, transcript_UK]

    responseGen = modelText.generate_content(f''' {transcript_IN};{transcript_UK};{transcript_US}: which of these three sentences corresponds to a fan and its speed, if neither do then return -1,\
                                              else return the speed of the fan as a number.
                                             examples: 
                                             fan speed 1 : 1
                                             fan speed 2 : 2
                                             fan speed 3 : 3
                                             fan speed 4 : 4
                                             fan speed 5 : 5''')
    value = int(responseGen.text)
    print(value)
    sendVals(value)
    os.system('python fan.py')
    return jsonify({"response":int(responseGen.text),
                    "transcripts":transcripts}),200


    return transcripts

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")