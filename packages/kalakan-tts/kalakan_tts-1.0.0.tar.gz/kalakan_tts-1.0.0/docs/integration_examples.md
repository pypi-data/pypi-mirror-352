# Kalakan TTS Integration Examples

This document provides examples of how to integrate the Kalakan TTS system for Twi language into various applications and frameworks. These examples will help developers quickly implement Twi speech synthesis in their projects.

## Table of Contents

1. [Python Applications](#python-applications)
2. [Web Applications](#web-applications)
3. [Mobile Applications](#mobile-applications)
4. [Desktop Applications](#desktop-applications)
5. [Command Line Tools](#command-line-tools)
6. [Cloud Services](#cloud-services)

## Python Applications

### Basic Usage

```python
from kalakan_twi_tts import TwiSynthesizer

# Initialize the synthesizer
synthesizer = TwiSynthesizer()

# Generate speech from Twi text
audio = synthesizer.synthesize("Akwaaba! Wo ho te sɛn?")

# Save the audio to a file
synthesizer.save_audio(audio, "output.wav")

# Play the audio
synthesizer.play_audio(audio)
```

### Async Usage

```python
import asyncio
from kalakan_twi_tts import AsyncTwiSynthesizer

async def generate_speech():
    # Initialize the async synthesizer
    synthesizer = AsyncTwiSynthesizer()
    
    # Generate speech asynchronously
    audio = await synthesizer.synthesize("Akwaaba! Wo ho te sɛn?")
    
    # Save the audio to a file
    await synthesizer.save_audio(audio, "output.wav")
    
    return audio

# Run the async function
audio = asyncio.run(generate_speech())
```

### Batch Processing

```python
from kalakan_twi_tts import TwiSynthesizer

def batch_synthesize(texts, output_dir):
    synthesizer = TwiSynthesizer()
    
    for i, text in enumerate(texts):
        # Generate speech
        audio = synthesizer.synthesize(text)
        
        # Save to file
        output_path = f"{output_dir}/output_{i:04d}.wav"
        synthesizer.save_audio(audio, output_path)
        
        print(f"Generated {output_path}")

# Example usage
texts = [
    "Akwaaba! Wo ho te sɛn?",
    "Me din de Kofi.",
    "Ɛte sɛn?",
    "Meda wo ase.",
]

batch_synthesize(texts, "output_directory")
```

## Web Applications

### Flask Application

```python
from flask import Flask, request, send_file, render_template
from kalakan_twi_tts import TwiSynthesizer
import io
import os

app = Flask(__name__)
synthesizer = TwiSynthesizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/synthesize', methods=['POST'])
def synthesize():
    # Get text from request
    text = request.form.get('text', '')
    
    if not text:
        return {"error": "No text provided"}, 400
    
    # Generate speech
    audio = synthesizer.synthesize(text)
    
    # Save to in-memory file
    buffer = io.BytesIO()
    synthesizer.save_audio(audio, buffer)
    buffer.seek(0)
    
    # Return audio file
    return send_file(
        buffer,
        mimetype="audio/wav",
        as_attachment=True,
        attachment_filename="speech.wav"
    )

if __name__ == '__main__':
    app.run(debug=True)
```

HTML template (`templates/index.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <title>Twi TTS Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        textarea {
            width: 100%;
            height: 100px;
            margin-bottom: 10px;
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        #audioContainer {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Twi Text-to-Speech Demo</h1>
    
    <form id="ttsForm">
        <textarea id="textInput" placeholder="Enter Twi text here...">Akwaaba! Wo ho te sɛn?</textarea>
        <button type="submit">Generate Speech</button>
    </form>
    
    <div id="audioContainer"></div>
    
    <script>
        document.getElementById('ttsForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const text = document.getElementById('textInput').value;
            const formData = new FormData();
            formData.append('text', text);
            
            try {
                const response = await fetch('/synthesize', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('Failed to generate speech');
                }
                
                const blob = await response.blob();
                const audioUrl = URL.createObjectURL(blob);
                
                const audioContainer = document.getElementById('audioContainer');
                audioContainer.innerHTML = `
                    <h3>Generated Speech:</h3>
                    <audio controls src="${audioUrl}"></audio>
                    <p><a href="${audioUrl}" download="speech.wav">Download audio</a></p>
                `;
            } catch (error) {
                console.error('Error:', error);
                alert('Error generating speech: ' + error.message);
            }
        });
    </script>
</body>
</html>
```

### Django Application

```python
# views.py
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import io
from kalakan_twi_tts import TwiSynthesizer

synthesizer = TwiSynthesizer()

def index(request):
    return render(request, 'tts/index.html')

@csrf_exempt
def synthesize(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    text = request.POST.get('text', '')
    
    if not text:
        return JsonResponse({'error': 'No text provided'}, status=400)
    
    # Generate speech
    audio = synthesizer.synthesize(text)
    
    # Save to in-memory file
    buffer = io.BytesIO()
    synthesizer.save_audio(audio, buffer)
    buffer.seek(0)
    
    # Return audio file
    response = HttpResponse(buffer, content_type='audio/wav')
    response['Content-Disposition'] = 'attachment; filename="speech.wav"'
    
    return response
```

### React Integration

```jsx
import React, { useState } from 'react';
import axios from 'axios';

function TwiTTS() {
  const [text, setText] = useState('Akwaaba! Wo ho te sɛn?');
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('text', text);
      
      const response = await axios.post('/api/synthesize', formData, {
        responseType: 'blob',
      });
      
      const url = URL.createObjectURL(response.data);
      setAudioUrl(url);
    } catch (err) {
      setError('Failed to generate speech. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tts-container">
      <h1>Twi Text-to-Speech</h1>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="text-input">Enter Twi text:</label>
          <textarea
            id="text-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={4}
            className="form-control"
          />
        </div>
        
        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={loading || !text}
        >
          {loading ? 'Generating...' : 'Generate Speech'}
        </button>
      </form>
      
      {error && <div className="alert alert-danger mt-3">{error}</div>}
      
      {audioUrl && (
        <div className="audio-container mt-4">
          <h3>Generated Speech:</h3>
          <audio controls src={audioUrl} className="w-100" />
          <a 
            href={audioUrl} 
            download="twi-speech.wav"
            className="btn btn-secondary mt-2"
          >
            Download Audio
          </a>
        </div>
      )}
    </div>
  );
}

export default TwiTTS;
```

## Mobile Applications

### Android Integration (Kotlin)

```kotlin
// TwiTTSManager.kt
import android.content.Context
import android.media.MediaPlayer
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import java.io.File
import java.io.IOException

class TwiTTSManager(private val context: Context) {
    private val client = OkHttpClient()
    private val mediaPlayer = MediaPlayer()
    private val apiUrl = "https://your-tts-api.com/synthesize"
    
    suspend fun synthesize(text: String): File? = withContext(Dispatchers.IO) {
        try {
            // Create request body
            val requestBody = FormBody.Builder()
                .add("text", text)
                .build()
            
            // Create request
            val request = Request.Builder()
                .url(apiUrl)
                .post(requestBody)
                .build()
            
            // Execute request
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    Log.e("TwiTTS", "API call failed: ${response.code}")
                    return@withContext null
                }
                
                // Save audio to file
                val audioFile = File(context.cacheDir, "twi_speech_${System.currentTimeMillis()}.wav")
                response.body?.byteStream()?.use { input ->
                    audioFile.outputStream().use { output ->
                        input.copyTo(output)
                    }
                }
                
                return@withContext audioFile
            }
        } catch (e: IOException) {
            Log.e("TwiTTS", "Error synthesizing speech", e)
            return@withContext null
        }
    }
    
    fun playAudio(audioFile: File) {
        try {
            mediaPlayer.reset()
            mediaPlayer.setDataSource(audioFile.path)
            mediaPlayer.prepare()
            mediaPlayer.start()
        } catch (e: IOException) {
            Log.e("TwiTTS", "Error playing audio", e)
        }
    }
    
    fun release() {
        mediaPlayer.release()
    }
}
```

Usage in an Activity:

```kotlin
// MainActivity.kt
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {
    private lateinit var ttsManager: TwiTTSManager
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        ttsManager = TwiTTSManager(this)
        
        val textInput = findViewById<EditText>(R.id.textInput)
        val speakButton = findViewById<Button>(R.id.speakButton)
        
        speakButton.setOnClickListener {
            val text = textInput.text.toString()
            if (text.isNotEmpty()) {
                speakButton.isEnabled = false
                
                CoroutineScope(Dispatchers.Main).launch {
                    try {
                        val audioFile = ttsManager.synthesize(text)
                        if (audioFile != null) {
                            ttsManager.playAudio(audioFile)
                        } else {
                            Toast.makeText(
                                this@MainActivity,
                                "Failed to generate speech",
                                Toast.LENGTH_SHORT
                            ).show()
                        }
                    } finally {
                        speakButton.isEnabled = true
                    }
                }
            }
        }
    }
    
    override fun onDestroy() {
        ttsManager.release()
        super.onDestroy()
    }
}
```

### iOS Integration (Swift)

```swift
// TwiTTSManager.swift
import Foundation
import AVFoundation

class TwiTTSManager {
    private let apiUrl = "https://your-tts-api.com/synthesize"
    private var audioPlayer: AVAudioPlayer?
    
    func synthesize(text: String, completion: @escaping (Result<URL, Error>) -> Void) {
        // Create request
        guard let url = URL(string: apiUrl) else {
            completion(.failure(NSError(domain: "TwiTTS", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"])))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        // Create form data
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"text\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(text)\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        // Execute request
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "TwiTTS", code: 1, userInfo: [NSLocalizedDescriptionKey: "No data received"])))
                return
            }
            
            // Save audio to temporary file
            let tempDir = FileManager.default.temporaryDirectory
            let audioFile = tempDir.appendingPathComponent("twi_speech_\(Date().timeIntervalSince1970).wav")
            
            do {
                try data.write(to: audioFile)
                completion(.success(audioFile))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    func playAudio(from url: URL) throws {
        audioPlayer = try AVAudioPlayer(contentsOf: url)
        audioPlayer?.prepareToPlay()
        audioPlayer?.play()
    }
}
```

Usage in a View Controller:

```swift
// ViewController.swift
import UIKit

class ViewController: UIViewController {
    @IBOutlet weak var textField: UITextField!
    @IBOutlet weak var speakButton: UIButton!
    @IBOutlet weak var activityIndicator: UIActivityIndicatorView!
    
    private let ttsManager = TwiTTSManager()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        activityIndicator.isHidden = true
    }
    
    @IBAction func speakButtonTapped(_ sender: UIButton) {
        guard let text = textField.text, !text.isEmpty else {
            return
        }
        
        // Show loading indicator
        speakButton.isEnabled = false
        activityIndicator.isHidden = false
        activityIndicator.startAnimating()
        
        // Synthesize speech
        ttsManager.synthesize(text: text) { [weak self] result in
            DispatchQueue.main.async {
                self?.activityIndicator.stopAnimating()
                self?.activityIndicator.isHidden = true
                self?.speakButton.isEnabled = true
                
                switch result {
                case .success(let audioUrl):
                    do {
                        try self?.ttsManager.playAudio(from: audioUrl)
                    } catch {
                        self?.showAlert(message: "Failed to play audio: \(error.localizedDescription)")
                    }
                case .failure(let error):
                    self?.showAlert(message: "Failed to generate speech: \(error.localizedDescription)")
                }
            }
        }
    }
    
    private func showAlert(message: String) {
        let alert = UIAlertController(
            title: "Error",
            message: message,
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}
```

## Desktop Applications

### PyQt5 Application

```python
import sys
import os
import tempfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                            QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from kalakan_twi_tts import TwiSynthesizer

class SynthesisThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, text):
        super().__init__()
        self.text = text
        
    def run(self):
        try:
            # Initialize synthesizer
            synthesizer = TwiSynthesizer()
            
            # Generate speech
            audio = synthesizer.synthesize(self.text)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file.close()
            
            synthesizer.save_audio(audio, temp_file.name)
            
            self.finished.emit(temp_file.name)
        except Exception as e:
            self.error.emit(str(e))

class TwiTTSApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Twi Text-to-Speech")
        self.setMinimumSize(600, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Text input
        main_layout.addWidget(QLabel("Enter Twi text:"))
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type Twi text here...")
        self.text_edit.setText("Akwaaba! Wo ho te sɛn?")
        main_layout.addWidget(self.text_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.speak_button = QPushButton("Speak")
        self.speak_button.clicked.connect(self.synthesize_speech)
        button_layout.addWidget(self.speak_button)
        
        self.save_button = QPushButton("Save Audio")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_audio)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Media player for audio playback
        self.media_player = QMediaPlayer()
        
        # Current audio file
        self.current_audio_file = None
        
    def synthesize_speech(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text.")
            return
        
        # Disable button and show progress
        self.speak_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start synthesis in a separate thread
        self.synthesis_thread = SynthesisThread(text)
        self.synthesis_thread.finished.connect(self.on_synthesis_finished)
        self.synthesis_thread.error.connect(self.on_synthesis_error)
        self.synthesis_thread.start()
        
    def on_synthesis_finished(self, audio_file):
        # Enable buttons and hide progress
        self.speak_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Store audio file path
        self.current_audio_file = audio_file
        
        # Play the audio
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_file)))
        self.media_player.play()
        
    def on_synthesis_error(self, error_message):
        # Enable button and hide progress
        self.speak_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Show error message
        QMessageBox.critical(self, "Error", f"Failed to generate speech: {error_message}")
        
    def save_audio(self):
        from PyQt5.QtWidgets import QFileDialog
        
        if not self.current_audio_file:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Audio File", "", "WAV Files (*.wav)"
        )
        
        if file_path:
            import shutil
            shutil.copy(self.current_audio_file, file_path)
            QMessageBox.information(self, "Success", f"Audio saved to {file_path}")
            
    def closeEvent(self, event):
        # Clean up temporary files
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                os.unlink(self.current_audio_file)
            except:
                pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TwiTTSApp()
    window.show()
    sys.exit(app.exec_())
```

### Electron Application

```javascript
// main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const axios = require('axios');
const fs = require('fs');
const { promisify } = require('util');
const writeFileAsync = promisify(fs.writeFile);

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

// Handle TTS requests
ipcMain.handle('synthesize-speech', async (event, text) => {
  try {
    // Call TTS API
    const response = await axios.post('https://your-tts-api.com/synthesize', 
      { text },
      { responseType: 'arraybuffer' }
    );
    
    // Save to temporary file
    const tempFile = path.join(app.getPath('temp'), `twi-speech-${Date.now()}.wav`);
    await writeFileAsync(tempFile, Buffer.from(response.data));
    
    return { success: true, filePath: tempFile };
  } catch (error) {
    console.error('TTS Error:', error);
    return { 
      success: false, 
      error: error.message || 'Failed to generate speech' 
    };
  }
});
```

```javascript
// preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('twiTTS', {
  synthesize: (text) => ipcRenderer.invoke('synthesize-speech', text)
});
```

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Twi Text-to-Speech</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 20px;
      max-width: 800px;
      margin: 0 auto;
    }
    textarea {
      width: 100%;
      height: 150px;
      margin-bottom: 15px;
      padding: 10px;
      font-size: 16px;
    }
    button {
      padding: 10px 20px;
      font-size: 16px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    button:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
    }
    .audio-container {
      margin-top: 20px;
    }
    .error {
      color: red;
      margin-top: 10px;
    }
    .loading {
      margin-top: 10px;
      color: #666;
    }
  </style>
</head>
<body>
  <h1>Twi Text-to-Speech</h1>
  
  <div>
    <label for="text-input">Enter Twi text:</label>
    <textarea id="text-input">Akwaaba! Wo ho te sɛn?</textarea>
  </div>
  
  <button id="speak-button">Speak</button>
  
  <div id="loading" class="loading" style="display: none;">
    Generating speech...
  </div>
  
  <div id="error" class="error" style="display: none;"></div>
  
  <div id="audio-container" class="audio-container" style="display: none;">
    <h3>Generated Speech:</h3>
    <audio id="audio-player" controls></audio>
  </div>
  
  <script>
    const textInput = document.getElementById('text-input');
    const speakButton = document.getElementById('speak-button');
    const loadingElement = document.getElementById('loading');
    const errorElement = document.getElementById('error');
    const audioContainer = document.getElementById('audio-container');
    const audioPlayer = document.getElementById('audio-player');
    
    speakButton.addEventListener('click', async () => {
      const text = textInput.value.trim();
      
      if (!text) {
        errorElement.textContent = 'Please enter some text.';
        errorElement.style.display = 'block';
        return;
      }
      
      // Reset UI
      errorElement.style.display = 'none';
      audioContainer.style.display = 'none';
      loadingElement.style.display = 'block';
      speakButton.disabled = true;
      
      try {
        // Call TTS API
        const result = await window.twiTTS.synthesize(text);
        
        if (result.success) {
          // Play audio
          audioPlayer.src = `file://${result.filePath}`;
          audioContainer.style.display = 'block';
        } else {
          // Show error
          errorElement.textContent = result.error;
          errorElement.style.display = 'block';
        }
      } catch (error) {
        errorElement.textContent = error.message || 'An error occurred';
        errorElement.style.display = 'block';
      } finally {
        loadingElement.style.display = 'none';
        speakButton.disabled = false;
      }
    });
  </script>
</body>
</html>
```

## Command Line Tools

### Basic CLI Tool

```python
#!/usr/bin/env python
# cli.py
import argparse
import sys
from kalakan_twi_tts import TwiSynthesizer

def main():
    parser = argparse.ArgumentParser(description="Twi Text-to-Speech CLI")
    parser.add_argument("--text", "-t", type=str, help="Text to synthesize")
    parser.add_argument("--file", "-f", type=str, help="Text file to synthesize")
    parser.add_argument("--output", "-o", type=str, default="output.wav", help="Output audio file")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed factor")
    parser.add_argument("--pitch", type=float, default=1.0, help="Pitch factor")
    parser.add_argument("--energy", type=float, default=1.0, help="Energy/volume factor")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    # Initialize synthesizer
    synthesizer = TwiSynthesizer()
    
    if args.interactive:
        print("Twi Text-to-Speech Interactive Mode")
        print("Type 'exit' or 'quit' to exit")
        print("Type 'save <filename>' to save the last generated audio")
        
        last_audio = None
        
        while True:
            try:
                text = input("\nEnter text: ")
                
                if text.lower() in ["exit", "quit"]:
                    break
                
                if text.lower().startswith("save "):
                    if last_audio is None:
                        print("No audio to save. Generate some audio first.")
                        continue
                    
                    filename = text[5:].strip()
                    if not filename:
                        filename = "output.wav"
                    
                    synthesizer.save_audio(last_audio, filename)
                    print(f"Audio saved to {filename}")
                    continue
                
                # Generate speech
                print("Generating speech...")
                audio = synthesizer.synthesize(
                    text=text,
                    speed=args.speed,
                    pitch=args.pitch,
                    energy=args.energy
                )
                
                # Play audio
                print("Playing audio...")
                synthesizer.play_audio(audio)
                
                # Store for potential saving
                last_audio = audio
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("Goodbye!")
        return 0
    
    # Get text to synthesize
    if args.text:
        text = args.text
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1
    
    # Generate speech
    try:
        print(f"Generating speech for: {text[:50]}{'...' if len(text) > 50 else ''}")
        audio = synthesizer.synthesize(
            text=text,
            speed=args.speed,
            pitch=args.pitch,
            energy=args.energy
        )
        
        # Save audio
        synthesizer.save_audio(audio, args.output)
        print(f"Audio saved to {args.output}")
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Cloud Services

### AWS Lambda Function

```python
# lambda_function.py
import json
import os
import tempfile
import base64
from kalakan_twi_tts import TwiSynthesizer

# Initialize synthesizer at the module level for reuse across invocations
synthesizer = TwiSynthesizer()

def lambda_handler(event, context):
    try:
        # Get text from request
        body = json.loads(event.get('body', '{}'))
        text = body.get('text', '')
        
        if not text:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No text provided'})
            }
        
        # Optional parameters
        speed = float(body.get('speed', 1.0))
        pitch = float(body.get('pitch', 1.0))
        energy = float(body.get('energy', 1.0))
        
        # Generate speech
        audio = synthesizer.synthesize(
            text=text,
            speed=speed,
            pitch=pitch,
            energy=energy
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        synthesizer.save_audio(audio, temp_path)
        
        # Read file and encode as base64
        with open(temp_path, 'rb') as f:
            audio_data = f.read()
        
        os.unlink(temp_path)
        
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'audio': audio_base64,
                'format': 'wav',
                'sample_rate': 22050
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### Google Cloud Function

```python
# main.py
import functions_framework
import tempfile
import base64
import os
from flask import jsonify, Request
from kalakan_twi_tts import TwiSynthesizer

# Initialize synthesizer
synthesizer = TwiSynthesizer()

@functions_framework.http
def synthesize_speech(request: Request):
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # Handle OPTIONS request (preflight)
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    # Handle POST request
    if request.method != 'POST':
        return (jsonify({'error': 'Method not allowed'}), 405, headers)
    
    # Get request data
    request_json = request.get_json(silent=True)
    
    if not request_json or 'text' not in request_json:
        return (jsonify({'error': 'No text provided'}), 400, headers)
    
    text = request_json['text']
    speed = float(request_json.get('speed', 1.0))
    pitch = float(request_json.get('pitch', 1.0))
    energy = float(request_json.get('energy', 1.0))
    
    try:
        # Generate speech
        audio = synthesizer.synthesize(
            text=text,
            speed=speed,
            pitch=pitch,
            energy=energy
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        synthesizer.save_audio(audio, temp_path)
        
        # Read file and encode as base64
        with open(temp_path, 'rb') as f:
            audio_data = f.read()
        
        os.unlink(temp_path)
        
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Return response
        response = {
            'audio': audio_base64,
            'format': 'wav',
            'sample_rate': 22050
        }
        
        return (jsonify(response), 200, headers)
    except Exception as e:
        return (jsonify({'error': str(e)}), 500, headers)
```

---

These integration examples should help developers quickly implement Twi speech synthesis in their applications. For more advanced use cases or specific frameworks, refer to the API documentation or contact the Kalakan TTS team for support.