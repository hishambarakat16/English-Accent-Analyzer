# app.py
import os
import tempfile
import uuid
from flask import Flask, request, jsonify, render_template, url_for
from werkzeug.utils import secure_filename
from accent_analyzer import download_video_audio, transcribe_audio, analyze_accent

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_change_in_production')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if the request contains a URL or a file upload
    if 'url' in request.form and request.form['url']:
        video_url = request.form['url']
        return process_url(video_url)
    elif 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        return process_file(file)
    else:
        return jsonify({'error': 'No URL or file provided'}), 400

def process_url(video_url):
    try:
        # Create a unique session ID
        session_id = str(uuid.uuid4())
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Set paths
        audio_path = os.path.join(temp_dir, "audio.wav")
        
        # Step 1: Download video and extract audio
        if not download_video_audio(video_url, audio_path):
            return jsonify({'error': 'Failed to download video. Please check the URL and try again.'}), 400
        
        # Step 2: Transcribe audio
        transcript, is_english, english_prob = transcribe_audio(audio_path)
        
        if not is_english and english_prob < 0.5:
            return jsonify({
                'error': 'The speech is likely not in English',
                'english_confidence': f"{english_prob*100:.2f}%"
            }), 400
        
        # Step 3: Analyze accent
        accent, confidence, top_accents = analyze_accent(transcript)
        
        # Step 4: Return results
        result = {
            'accent': accent,
            'confidence': f"{confidence:.2f}%",
            'english_confidence': f"{english_prob*100:.2f}%",
            'top_accents': [{'accent': acc, 'confidence': f"{conf:.2f}%"} for acc, conf in top_accents],
            'transcript_sample': transcript[:300] + ('...' if len(transcript) > 300 else '')
        }
        
        # Clean up temporary files
        try:
            os.remove(audio_path)
            os.rmdir(temp_dir)
        except:
            pass  # Ignore cleanup errors
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_file(file):
    try:
        # Create a unique session ID
        session_id = str(uuid.uuid4())
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Set paths
        video_path = os.path.join(temp_dir, secure_filename(file.filename))
        audio_path = os.path.join(temp_dir, "audio.wav")
        
        # Save the uploaded file
        file.save(video_path)
        
        # Extract audio using ffmpeg
        import subprocess
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",  # No video
            "-acodec", "pcm_s16le",  # PCM 16-bit little-endian
            "-ar", "16000",  # 16kHz sample rate
            "-ac", "1",  # Mono
            audio_path
        ]
        subprocess.run(cmd, check=True)
        
        # Step 2: Transcribe audio
        transcript, is_english, english_prob = transcribe_audio(audio_path)
        
        if not is_english and english_prob < 0.5:
            return jsonify({
                'error': 'The speech is likely not in English',
                'english_confidence': f"{english_prob*100:.2f}%"
            }), 400
        
        # Step 3: Analyze accent
        accent, confidence, top_accents = analyze_accent(transcript)
        
        # Step 4: Return results
        result = {
            'accent': accent,
            'confidence': f"{confidence:.2f}%",
            'english_confidence': f"{english_prob*100:.2f}%",
            'top_accents': [{'accent': acc, 'confidence': f"{conf:.2f}%"} for acc, conf in top_accents],
            'transcript_sample': transcript[:300] + ('...' if len(transcript) > 300 else '')
        }
        
        # Clean up temporary files
        try:
            os.remove(video_path)
            os.remove(audio_path)
            os.rmdir(temp_dir)
        except:
            pass  # Ignore cleanup errors
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
