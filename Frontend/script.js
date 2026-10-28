// --- Config ---
const API_URL = "http://127.0.0.1:8000/receptionist/chat";

// --- DOM ---
const chatEl = document.getElementById("chat");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const suggestionsEl = document.getElementById("suggestions");

let isWaiting = false;
const sessionId = crypto.randomUUID();  // generated once per page load

// --- Send message to backend ---
async function sendMessage(text) {
    if (isWaiting) return;
    isWaiting = true;

    // Show user message
    addMessage(text, "user");
    inputEl.value = "";
    toggleInput(false);
    showTyping();

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text, session_id: sessionId }),
        });

        hideTyping();

        if (!response.ok) {
            if (response.status === 429) {
                addMessage(
                    "You're sending messages too quickly. Please wait a moment and try again.",
                    "error"
                );
            } else if (response.status === 502) {
                addMessage(
                    "The AI receptionist couldn't process your message. Please try again.",
                    "error"
                );
            } else {
                addMessage(`Error: ${response.status} ${response.statusText}`, "error");
            }
            return;
        }

        const data = await response.json();
        addMessage(data.reply, "assistant");

    } catch (err) {
        hideTyping();
        addMessage(
            "Couldn't reach the server. Make sure the backend is running at " + API_URL,
            "error"
        );
    } finally {
        isWaiting = false;
        toggleInput(true);
        inputEl.focus();
    }
}

// --- Add a message bubble ---
function addMessage(text, type) {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${type}`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    wrapper.appendChild(bubble);
    chatEl.appendChild(wrapper);
    scrollToBottom();
}

// --- Typing indicator ---
function showTyping() {
    const typing = document.createElement("div");
    typing.className = "typing";
    typing.id = "typing-indicator";
    typing.innerHTML = "<span></span><span></span><span></span>";
    chatEl.appendChild(typing);
    scrollToBottom();
}

function hideTyping() {
    const el = document.getElementById("typing-indicator");
    if (el) el.remove();
}

// --- Toggle input state ---
function toggleInput(enabled) {
    inputEl.disabled = !enabled;
    sendBtn.disabled = !enabled;
}

// --- Scroll to bottom ---
function scrollToBottom() {
    chatEl.scrollTop = chatEl.scrollHeight;
}

// --- Event listeners ---
formEl.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = inputEl.value.trim();
    if (text) sendMessage(text);
});

// Suggestion buttons
suggestionsEl.addEventListener("click", (e) => {
    const btn = e.target.closest(".suggestion");
    if (btn && !isWaiting) {
        sendMessage(btn.dataset.msg);
    }
});
