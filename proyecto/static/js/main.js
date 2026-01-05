document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadSection = document.getElementById('upload-section');
    const configSection = document.getElementById('config-section');
    const progressSection = document.getElementById('progress-section');
    const resultSection = document.getElementById('result-section');

    let currentConversionId = null;

    // Drag and Drop Events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length) handleFile(files[0]);
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });

    function handleFile(file) {
        if (file.type !== 'application/pdf') {
            showError('Por favor sube un archivo PDF válido.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        // Show loading state implies uploading
        uploadSection.classList.add('opacity-50', 'pointer-events-none');

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) throw new Error(data.error);
                showConfig(data);
            })
            .catch(err => {
                showError(err.message);
                uploadSection.classList.remove('opacity-50', 'pointer-events-none');
            });
    }

    function showError(msg) {
        const errorDiv = document.getElementById('upload-error');
        errorDiv.textContent = msg;
        errorDiv.classList.remove('hidden');
    }

    function showConfig(data) {
        currentConversionId = data.id;

        document.getElementById('doc-title').textContent = data.title || data.filename;
        document.getElementById('doc-author').textContent = data.author || 'Autor desconocido';
        document.getElementById('detected-language').textContent = data.language ? data.language.toUpperCase() : 'Unknown';
        document.getElementById('doc-pages').textContent = data.pages;

        // Populate Voices based on Language
        populateVoices(data.language);

        uploadSection.classList.add('hidden');
        configSection.classList.remove('hidden');
    }

    function populateVoices(lang) {
        const select = document.getElementById('voice-select');
        select.innerHTML = '';

        // Simple mapping for 'Accents' as voices since gTTS logic is simple
        // This is a mock-up of what could be real voices
        let options = [];
        const baseLang = lang ? lang.split('-')[0] : 'en';

        if (baseLang === 'es') {
            options = [
                { value: 'es', label: 'Español (España) - Femenina' },
                { value: 'es-us', label: 'Español (Latino) - Femenina' }, // gTTS defaults mapped
                { value: 'es', label: 'Español (Neutro) - Masculina (Simulado)' } // gTTS doesn't support male usually
            ];
        } else if (baseLang === 'en') {
            options = [
                { value: 'en', label: 'English (US)' },
                { value: 'en-uk', label: 'English (UK)' },
                { value: 'en-au', label: 'English (Australia)' }
            ];
        } else {
            options = [
                { value: lang, label: `Standard (${lang})` }
            ];
        }

        options.forEach(opt => {
            const el = document.createElement('option');
            el.value = opt.value;
            el.textContent = opt.label;
            select.appendChild(el);
        });
    }

    // Speed Slider
    const speedRange = document.getElementById('speed-range');
    const speedDisplay = document.getElementById('speed-display');
    speedRange.addEventListener('input', (e) => {
        speedDisplay.textContent = e.target.value + 'x';
    });

    // Generate Button
    document.getElementById('convert-btn').addEventListener('click', () => {
        const voice = document.getElementById('voice-select').value;
        const speed = speedRange.value;

        configSection.classList.add('hidden');
        progressSection.classList.remove('hidden');

        fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: currentConversionId,
                voice: voice,
                speed: parseFloat(speed)
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'started') {
                    pollStatus();
                }
            });
    });

    function pollStatus() {
        const interval = setInterval(() => {
            fetch(`/status/${currentConversionId}`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById('progress-status').textContent = data.status === 'processing' ? 'Procesando...' : data.status;
                    document.getElementById('progress-detail').textContent = data.progress;

                    // Simulate progress bar width
                    const bar = document.getElementById('progress-bar');
                    if (data.status === 'processing') {
                        // Fake progress
                        let w = parseInt(bar.style.width || 0);
                        if (w < 90) bar.style.width = (w + 5) + '%';
                    }

                    if (data.status === 'completed') {
                        clearInterval(interval);
                        bar.style.width = '100%';
                        showResult(data);
                    } else if (data.status === 'error') {
                        clearInterval(interval);
                        showError("Error en la conversión"); // simplified
                    }
                });
        }, 1000);
    }

    function showResult(data) {
        setTimeout(() => {
            progressSection.classList.add('hidden');
            resultSection.classList.remove('hidden');

            const audio = document.getElementById('audio-player');
            audio.src = data.mp3_url;

            const downloadBtn = document.getElementById('download-btn');
            downloadBtn.href = `/download/${currentConversionId}`;

            document.getElementById('play-btn').onclick = () => audio.play();

        }, 500);
    }
});
