document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // File upload handling
    const fileInput = document.getElementById('video-file');
    const fileLabel = document.querySelector('.file-text');
    const fileName = document.querySelector('.file-name');
    
    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length > 0) {
            fileName.textContent = fileInput.files[0].name;
            fileLabel.textContent = 'File selected';
        } else {
            fileName.textContent = '';
            fileLabel.textContent = 'Choose a file or drag it here';
        }
    });
    
    // URL form submission
    const urlForm = document.getElementById('url-form');
    urlForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const videoUrl = document.getElementById('video-url').value;
        analyzeAccent('url', videoUrl);
    });
    
    // File form submission
    const fileForm = document.getElementById('file-form');
    fileForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (fileInput.files.length > 0) {
            analyzeAccent('file', fileInput.files[0]);
        }
    });
    
    // New analysis button
    document.getElementById('new-analysis').addEventListener('click', () => {
        resetForms();
    });
    
    // Try again button
    document.getElementById('try-again').addEventListener('click', () => {
        resetForms();
    });
    
    // Function to analyze accent
    function analyzeAccent(type, source) {
        // Show loading
        document.querySelector('.tabs').classList.add('hidden');
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.add('hidden'));
        document.getElementById('loading').classList.remove('hidden');
        document.getElementById('results').classList.add('hidden');
        document.getElementById('error').classList.add('hidden');
        
        // Prepare form data
        const formData = new FormData();
        if (type === 'url') {
            formData.append('url', source);
        } else {
            formData.append('file', source);
        }
        
        // Send request
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('loading').classList.add('hidden');
            
            if (data.error) {
                // Show error
                document.getElementById('error-message').textContent = data.error;
                document.getElementById('error').classList.remove('hidden');
            } else {
                // Show results
                displayResults(data);
                document.getElementById('results').classList.remove('hidden');
            }
        })
        .catch(error => {
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('error-message').textContent = 'An error occurred. Please try again.';
            document.getElementById('error').classList.remove('hidden');
            console.error('Error:', error);
        });
    }
    
    // Function to display results
    function displayResults(data) {
        // Set accent
        document.getElementById('accent-result').textContent = data.accent;
        
        // Set confidence
        const confidenceValue = parseFloat(data.confidence);
        document.getElementById('confidence-value').textContent = data.confidence;
        document.getElementById('confidence-bar').style.width = `${confidenceValue}%`;
        
        // Set English confidence
        const englishValue = parseFloat(data.english_confidence);
        document.getElementById('english-value').textContent = data.english_confidence;
        document.getElementById('english-bar').style.width = `${englishValue}%`;
        
        // Set top accents
        const topAccentsList = document.getElementById('top-accents');
        topAccentsList.innerHTML = '';
        data.top_accents.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<span>${item.accent}</span><span>${item.confidence}</span>`;
            topAccentsList.appendChild(li);
        });
        
        // Set transcript sample
        document.getElementById('transcript-sample').textContent = data.transcript_sample;
    }
    
    // Function to reset forms
    function resetForms() {
        urlForm.reset();
        fileForm.reset();
        fileName.textContent = '';
        fileLabel.textContent = 'Choose a file or drag it here';
        
        document.querySelector('.tabs').classList.remove('hidden');
        document.getElementById('url-tab').classList.add('active');
        document.getElementById('file-tab').classList.remove('active');
        tabBtns[0].classList.add('active');
        tabBtns[1].classList.remove('active');
        
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results').classList.add('hidden');
        document.getElementById('error').classList.add('hidden');
    }
});
