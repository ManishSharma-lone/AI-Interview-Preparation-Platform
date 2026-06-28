// Web Speech API wrapper for Microphone transcribing and visuals

let recognition = null;
let speechRecognitionActive = false;

// Check browser support on startup
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.warn("Speech Recognition API is not supported in this browser. Fallback typing active.");
        return null;
    }

    const rec = new SpeechRecognition();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = 'en-US';

    rec.onstart = () => {
        speechRecognitionActive = true;
        updateVoiceUI(true);
    };

    rec.onresult = (event) => {
        let interimTranscript = "";
        let finalTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            } else {
                interimTranscript += event.results[i][0].transcript;
            }
        }

        const activeText = finalTranscript || interimTranscript;
        if (activeText.trim()) {
            const transcriptLog = document.getElementById("voice-transcript-log");
            transcriptLog.textContent = activeText;
            
            // Sync with textarea if it's visible
            const textInput = document.getElementById("answer-textbox");
            if (textInput) {
                textInput.value = activeText;
            }
        }
    };

    rec.onerror = (event) => {
        console.error("Speech Recognition Error:", event.error);
        if (event.error === 'not-allowed') {
            alert("Microphone permission denied. Enable microphone access in browser settings.");
        }
        stopVoiceRecognition();
    };

    rec.onend = () => {
        speechRecognitionActive = false;
        updateVoiceUI(false);
    };

    return rec;
}

function toggleVoiceDictation() {
    if (!recognition) {
        recognition = initSpeechRecognition();
    }

    if (!recognition) {
        alert("Web Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge, or type your response.");
        return;
    }

    if (speechRecognitionActive) {
        stopVoiceRecognition();
    } else {
        startVoiceRecognition();
    }
}

function startVoiceRecognition() {
    if (recognition && !speechRecognitionActive) {
        try {
            document.getElementById("voice-transcript-log").textContent = "Listening... Speak into your microphone.";
            recognition.start();
        } catch (e) {
            console.error("Failed to start speech recognition:", e);
        }
    }
}

function stopVoiceRecognition() {
    if (recognition && speechRecognitionActive) {
        try {
            recognition.stop();
        } catch (e) {
            console.error("Failed to stop speech recognition:", e);
        }
    }
}

function updateVoiceUI(isRecording) {
    const orb = document.getElementById("mic-trigger-btn");
    
    if (isRecording) {
        orb.classList.add("recording");
        orb.innerHTML = '<i data-lucide="mic-off"></i>';
    } else {
        orb.classList.remove("recording");
        orb.innerHTML = '<i data-lucide="mic"></i>';
    }
    
    lucide.createIcons();
}
