// backend/static/js/chat.js

const messagesEl = document.getElementById('messages');
const welcomeEl  = document.getElementById('welcome-screen');
const inputEl    = document.getElementById('input-pergunta');
const sendBtn    = document.getElementById('send-btn');

function addMessage(text, type) {
    // Remove tela de boas-vindas na primeira mensagem
    if (welcomeEl) welcomeEl.style.display = 'none';

    const msg = document.createElement('div');
    msg.className = `message ${type}`;

    const avatarIcon = type === 'user' ? '👨‍🌾' : '🤖';
    const textFormatted = text.replace(/\n/g, '<br>');

    msg.innerHTML = `
        <div class="message-avatar">${avatarIcon}</div>
        <div class="message-bubble">${textFormatted}</div>
    `;

    messagesEl.appendChild(msg);
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function showTyping() {
    if (welcomeEl) welcomeEl.style.display = 'none';

    const typing = document.createElement('div');
    typing.className = 'message zana';
    typing.id = 'typing-indicator';
    typing.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-bubble">
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    messagesEl.appendChild(typing);
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
}

async function enviar() {
    const pergunta = inputEl.value.trim();
    if (!pergunta) return;

    addMessage(pergunta, 'user');
    inputEl.value = '';
    inputEl.disabled = true;
    sendBtn.disabled = true;
    showTyping();

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pergunta })
        });
        const data = await res.json();
        hideTyping();
        addMessage(data.resposta, 'zana');
    } catch {
        hideTyping();
        addMessage('Erro de conexão. Verifique se o servidor está rodando.', 'zana');
    }

    inputEl.disabled = false;
    sendBtn.disabled = false;
    inputEl.focus();
}

function enviarSugestao(btn) {
    inputEl.value = btn.textContent.trim().replace(/^[^\w]+/, '');
    enviar();
}

async function logout() {
    await fetch('/auth/logout', {method: 'POST'});
    window.location.href = '/login';
}