# import streamlit as st 
# from dotenv import load_dotenv
# load_dotenv()
# import google.generativeai as genai
# import os
# from youtube_transcript_api import YouTubeTranscriptApi
# from generate_pdf import download_summary
# from translate import translate_text

# genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))

# prompt = """Youtube video summarizer. You will be  taking transcript text and summarizing the entire video and providing the important summary in points within 500 words"""

# ##getting transcript from YT videos
# def extract_transcript_details(youtube_video_url):
#     try:
#         video_id = youtube_video_url.split("=")[1]
#         transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        
#         transcript = ""
#         for i in transcript_text:
#             transcript += " " + i["text"]
#         return transcript

#     except Exception as e:
#         return str(e)

# #getting summary of the YT videos based on Prompt from Gemini Pro
# def generate_gemini_content(transcript_text, prompt):
#     #print(type(transcript_text))
#     model = genai.GenerativeModel("gemini-pro")
    
#     if isinstance(transcript_text, str):
#         response = model.generate_content(prompt + transcript_text)
#         return response.text
#     else:
#         return "Error: Transcript text is not a string."
#     # response = model.generate_content(prompt + transcript_text)
#     # return response.text

# st.title("Youtube Transcript to Detailed Notes Converter")
# youtube_link = st.text_input("Enter Youtube Video Link :")

# if youtube_link:
#     video_id = youtube_link.split("=")[1]
#     print(video_id)
#     # st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width = True)

#     dest_language = st.selectbox("Select the language for translation:", ["en","es", "fr", "de", "zh"], index=0)

# if st.button("Get Detailed Notes : "):
#     transcript_text = extract_transcript_details(youtube_link)
    
#     if transcript_text:
#         summary = generate_gemini_content(transcript_text, prompt)
#         st.markdown("## Detailed Notes : ")
#         st.write(summary)
        
#         translated_summary = translate_text(summary, dest_language)
#         st.markdown(f"## Translated Notes ({dest_language}):")
#         st.write(translated_summary)
        
#         pdf_file_path = download_summary(summary)
#         with open(pdf_file_path, "rb") as pdf_file:
#                 btn = st.download_button(
#                 label = "Download Summary as PDF",
#                 data = pdf_file,
#                 file_name = "summary.pdf",
#                 mime = "application/pdf"
#             )
            
#         if btn:
#             st.success("Summary downloaded as summary.pdf")
#             st.info("Check your browser's download bar to access the file and click 'Show in folder' to locate it.")
#     else:
#         st.error("Failed to extract transcript. Please check the video URL or try again.")

# from dotenv import load_dotenv
# import os

# load_dotenv()
# api_key = os.getenv("GOOGLE_API_KEY")
# print(f"Loaded API Key: {api_key}")  # Ensure this prints your actual API key

#translated_summary = translate_text("Hello",'es')

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
import tempfile
from translatepy import Translator

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt for Gemini AI
prompt = """Youtube video summarizer. You will be taking transcript text and summarizing the entire video and providing the important summary in points within 200 words."""

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        
        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]
        return transcript

    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return None

def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    
    if isinstance(transcript_text, str):
        try:
            response = model.generate_content(prompt + transcript_text)
            return response.text
        except Exception as e:
            st.error(f"Error generating content with Gemini AI: {e}")
            return "Error generating summary."
    else:
        return "Error: Transcript text is not a string."

def download_summary(summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)  # Adding the Unicode font
    pdf.set_font('DejaVu', size=12)
    pdf.multi_cell(0, 10, summary)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_file_path = temp_file.name
    pdf.output(pdf_file_path)
    temp_file.close()
    
    return pdf_file_path

def translate_text(text, dest_language):
    translator = Translator()
    translation = translator.translate(text, dest_language)
    return str(translation)  # Convert the translation result to string

# Streamlit Application
st.title("Youtube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter Youtube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[1]

    if 'transcript' not in st.session_state:
        st.session_state.transcript = extract_transcript_details(youtube_link)
    
    if st.session_state.transcript:
        st.write("Transcript extracted successfully.")
        if 'summary' not in st.session_state:
            st.session_state.summary = generate_gemini_content(st.session_state.transcript, prompt)
        
        st.markdown("## Detailed Notes:")
        st.write(st.session_state.summary)
        
        languages = {'Select Language': None, 'Spanish': 'es', 'French': 'fr', 'German': 'de', 'Chinese': 'zh', 'Kannada': 'kn','english' : 'en'}
        selected_language = st.selectbox("Select language for translation:", list(languages.keys()), key="language")

        if selected_language != 'Select Language':
            dest_language = languages[selected_language]
            try:
                if 'translated_summary' not in st.session_state or st.session_state.get('selected_language') != selected_language:
                    st.session_state.translated_summary = translate_text(st.session_state.summary, dest_language)
                    st.session_state.selected_language = selected_language

                st.markdown(f"## Translated Notes ({selected_language}):")
                st.write(st.session_state.translated_summary)

                pdf_file_path = download_summary(st.session_state.translated_summary)
                with open(pdf_file_path, "rb") as pdf_file:
                    btn = st.download_button(
                        label="Download Translated Summary as PDF",
                        data=pdf_file,
                        file_name="translated_summary.pdf",
                        mime="application/pdf"
                    )
                    if btn:
                        st.success("Translated summary downloaded as translated_summary.pdf")
                        st.info("Check your browser's download bar to access the file and click 'Show in folder' to locate it.")
            except ValueError as ve:
                st.error(f"Translation error: {ve}")
            except Exception as e:
                st.error(f"An error occurred during translation: {e}")
    else:
        st.error("Failed to extract transcript. Please check the video URL or try again.")

# import streamlit as st
# from langdetect import detect
# from google_trans_new import google_translator  # Google Translate library
# from youtube_transcript_api import YouTubeTranscriptApi
# from fpdf import FPDF
# import tempfile
# import os

# prompt = "Youtube video summarizer. You will be taking transcript text and summarizing the entire video and providing the important summary in points within 200 words."

# # Load environment variables if needed
# # from dotenv import load_dotenv
# # load_dotenv()

# # Configure Google Generative AI (Gemini AI) if needed
# # import google.generativeai as genai
# # genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# # Prompt for Gemini AI if needed
# # prompt = """Youtube video summarizer. You will be taking transcript text and summarizing the entire video and providing the important summary in points within 200 words."""

# def extract_transcript_details(youtube_video_url, language_code):
#     try:
#         video_id = youtube_video_url.split("=")[1]
#         transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code, 'en'])
        
#         transcript = ""
#         for i in transcript_text:
#             transcript += " " + i["text"]

#         return transcript, language_code

#     except Exception as e:
#         st.error(f"Error extracting transcript: {e}")
#         return None, None



# def generate_gemini_content(transcript_text, prompt):
#     # Generate content using Gemini AI
#     # model = genai.GenerativeModel("gemini-pro")
    
#     # Placeholder for Gemini AI content generation
#     # response = model.generate_content(prompt + transcript_text)
#     # return response.text

#     # For demonstration purposes, return a simple summary based on the transcript text
#     return "Placeholder summary generated based on transcript."

# def translate_text(text, dest_language):
#     translator = google_translator()  # Initialize Google Translator
#     translation = translator.translate(text, lang_tgt=dest_language)
#     return translation

# def download_summary(summary):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)  # Adding the Unicode font
#     pdf.set_font('DejaVu', size=12)
#     pdf.multi_cell(0, 10, summary)
    
#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
#     pdf_file_path = temp_file.name
#     pdf.output(pdf_file_path)
#     temp_file.close()
    
#     return pdf_file_path

# # Streamlit Application
# st.title("Multilingual Youtube Transcript Summarizer")
# youtube_link = st.text_input("Enter Youtube Video Link:")

# if youtube_link:
#     video_id = youtube_link.split("=")[1]

#     # if 'transcript' not in st.session_state:
#     #     st.session_state.transcript, st.session_state.detected_lang = extract_transcript_details(youtube_link)
    
#     if 'transcript' not in st.session_state:
#         st.session_state.transcript, st.session_state.detected_lang = extract_transcript_details(youtube_link, 'kn')  # 'kn' for Kannada

    
#     if st.session_state.transcript:
#         st.write(f"Transcript detected in {st.session_state.detected_lang}")
        
#         # Generate summary based on the original transcript
#         st.markdown("## Original Transcript:")
#         st.write(st.session_state.transcript)

#         if 'summary' not in st.session_state:
#             st.session_state.summary = generate_gemini_content(st.session_state.transcript, prompt)
        
#         st.markdown("## Summary:")
#         st.write(st.session_state.summary)
        
#         # Language selection for translation
#         languages = {'Select Language': None, 'Spanish': 'es', 'French': 'fr', 'German': 'de', 'Chinese': 'zh', 'Kannada': 'kn'}
#         selected_language = st.selectbox("Select language for translation:", list(languages.keys()))

#         if selected_language != 'Select Language':
#             dest_language = languages[selected_language]
#             try:
#                 if 'translated_summary' not in st.session_state or st.session_state.get('selected_language') != selected_language:
#                     st.session_state.translated_summary = translate_text(st.session_state.summary, dest_language)
#                     st.session_state.selected_language = selected_language

#                 st.markdown(f"## Translated Summary ({selected_language}):")
#                 st.write(st.session_state.translated_summary)

#                 pdf_file_path = download_summary(st.session_state.translated_summary)
#                 with open(pdf_file_path, "rb") as pdf_file:
#                     btn = st.download_button(
#                         label="Download Translated Summary as PDF",
#                         data=pdf_file,
#                         file_name="translated_summary.pdf",
#                         mime="application/pdf"
#                     )
#                     if btn:
#                         st.success("Translated summary downloaded as translated_summary.pdf")
#                         st.info("Check your browser's download bar to access the file and click 'Show in folder' to locate it.")
#             except ValueError as ve:
#                 st.error(f"Translation error: {ve}")
#             except Exception as e:
#                 st.error(f"An error occurred during translation: {e}")
#     else:
#         st.error("Failed to extract transcript. Please check the video URL or try again.")

















        


