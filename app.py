from flask import Flask, request, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import re

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key="AIzaSyBMYArSvQeZgtolFbQqJzfCCbvJhMl9JEA")

def get_video_transcription(video_url):
    try:
        # Extract video ID from URL
        video_id = video_url.split("v=")[-1].split("&")[0]
        
        # Get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Extract and clean text
        raw_text = " ".join([entry['text'] for entry in transcript])
        return clean_transcription(raw_text)
    except Exception as e:
        return f"Could not fetch transcript: {str(e)}"

def clean_transcription(transcription):
    # Remove extra spaces and newlines
    cleaned_text = re.sub(r'\s+', ' ', transcription).strip()
    return cleaned_text

def generate_linkedin_post(transcription):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
    I am a professional sharing insights on LinkedIn, and I want to craft a well-researched and engaging post based on the content of a YouTube video I watched.
    The post should not appear as if it was generated from a video or summarize it directly. Instead, it should reflect my own analysis, expertise, and takeaways in a professional tone.
    
    Ensure the post:
    - Sounds like I have researched and written it myself.
    - Is engaging and thought-provoking.
    - Uses a professional yet conversational tone.
    - Includes relevant insights and possibly additional perspectives.
    - Uses emojis where appropriate to enhance readability.
    
    Here is the core content I want to base my post on:
    {transcription}
    """
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else "Error generating post."
    except Exception as e:
        return f"Error generating post: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        transcription = get_video_transcription(video_url)
        linkedin_post = generate_linkedin_post(transcription)
        return render_template('index.html', transcription=transcription, linkedin_post=linkedin_post)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
