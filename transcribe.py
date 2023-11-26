import requests
import base64
import json
import pyaudio
import wave
import io
import threading
from openai import OpenAI
from dotenv import load_dotenv
import os

# Global variable to control the recording state
recording_active = True

def list_audio_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

    p.terminate()

def record_audio(sample_rate=48000, channels=1, device_index=1):
    global recording_actives

    audio_format = pyaudio.paInt16
    chunk = 1024

    p = pyaudio.PyAudio()
    stream = p.open(format=audio_format, channels=channels,
                    rate=sample_rate, input=True, frames_per_buffer=chunk, input_device_index=device_index)

    print("Recording...")

    frames = []
    while recording_active:
        data = stream.read(chunk)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    buffer = io.BytesIO()
    wf = wave.open(buffer, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(audio_format))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    buffer.seek(0)
    return buffer.read()


def transcribe(api_key, language_code="en-US"):
    url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}"
    audio_content = base64.b64encode(record_audio()).decode('UTF-8')

    # Prepare request payload
    data = {
        "config": {
            "encoding": "LINEAR16",
            "sampleRateHertz": 48000,
            "languageCode": language_code
        },
        "audio": {
            "content": audio_content
        }
    }

    # Send the POST request
    response = requests.post(url, json=data)

    if response.status_code == 200:
        response_data = response.json()
        transcript_parts = [result['alternatives'][0]['transcript']
                            for result in response_data['results']]
        return transcript_parts
    else:
        raise Exception(f"Error code {response.status_code}: {response.text}")


def stop_audio_recording():
    global recording_active
    recording_active = False

def start_audio_recording():
    global recording_active
    recording_active = True

# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

def summarize(dialogue):
    user = "Rachel"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": f'''Extract the name and key information about the person from this conversation dialogue:

        {dialogue}

        This is going to be displayed as a reminder to them about this person. Use this format and fill in the blanks, if name or location info is not available, assign it [Unknown].:
        Name: [insert name]
        Where they are: [insert location]
        Points:
        - [insert point 1]
        - [insert point 2]
        - [insert point 3]...
        '''
            },
            {
            "role": "user",
            "content": ""
            }
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response

# Usage example
if __name__ == "__main__":
    api_key = "AIzaSyBN197RE1Jgm3F_oQ8OkRIXg9RB6xPXL3g"
    transcript_parts = []

    list_audio_devices()

    def handle_transcription():
        global transcript_parts
        transcript_parts = transcribe(api_key)

    transcription_thread = threading.Thread(target=handle_transcription)
    transcription_thread.start()

    import time
    time.sleep(15)
    stop_recording()
    transcription_thread.join()
    full_transcript = "".join(transcript_parts)
    summary = summarize(full_transcript)
    print(full_transcript)
    print(summary)