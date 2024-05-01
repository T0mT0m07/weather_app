document.addEventListener("DOMContentLoaded", function() {
    // Setup for dynamic theme colors based on time
    applyThemeColors();
    
    // Conditional logic to initialize Swiper and handle password strength on the signup page
    handleSignupPage();
    
    // Initialize Swiper only if it's the correct page for displaying forecasts
    initializeSwiper();

    function applyThemeColors() {
        var now = new Date();
        var hour = now.getHours();
        var bodyStyle = document.body.style;
        var dayColorStart = '#62b8f5';
        var dayColorEnd = '#4475ef';
        var nightColorStart = '#2c3e50';
        var nightColorEnd = '#34495e';

        if (hour >= 6 && hour < 18) {
            bodyStyle.setProperty('--blue-1', dayColorStart);
            bodyStyle.setProperty('--blue-2', dayColorEnd);
        } else {
            bodyStyle.setProperty('--blue-1', nightColorStart);
            bodyStyle.setProperty('--blue-2', nightColorEnd);
        }
    }

    function handleSignupPage() {
        // Check if we are on the signup page
        if (document.querySelector('.form') && window.location.href.indexOf('signup') > -1) {
            const passwordInput = document.querySelector('input[name="password1"]');
            const strengthIndicator = document.getElementById('password-strength'); // Ensure there's an element with this ID in HTML
            if (passwordInput && strengthIndicator) {
                passwordInput.addEventListener('input', function() {
                    const strengthMessage = checkPasswordStrength(this.value);
                    strengthIndicator.textContent = strengthMessage;
                    strengthIndicator.style.display = 'block'; // Only display when there's input
                });
            }
        }
    }

    function checkPasswordStrength(password) {
        let strength = "Weak";
        const length = password.length;
        const hasNumbers = /\d/.test(password);
        const hasSpecialChars = /\W/.test(password);

        if (length > 8 && hasNumbers && hasSpecialChars) {
            strength = "Strong";
        } else if (length > 5) {
            strength = "Moderate";
        }
        return strength;
    }

  
    function initializeSwiper() {
        const swiper = new Swiper('.swiper-container', {
            slidesPerView: 1,
                spaceBetween: 30,
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
        });
    }
});
