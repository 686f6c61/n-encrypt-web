document.addEventListener('DOMContentLoaded', function() {
    console.log('N-Encrypt iniciado');

    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;
    
    function updateDarkModeUI(isDark) {
        if (isDark) {
            html.classList.add('dark');
        } else {
            html.classList.remove('dark');
        }

        // Update button icons
        const moonIcon = darkModeToggle.querySelector('.fa-moon');
        const sunIcon = darkModeToggle.querySelector('.fa-sun');
        
        if (isDark) {
            moonIcon.classList.add('hidden');
            sunIcon.classList.remove('hidden');
        } else {
            moonIcon.classList.remove('hidden');
            sunIcon.classList.add('hidden');
        }
    }

    if (darkModeToggle) {
        // Check system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Check saved preference or use system preference
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode !== null) {
            updateDarkModeUI(savedDarkMode === 'true');
        } else {
            updateDarkModeUI(prefersDark.matches);
        }

        // Toggle dark mode on button click
        darkModeToggle.addEventListener('click', function() {
            const isDark = !html.classList.contains('dark');
            updateDarkModeUI(isDark);
            localStorage.setItem('darkMode', isDark);
        });

        // Listen for system theme changes
        prefersDark.addEventListener('change', e => {
            if (localStorage.getItem('darkMode') === null) {
                updateDarkModeUI(e.matches);
            }
        });
    }

    // Initialize CAPTCHA if we're on the create message page
    initializeCaptcha();
    initializeExpirationCalculator();
    initializeCopyFunctionality();
});

function initializeCaptcha() {
    const form = document.querySelector('form[action="/create"]');
    if (!form) return;

    const captchaSection = document.getElementById('captcha-section');
    const submitButton = document.getElementById('submit-button');
    const num1Span = document.getElementById('num1');
    const operatorSpan = document.getElementById('operator');
    const num2Span = document.getElementById('num2');
    const captchaAnswer = document.getElementById('captcha-answer');
    const captchaMessage = document.getElementById('captcha-message');

    if (!captchaSection || !submitButton || !num1Span || !operatorSpan || !num2Span || !captchaAnswer || !captchaMessage) {
        console.error('Required CAPTCHA elements not found');
        return;
    }

    let correctAnswer;

    function generateCaptcha() {
        const num1 = Math.floor(Math.random() * 10) + 1;
        const num2 = Math.floor(Math.random() * 10) + 1;
        const isAddition = Math.random() < 0.5;
        const operator = isAddition ? '+' : '-';

        num1Span.textContent = num1;
        operatorSpan.textContent = operator;
        num2Span.textContent = num2;

        correctAnswer = isAddition ? num1 + num2 : num1 - num2;

        captchaAnswer.value = '';
        submitButton.disabled = true;
        captchaMessage.textContent = '';
        captchaMessage.className = 'text-sm';
    }

    captchaAnswer.addEventListener('input', function() {
        const userAnswer = parseInt(this.value.trim());

        if (!isNaN(userAnswer)) {
            if (userAnswer === correctAnswer) {
                captchaMessage.textContent = '¡Correcto!';
                captchaMessage.className = 'text-sm text-green-600 dark:text-green-400';
                submitButton.disabled = false;
            } else {
                captchaMessage.textContent = 'Respuesta incorrecta. Intenta de nuevo.';
                captchaMessage.className = 'text-sm text-red-600 dark:text-red-400';
                submitButton.disabled = true;
            }
        } else {
            submitButton.disabled = true;
        }
    });

    generateCaptcha();
}

function initializeExpirationCalculator() {
    const expirationDays = document.getElementById('expiration_days');
    const expirationHours = document.getElementById('expiration_hours');
    const expirationMinutes = document.getElementById('expiration_minutes');
    const expirationDisplay = document.getElementById('expiration-display');

    if (expirationDays && expirationHours && expirationMinutes && expirationDisplay) {
        function updateExpirationDate() {
            const days = parseInt(expirationDays.value) || 0;
            const hours = parseInt(expirationHours.value) || 0;
            const minutes = parseInt(expirationMinutes.value) || 0;

            const expirationDate = new Date();
            expirationDate.setDate(expirationDate.getDate() + days);
            expirationDate.setHours(expirationDate.getHours() + hours);
            expirationDate.setMinutes(expirationDate.getMinutes() + minutes);

            expirationDisplay.textContent = `El mensaje expirará el: ${expirationDate.toLocaleString('es-ES')}`;
        }

        expirationDays.addEventListener('input', updateExpirationDate);
        expirationHours.addEventListener('input', updateExpirationDate);
        expirationMinutes.addEventListener('input', updateExpirationDate);
        updateExpirationDate();
    }
}

function initializeCopyFunctionality() {
    const urlElement = document.querySelector('.message-url');
    const encryptionKeyElement = document.querySelector('.encryption-key');

    if (urlElement) {
        urlElement.addEventListener('click', function(e) {
            e.preventDefault();
            copyToClipboard(this.href, 'URL copiada al portapapeles');
        });
    }

    if (encryptionKeyElement) {
        encryptionKeyElement.addEventListener('click', function(e) {
            e.preventDefault();
            copyToClipboard(this.textContent, 'Clave de encriptación copiada al portapapeles');
        });
    }
}

function copyToClipboard(text, message) {
    navigator.clipboard.writeText(text)
        .then(() => {
            alert(message);
        })
        .catch(err => {
            console.error('Error al copiar al portapapeles:', err);
        });
}
