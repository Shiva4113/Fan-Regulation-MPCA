'''
COMMANDS:
SPEECH:

FAN STATUS -> ON, OFF
FAN SPEED {0 - 5} -> fan speed [012345]

'''
from flask import Flask
import cv2
from google.cloud import speech



app = Flask(__name__)

@app.route('/')
def process():
    
    return processSpeech()


@app.route('/predict')
def predict():
    #this will call processSpeech/Image() based on image or speech
    api_url = "something"
    #here i will either capture image or detect speech

def processImage():
    #i will send prompt and receive response  -> train a model, pickle load the model.pkl
    pass
'''
def processSpeech():
    final = ""

    clientSpeech = speech.SpeechClient.from_service_account_file('key.json')

    numbers_file  = "./sample/speed_1.mp3"
    
    with open(numbers_file,'rb') as file:
        data = file.read()
    
    audio_file = speech.RecognitionAudio(content =data)

    config = speech.RecognitionConfig(sample_rate_hertz = 44100,
                                     enable_automatic_punctuation = True,
                                     language_code = 'en-US',
                                     profanity_filter=False)
    
    response_US  = clientSpeech.recognize(config = config,audio=audio_file)
    
    config = speech.RecognitionConfig(sample_rate_hertz = 44100,
                                     enable_automatic_punctuation = True,
                                     language_code = 'en-UK',
                                     profanity_filter=False)
    
    response_UK = clientSpeech.recognize(config=config,audio=audio_file)

    config = speech.RecognitionConfig(sample_rate_hertz = 44100,
                                     enable_automatic_punctuation = True,
                                     language_code = 'en-IN',
                                     profanity_filter=False)
    
    response_IN = clientSpeech.recognize(config=config,audio=audio_file)

    for res in response_IN.results:
        res+=res.alternatives[0].transcript

    cmd = getCommand(response_UK,response_US,response_IN)

    return cmd

def getCommand(final1,final2,final3):
    final1 = list(final1.split())
    final2 = list(final2.split())
    final3 = list(final3.split())
    speed = None
    
    msg1= cmdHelper(final1)
    msg2= cmdHelper(final2)
    msg3= cmdHelper(final3)
    
    return list(msg1,msg2,msg3)

def cmdHelper(final):
    msg = []
    for i in msg:
        if i.upper() in ["FAN", "STATUS", "SPEED", "ON", "OFF"]:
            msg.append(i)
        elif i.isnumeric():
            speed = int(i)
            msg.append(speed)

    return msg
'''

def processSpeech():
    clientSpeech = speech.SpeechClient.from_service_account_file('key.json')
    numbers_file = "./sample/ljiv5.mp3"
    
    with open(numbers_file,'rb') as file:
        data = file.read()
    
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
    transcripts = [transcript_IN.split(), transcript_US.split(), transcript_UK.split()]

    command = getCmd(transcripts)
    
    return command

    # return transcripts

def getCmd(transcripts):
    nums = {"ONE":"1","TWO":"2","THREE":"3","FOUR":"4","FIVE":"5","ON":"on","OFF":"off"}
    filtered_transcripts = list(filter(lambda i: len(i) == 3, transcripts))
    # filtered_transcripts = list(filter(lambda i: i[0].upper() == 'FAN', filtered_transcripts)) does not detect the word fan for multiple audio so i ignored this
    filtered_transcripts = list(filter(lambda i: (i[1].upper() == 'STATUS') or (i[1].upper() == 'SPEED' and (i[2].isnumeric() or i[2].upper() in ["ZERO","ONE","TWO","THREE","FOUR","FIVE"])), filtered_transcripts))
    
    # return filtered_transcripts

    if len(filtered_transcripts[0]) == 3:
        if filtered_transcripts[0][0].upper()!="FAN":
            filtered_transcripts[0][0] = "fan"#for generation of the command
        if filtered_transcripts[0][1].upper() == "SPEED":
            if filtered_transcripts[0][2].isdigit():
                return filtered_transcripts[0]
            else:
                filtered_transcripts[0][2] = nums[filtered_transcripts[0][2].upper()]
                return filtered_transcripts[0]
        elif filtered_transcripts[0][1].upper() == "STATUS":
                return filtered_transcripts[0][:2]
    return []

if __name__ == "__main__":
    app.run(debug=True)