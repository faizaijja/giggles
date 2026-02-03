
        // Mobile sidebar toggle
        const mobileToggle = document.getElementById('mobileToggle');
        const sidebar = document.getElementById('sidebar');
        
        mobileToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
        
        // Login Modal
        const loginBtn = document.getElementById('loginBtn');
        const loginModal = document.getElementById('loginModal');
        const closeModal = document.getElementById('closeModal');
        
        loginBtn.addEventListener('click', () => {
            loginModal.style.display = 'flex';
        });
        
        closeModal.addEventListener('click', () => {
            loginModal.style.display = 'none';
        });
        
        window.addEventListener('click', (e) => {
            if (e.target === loginModal) {
                loginModal.style.display = 'none';
            }
        });
        
        // Accessibility features
        const increaseTextBtn = document.getElementById('increaseText');
        const decreaseTextBtn = document.getElementById('decreaseText');
        const highContrastBtn = document.getElementById('highContrast');
        const readAloudBtn = document.getElementById('readAloud');
        const simplifyLayoutBtn = document.getElementById('simplifyLayout');
        
        let fontSize = 16;
        let isHighContrast = false;
        let isSimplified = false;
        
        increaseTextBtn.addEventListener('click', () => {
            fontSize += 2;
            document.body.style.fontSize = `${fontSize}px`;
        });
        
        decreaseTextBtn.addEventListener('click', () => {
            if (fontSize > 12) {
                fontSize -= 2;
                document.body.style.fontSize = `${fontSize}px`;
            }
        });
        
        highContrastBtn.addEventListener('click', () => {
            isHighContrast = !isHighContrast;
            if (isHighContrast) {
                document.body.style.backgroundColor = '#000';
                document.body.style.color = '#fff';
            } else {
                document.body.style.backgroundColor = '';
                document.body.style.color = '';
            }
        });
        
        readAloudBtn.addEventListener('click', () => {
            alert('Text-to-speech feature would be implemented here with the Web Speech API');
        });
        
        simplifyLayoutBtn.addEventListener('click', () => {
            isSimplified = !isSimplified;
            const elements = document.querySelectorAll('.feature-card, .activity-card, .footer-section');
            if (isSimplified) {
                elements.forEach(el => {
                    el.style.animation = 'none';
                    el.style.transition = 'none';
                    el.style.boxShadow = 'none';
                });
            } else {
                elements.forEach(el => {
                    el.style.animation = '';
                    el.style.transition = '';
                    el.style.boxShadow = '';
                });
            }
        });
   