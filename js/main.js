// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// Form submit handler (demo placeholder)
// const contactForm = document.querySelector('.contact-form');
// if(contactForm) {
//   contactForm.addEventListener('submit', function(e) {
//     e.preventDefault();
//     alert('Форма отправлена! (демо-режим)');
//     contactForm.reset();
//   });
// }

// Chat widget behavior (VoxBot)
(function() {
  const chatInput = document.getElementById('chatInput');
  const chatSend = document.getElementById('chatSend');
  const chatMessages = document.getElementById('chatMessages');

  if (!chatInput || !chatSend || !chatMessages) return;

  function appendMessage(text, cls) {
    const el = document.createElement('div');
    el.className = cls;
    el.textContent = text;
    chatMessages.appendChild(el);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function botReply(userText) {
    const txt = userText.toLowerCase();
    if (!txt) return 'Не совсем понял — можешь переформулировать?';
    if (txt.includes('цена') || txt.includes('стоимость') || txt.includes('тариф')) {
      return 'Наши тарифы начинаются от бесплатного пилота до корпоративных решений. Хотите ссылку на тарифы?';
    }
    if (txt.includes('интегра') || txt.includes('интегр')) {
      return 'Мы поддерживаем интеграции по API, SIP, WebRTC и через мобильные SDK. Нужна помощь с архитектурой?';
    }
    if (txt.includes('демо') || txt.includes('показ')) {
      return 'Могу организовать демо — оставьте email через форму или нажмите «Запросить демо».';
    }
    if (txt.includes('привет') || txt.includes('здравств')) {
      return 'Привет! Рад помочь — расскажите, какая у вас задача?';
    }
    return 'Интересно — ' + userText + '. Могу предложить связаться с нами через форму, если нужно больше деталей.';
  }

  function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    appendMessage(text, 'user-message');
    chatInput.value = '';
    setTimeout(() => {
      const reply = botReply(text);
      appendMessage(reply, 'bot-message');
    }, 600);
  }

  chatSend.addEventListener('click', sendMessage);
  chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });
})();
