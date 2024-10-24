// Password Generator with Entropy Measurement
document.addEventListener('DOMContentLoaded', function() {
    const passwordSection = document.createElement('div');
    passwordSection.className = 'mb-6 bg-white p-4 rounded-lg shadow-md dark:bg-gray-800';
    passwordSection.innerHTML = `
        <h3 class="text-lg font-medium mb-4 text-gray-700 dark:text-gray-300">
            <i class="fas fa-key mr-2"></i>Generador de Contraseñas Seguras
        </h3>
        <div class="space-y-4">
            <div class="flex items-center gap-4">
                <label class="text-sm text-gray-600 dark:text-gray-400">Longitud:</label>
                <input type="range" id="passwordLength" min="20" max="64" value="24" class="w-full">
                <span id="lengthDisplay" class="text-sm text-gray-600 dark:text-gray-400">24</span>
            </div>
            <div class="relative">
                <input type="text" id="generatedPassword" readonly 
                    class="w-full px-4 py-2 border rounded-md bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    placeholder="Contraseña generada">
                <button id="copyPassword" class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
            <div class="flex items-center gap-4">
                <div class="flex-grow">
                    <div class="h-2 bg-gray-200 rounded-full dark:bg-gray-700">
                        <div id="strengthIndicator" class="h-2 rounded-full transition-all duration-300"></div>
                    </div>
                </div>
                <span id="entropyValue" class="text-sm text-gray-600 dark:text-gray-400">0 bits</span>
            </div>
            <button id="generatePassword" class="w-full bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-50 transition duration-300">
                <i class="fas fa-sync-alt mr-2"></i>Generar Nueva Contraseña
            </button>

            <!-- Entropy Explanation Section -->
            <div class="mt-4 p-4 bg-blue-50 rounded-lg dark:bg-gray-700">
                <h4 class="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                    <i class="fas fa-info-circle mr-2"></i>¿Qué es la Entropía?
                </h4>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    La entropía es una medida matemática de la aleatoriedad y complejidad de una contraseña. Se mide en bits y cuanto mayor sea el valor, más segura será la contraseña.
                </p>
                <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                    <li><i class="fas fa-check-circle text-green-500 mr-1"></i>< 80 bits: Moderada - Suficiente para uso general</li>
                    <li><i class="fas fa-check-circle text-blue-500 mr-1"></i>80-100 bits: Fuerte - Recomendada para cuentas importantes</li>
                    <li><i class="fas fa-check-circle text-purple-500 mr-1"></i>> 100 bits: Muy Fuerte - Ideal para datos críticos</li>
                </ul>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">
                    <i class="fas fa-lightbulb mr-1 text-yellow-500"></i>Tip: Una contraseña más larga con diferentes tipos de caracteres aumenta significativamente la entropía.
                </p>
            </div>
            <p id="strengthDescription" class="text-sm text-gray-500 dark:text-gray-400 mt-2"></p>
        </div>
    `;

    // Insert the password generator before the form in create_message.html
    const form = document.querySelector('form[action="/create"]');
    if (form) {
        form.parentNode.insertBefore(passwordSection, form);
    }

    const passwordLength = document.getElementById('passwordLength');
    const lengthDisplay = document.getElementById('lengthDisplay');
    const generatedPassword = document.getElementById('generatedPassword');
    const generateButton = document.getElementById('generatePassword');
    const copyButton = document.getElementById('copyPassword');
    const strengthIndicator = document.getElementById('strengthIndicator');
    const entropyValue = document.getElementById('entropyValue');
    const strengthDescription = document.getElementById('strengthDescription');

    function calculateEntropy(password) {
        // All character types are included by default
        const poolSize = 26 + 26 + 10 + 32; // uppercase + lowercase + numbers + special
        
        // Calculate entropy using Shannon's formula: log2(poolSize^length)
        const entropy = Math.floor(password.length * Math.log2(poolSize));
        
        let strength, color;
        if (entropy < 80) {
            strength = 'Moderada';
            color = 'bg-yellow-500';
        } else if (entropy < 100) {
            strength = 'Fuerte';
            color = 'bg-green-500';
        } else {
            strength = 'Muy Fuerte';
            color = 'bg-blue-500';
        }

        return { entropy, strength, color };
    }

    function generatePassword(length) {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?';
        
        let password = '';
        const array = new Uint32Array(length);
        crypto.getRandomValues(array);
        
        for (let i = 0; i < length; i++) {
            password += chars[array[i] % chars.length];
        }

        return password;
    }

    function updatePasswordStrength(password) {
        const { entropy, strength, color } = calculateEntropy(password);
        
        // Update UI
        strengthIndicator.className = `h-2 rounded-full transition-all duration-300 ${color}`;
        strengthIndicator.style.width = Math.min((entropy / 128) * 100, 100) + '%';
        entropyValue.textContent = `${entropy} bits`;
        strengthDescription.innerHTML = `
            <i class="fas ${entropy < 80 ? 'fa-shield' : entropy < 100 ? 'fa-shield-alt' : 'fa-shield-check'} mr-2"></i>
            Fortaleza de la contraseña: ${strength} (${entropy} bits de entropía)
        `;
        
        return entropy;
    }

    function generateAndUpdatePassword() {
        const length = parseInt(passwordLength.value);
        const password = generatePassword(length);
        generatedPassword.value = password;
        updatePasswordStrength(password);
    }

    // Event Listeners
    generateButton.addEventListener('click', generateAndUpdatePassword);

    copyButton.addEventListener('click', () => {
        if (generatedPassword.value) {
            navigator.clipboard.writeText(generatedPassword.value)
                .then(() => {
                    copyButton.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => {
                        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                    }, 1500);
                });
        }
    });

    passwordLength.addEventListener('input', () => {
        lengthDisplay.textContent = passwordLength.value;
        generateAndUpdatePassword();
    });

    // Generate initial password
    generateAndUpdatePassword();
});
