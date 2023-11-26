import requests
import base64
import json
import pyaudio
import wave
import io
import threading

# Global variable to control the recording state
recording_active = True


def record_audio(sample_rate=48000, channels=1):
    global recording_active

    audio_format = pyaudio.paInt16
    chunk = 1024

    p = pyaudio.PyAudio()
    stream = p.open(format=audio_format, channels=channels,
                    rate=sample_rate, input=True, frames_per_buffer=chunk)

    print("Recording")

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
        return response.json()
    else:
        raise Exception(f"Error code {response.status_code}: {response.text}")


def stop_recording():
    global recording_active
    recording_active = False


# Usage example
if __name__ == "__main__":
    api_key = "AIzaSyBN197RE1Jgm3F_oQ8OkRIXg9RB6xPXL3g"
    transcription_thread = threading.Thread(
        target=lambda: print(json.dumps(transcribe(api_key), indent=2)))
    transcription_thread.start()

    # This is where you would implement your logic to determine when to stop recording
    # For now, let's assume you stop recording after some event or a set amount of time
    # For example, stop recording after 30 seconds (for demonstration)
    # You can replace this with any other condition
    import time
    time.sleep(10)
    stop_recording()
    transcription_thread.join()