import requests
import base64
import json

import pyaudio
import wave
import io

def record_audio(duration=5, sample_rate=48000, channels=1):
    audio_format = pyaudio.paInt16
    chunk = 1024

    p = pyaudio.PyAudio()

    stream = p.open(format=audio_format, channels=channels,
                    rate=sample_rate, input=True,
                    frames_per_buffer=chunk)

    print("Recording...")

    frames = []

    for _ in range(0, int(sample_rate / chunk * duration)):
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
            "sampleRateHertz": 48000,  # Match this with your audio file's sample rate
            "languageCode": language_code
        },
        "audio": {
            "content": audio_content
        }
    }

    # Send the POST request
    response = requests.post(url, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error code {response.status_code}: {response.text}")

# Usage example
api_key = "AIzaSyBN197RE1Jgm3F_oQ8OkRIXg9RB6xPXL3g"
# audio_file_path = "test.wav"
response = transcribe(api_key)
print(json.dumps(response, indent=2))