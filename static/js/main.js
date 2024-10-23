// main.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('Gestor de Mensajes Seguros en Castellano cargado');

    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            html.classList.toggle('dark');
            localStorage.setItem('darkMode', html.classList.contains('dark'));
        });

        // Check for saved dark mode preference
        if (localStorage.getItem('darkMode') === 'true') {
            html.classList.add('dark');
        }
    }

    // Initialize CAPTCHA if we're on the create message page
    initializeCaptcha();

    // Expiration date calculation on create message page
    initializeExpirationCalculator();

    // Copy URL and encryption key functionality
    initializeCopyFunctionality();
});

function initializeCaptcha() {
    // Only initialize if we're on the create message page
    const form = document.querySelector('form[action="/create"]');
    if (!form) return;

    const captchaSection = document.getElementById('captcha-section');
    if (!captchaSection) {
        console.error('CAPTCHA section not found');
        return;
    }

    const submitButton = document.getElementById('submit-button');
    const num1Span = document.getElementById('num1');
    const operatorSpan = document.getElementById('operator');
    const num2Span = document.getElementById('num2');
    const captchaAnswer = document.getElementById('captcha-answer');
    const captchaMessage = document.getElementById('captcha-message');

    if (!submitButton || !num1Span || !operatorSpan || !num2Span || !captchaAnswer || !captchaMessage) {
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

        console.log('CAPTCHA generated:', { num1, operator, num2, correctAnswer });
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

    // Ensure form can't be submitted without correct CAPTCHA
    form.addEventListener('submit', function(e) {
        if (submitButton.disabled) {
            e.preventDefault();
            captchaMessage.textContent = 'Por favor, complete el CAPTCHA correctamente.';
            captchaMessage.className = 'text-sm text-red-600 dark:text-red-400';
        }
    });

    // Generate initial CAPTCHA
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
