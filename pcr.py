import streamlit as st
import speech_recognition as sr
from assemblyai import AssemblyAIError
from deepgram import Deepgram
import requests
import whisper
import wave


def save_audio_to_file(audio_data, filename="temp_audio.wav"):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(audio_data.sample_width)
        wf.setframerate(audio_data.sample_rate)
        wf.writeframes(audio_data.get_raw_data())
    return filename

def whisper_transcribe(filename):
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    return result ["Transcription reussie"]

def deepgram_transcribe(filename):
    deepgram = Deepgram('Your DEEPGRAM_API_KEY')
    response = deepgram.transcription.pre_recorded(filename, {'punctuate': True})
    return response['channel']['alternatives'][0]['transcript']


def assemblyai_transcribe(audio_data):
    headers = {
        'authorization': 'YOUR_ASSEMBLYAI_API_KEY',
        'content-type': 'application/json'
    }

    response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=audio_data.get_raw_data())
    audio_url = response.json()['upload_url']

    transcript_request = {'audio_url': audio_url}
    transcript_response = requests.post('https://api.assemblyai.com/v2/transcript', json=transcript_request,
                                        headers=headers)

    transcript_id = transcript_response.json()['id']

    while True:
        result_response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
        if result_response.json()['status'] == 'completed':
            return result_response.json()['text']
        elif result_response.json()['status'] == 'failed':
            return "Transcription échouée."

def transcribe_speech(api_choice,language) :

    r = sr.Recognizer()
    with sr.Microphone() as source :

        st.info("Speak Now...")
        audio_text = r.listen(source)
        st.info("Transcription...")

        try :
            if api_choice == "Google":
                text = r.recognize_google(audio_text,language = language)

            elif api_choice == "Whisper":
                audio_data = sr.AudioData(audio_text.get_raw_data(),
                                          audio_text.sample_rate, audio_text.sample_width)
                text = whisper_transcribe(audio_data)

            elif api_choice == "Deepgram":
                audio_data = sr.AudioData(audio_text.get_raw_data(),
                                          audio_text.sample_rate, audio_text.sample_width)
                text = Deepgram(audio_data)

            elif api_choice == "AssemblyAI":
                audio_data = sr.AudioData(audio_text.get_raw_data(),
                                          audio_text.sample_rate, audio_text.sample_width)
                text = AssemblyAIError(audio_data)
            else :
                return "API not supported."

            return text
        except sr.UnknownValueError:
            return "Sorry, I don't Understand."

        except sr.RequestError as e:
            return f"Service error: {e}. Please check your connection or API key."

def save_transcription(text):

    with open("transcription.txt", "w",encoding="utf-8") as f:
        f.write(text)

def main() :

    st.title("Speech Recognition App")
    st.write("Click on the microphone to start speaking:")

    api_choice = st.selectbox("Choose Speech Recognition API:",
                              ["Google", "Whisper","Deepgram","AssemblyAI"])
    language = st.selectbox("Choose language:", ["fr-FR", "en-US"])

    if st.button("Start Recording"):
        text = transcribe_speech(api_choice, language)
        st.write("Transcription : " , text)

        if st.button("Save transcription"):
            save_transcription(text)
            st.success("save transcription in transcription.txt")

if __name__ == "__main__" :
    main()