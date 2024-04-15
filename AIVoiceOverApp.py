import streamlit as st
import sqlite3
from datetime import datetime
from styleTTS2_LJSpeech import tts_LJSpeech
from styleTTS2_LibriTTS import tts_LibriTTS
import os
from io import BytesIO

# Initialize the SQLite database
conn = sqlite3.connect('audio_database.db')
c = conn.cursor()

# Create the audio metadata table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS audio_metadata
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             text TEXT,
             method TEXT,
             speaker TEXT,
             wav_file TEXT,
             reference_audio TEXT,
             timestamp TEXT)''')
conn.commit()


def get_audio_list():
    c.execute("SELECT * FROM audio_metadata ORDER BY id DESC")
    return c.fetchall()

@st.cache_resource
def cached_tts_LJSpeech(text_input):
    return tts_LJSpeech(text_input)

@st.cache_resource
def cached_tts_LibriTTS(text_input, reference_audio):
    return tts_LibriTTS(text_input, reference_audio)

# Streamlit app
def main():
    st.title("Text-to-Speech Demo")

    # Left half of the page
    st.sidebar.header("Input")
    text_input = st.sidebar.text_area("Enter the text:")
    method_options = ["StyleTTS2-LibriTTS", "StyleTTS2-LJSpeech"]
    selected_method = st.sidebar.selectbox("Select the method:", method_options)

    if selected_method == "StyleTTS2-LJSpeech":
        speaker_options = ["Default"]
        selected_speaker = st.sidebar.selectbox("Select the speaker:", speaker_options)
    else:
        audio_option = st.sidebar.radio("Reference Audio Option", ["Default Speaker", "Upload Audio"])

        if audio_option == "Default Speaker":
            reference_audio = "Ref_audio/female_speaker_1.wav"
            st.sidebar.audio(reference_audio, format='audio/wav')
        else:
            uploaded_audio = st.sidebar.file_uploader("Upload reference audio", type=["wav"])
            if uploaded_audio is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                reference_audio = f"Ref_audio/uploaded_{timestamp}.wav"
                with open(reference_audio, "wb") as f:
                    f.write(uploaded_audio.getvalue())
            else:
                reference_audio = "Ref_audio/female_speaker_1.wav"

    if st.sidebar.button("Submit"):
        if text_input.strip() != "":
            # Call the cached text_to_speech function
            if selected_method == "StyleTTS2-LJSpeech":
                wav_file = cached_tts_LJSpeech(text_input)
                reference_audio = "N/A"
            else:
                wav_file = cached_tts_LibriTTS(text_input, reference_audio)

            # Save the audio metadata to the database
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO audio_metadata (text, method, speaker, wav_file, reference_audio, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                      (text_input, selected_method, selected_speaker if selected_method == "StyleTTS2-LJSpeech" else "N/A", wav_file, reference_audio, timestamp))
            conn.commit()

            st.sidebar.success("Audio generated successfully!")
        else:
            st.sidebar.warning("Please enter some text.")

    # Right half of the page
    st.header("Generated Audio List")

    # Retrieve the audio metadata from the database
    audio_list = get_audio_list()

    # Pagination
    items_per_page = 5
    total_pages = max(len(audio_list) // items_per_page + (1 if len(audio_list) % items_per_page > 0 else 0), 1)
    page_number = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
    start_index = (page_number - 1) * items_per_page
    end_index = start_index + items_per_page

    # Display the audio list for the current page
    for audio in audio_list[start_index:end_index]:
        audio_id, text, method, speaker, wav_file, reference_audio, timestamp = audio

        st.subheader(f"Audio ID: {audio_id}")
        st.write(f"Text: {text}")
        st.write(f"Method: {method}")
        st.write(f"Speaker: {speaker}")
        st.write(f"WAV File: {wav_file}")
        
        st.write(f"Timestamp: {timestamp}")

        # Display the playable audio
        audio_file = open(wav_file, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/wav')

        # Display the reference audio if available
        if reference_audio != "N/A":
            st.write(f"Reference Audio: {reference_audio}")
            ref_audio_file = open(reference_audio, 'rb')
            ref_audio_bytes = ref_audio_file.read()
            st.audio(ref_audio_bytes, format='audio/wav')

        st.divider()

if __name__ == '__main__':
    main()