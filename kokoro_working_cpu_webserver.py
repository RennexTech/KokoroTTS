import io
import os
import re
import sys
import time
import unicodedata
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
import soundfile as sf
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel

# Try importing ONNX Runtime and Kokoro
try:
    import onnxruntime as ort
    from kokoro_onnx import Kokoro, EspeakConfig
except ImportError:
    print("Error: Required libraries not found. Run: pip install kokoro-onnx onnxruntime soundfile fastapi uvicorn")
    sys.exit(1)

# File Paths
ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "kokoro-v1.0.onnx"
VOICES_PATH = ROOT / "voices-v1.0.bin"

# Global Kokoro Engine Instance
kokoro_engine = None
active_provider = "CPU"

def init_engine():
    global kokoro_engine, active_provider
    if not MODEL_PATH.exists() or not VOICES_PATH.exists():
        print(f"[Warning] Missing model files at {MODEL_PATH} or {VOICES_PATH}.")
        return

    print(f"[System] Available ONNX Providers: {ort.get_available_providers()}")
    print("[Engine] Initializing Kokoro on CPU (Multi-threaded) for stable audio...")

    try:
        # 1. Setup Espeak Config for Windows
        espeak_config = EspeakConfig(
            lib_path=r"C:\Program Files\eSpeak NG\libespeak-ng.dll",
            data_path=r"C:\Program Files\eSpeak NG\espeak-ng-data"
        )

        # 2. Setup CPU Session Options
        sess_options = ort.SessionOptions()
        sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.intra_op_num_threads = max(1, os.cpu_count() or 1)

        # 3. Create Session
        session = ort.InferenceSession(
            str(MODEL_PATH),
            sess_options=sess_options,
            providers=["CPUExecutionProvider"]
        )
        
        # 4. Load Kokoro with Espeak Config
        if hasattr(Kokoro, "from_session"):
            try:
                # Try passing espeak_config
                kokoro_engine = Kokoro.from_session(session, str(VOICES_PATH), espeak_config=espeak_config)
            except TypeError:
                # Fallback if the installed version doesn't accept the kwarg
                print("[Warning] Kokoro.from_session does not accept espeak_config. Using default.")
                kokoro_engine = Kokoro.from_session(session, str(VOICES_PATH))
        else:
            kokoro_engine = Kokoro(str(MODEL_PATH), str(VOICES_PATH))
            
        active_provider = "CPU Execution (Stable)"
        print(f"[Engine] Successfully loaded on {active_provider}!")
    except Exception as e:
        print(f"[Engine] Failed loading: {e}")
        sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_engine()
    yield
    global kokoro_engine
    kokoro_engine = None

app = FastAPI(title="Kokoro TTS v4 Local Studio", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SynthesisRequest(BaseModel):
    text: str
    voice: str = "af_heart"
    speed: float = 1.0

def clean_input_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    return text.strip()

@app.get("/api/info")
def get_info():
    voices = sorted(kokoro_engine.get_voices()) if kokoro_engine else []
    return {
        "status": "ready" if kokoro_engine else "missing_models",
        "provider": active_provider,
        "voices": voices,
        "default_voice": "af_heart" if "af_heart" in voices else (voices[0] if voices else "")
    }

@app.post("/api/generate")
def generate_speech(req: SynthesisRequest):
    if not kokoro_engine:
        raise HTTPException(status_code=500, detail="Kokoro model files not loaded.")
    
    cleaned_text = clean_input_text(req.text)
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Text input is empty.")

    try:
        t0 = time.time()
        lang_code = "en-us"
        if req.voice.startswith("b"):
            lang_code = "en-gb"
        elif req.voice.startswith("f"):
            lang_code = "fr-fr"
        elif req.voice.startswith("e"):
            lang_code = "es"

        samples, sample_rate = kokoro_engine.create(
            cleaned_text,
            voice=req.voice,
            speed=req.speed,
            lang=lang_code
        )
        elapsed = time.time() - t0

        buffer = io.BytesIO()
        sf.write(buffer, samples, sample_rate, format="WAV", subtype="PCM_16")
        buffer.seek(0)

        return Response(
            content=buffer.read(),
            media_type="audio/wav",
            headers={
                "X-Synthesis-Time-Sec": f"{elapsed:.2f}",
                "X-Audio-Duration-Sec": f"{len(samples) / sample_rate:.2f}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis error: {str(e)}")

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    # (UI code stays exactly the same as your Gemini file)
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kokoro Studio v4</title>
    <style>
        :root {
            --bg: #121118;
            --surface: #1e1b26;
            --surface-hover: #2a2636;
            --border: #352f44;
            --accent: #8b5cf6;
            --accent-hover: #7c3aed;
            --text: #f3f4f6;
            --muted: #9ca3af;
            --success: #34d399;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg); color: var(--text); display: flex; justify-content: center; min-height: 100vh; padding: 2rem 1rem; }
        .container { width: 100%; max-width: 800px; display: flex; flex-direction: column; gap: 1.25rem; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 1rem; }
        h1 { font-size: 1.5rem; color: var(--accent); }
        .badge { background: var(--surface); border: 1px solid var(--border); padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.8rem; color: var(--muted); }
        .card { background: var(--surface); border: 1px solid var(--border); border-radius: 0.75rem; padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
        .controls-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        label { font-size: 0.85rem; color: var(--muted); margin-bottom: 0.4rem; display: block; }
        select, input[type="range"] { width: 100%; background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 0.6rem; border-radius: 0.5rem; outline: none; }
        textarea { width: 100%; height: 200px; background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 1rem; border-radius: 0.5rem; resize: vertical; font-size: 1rem; line-height: 1.5; outline: none; }
        textarea:focus { border-color: var(--accent); }
        .actions { display: flex; justify-content: space-between; align-items: center; }
        button { background: var(--accent); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 0.5rem; font-weight: 600; cursor: pointer; transition: background 0.2s; }
        button:hover { background: var(--accent-hover); }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .stats { font-size: 0.85rem; color: var(--muted); }
        audio { width: 100%; margin-top: 0.5rem; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Kokoro Studio v4</h1>
            <div id="providerBadge" class="badge">Loading Engine...</div>
        </header>

        <div class="card">
            <div class="controls-grid">
                <div>
                    <label for="voiceSelect">Voice</label>
                    <select id="voiceSelect"><option>Loading voices...</option></select>
                </div>
                <div>
                    <label for="speedInput">Speed (<span id="speedVal">1.0</span>x)</label>
                    <input type="range" id="speedInput" min="0.5" max="1.8" step="0.05" value="1.0">
                </div>
            </div>

            <div>
                <label for="textInput">Text Prompt</label>
                <textarea id="textInput" placeholder="Type or paste text here to synthesize speech..."></textarea>
            </div>

            <div class="actions">
                <div id="stats" class="stats">Ready</div>
                <button id="generateBtn" onclick="generateAudio()">Generate Speech</button>
            </div>
        </div>

        <div class="card" id="audioCard" style="display: none;">
            <label>Output Audio</label>
            <audio id="audioPlayer" controls></audio>
        </div>
    </div>

    <script>
        const speedInput = document.getElementById('speedInput');
        const speedVal = document.getElementById('speedVal');
        const voiceSelect = document.getElementById('voiceSelect');
        const textInput = document.getElementById('textInput');
        const generateBtn = document.getElementById('generateBtn');
        const stats = document.getElementById('stats');
        const providerBadge = document.getElementById('providerBadge');
        const audioCard = document.getElementById('audioCard');
        const audioPlayer = document.getElementById('audioPlayer');

        speedInput.addEventListener('input', (e) => speedVal.textContent = e.target.value);

        async function loadInfo() {
            try {
                const res = await fetch('/api/info');
                const data = await res.json();
                providerBadge.textContent = 'Engine: ' + data.provider;
                voiceSelect.innerHTML = '';
                data.voices.forEach(voice => {
                    const opt = document.createElement('option');
                    opt.value = voice;
                    opt.textContent = voice;
                    if (voice === data.default_voice) opt.selected = true;
                    voiceSelect.appendChild(opt);
                });
            } catch (e) {
                providerBadge.textContent = 'Engine Error';
                stats.textContent = 'Failed to connect to backend server.';
            }
        }

        async function generateAudio() {
            const text = textInput.value.trim();
            if (!text) return alert('Please enter some text.');

            generateBtn.disabled = true;
            stats.textContent = 'Synthesizing...';

            try {
                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: text,
                        voice: voiceSelect.value,
                        speed: parseFloat(speedInput.value)
                    })
                });

                if (!res.ok) throw new Error(await res.text());

                const blob = await res.blob();
                const audioUrl = URL.createObjectURL(blob);
                audioPlayer.src = audioUrl;
                audioCard.style.display = 'block';
                audioPlayer.play();

                const synthTime = res.headers.get('X-Synthesis-Time-Sec') || '?';
                const audioDur = res.headers.get('X-Audio-Duration-Sec') || '?';
                stats.textContent = `Generated ${audioDur}s audio in ${synthTime}s`;
            } catch (e) {
                stats.textContent = 'Generation failed.';
                alert('Error: ' + e.message);
            } finally {
                generateBtn.disabled = false;
            }
        }

        loadInfo();
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    # Find an open port starting from 8000
    port = 8000
    while port < 8020:
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
            break
        except OSError:
            print(f"[Server] Port {port} is busy, trying next...")
            port += 1

    print(f"[Server] Starting local server at http://127.0.0.1:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port)
