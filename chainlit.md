# UWC Chatbot

<style>
/* Force light theme and prevent dark mode */
:root, [data-theme="dark"], [data-theme="light"] {
    --background: 255, 255, 255 !important; /* White */
    --primary: 0, 86, 167 !important; /* UWC Blue */
    --text-primary: 51, 51, 51 !important; /* Dark gray */
}

/* Apply to all elements */
html, body, #root, .cl-root, .cl-overlay, .cl-modal {
    background-color: rgb(var(--background)) !important;
    color: rgb(var(--text-primary)) !important;
}

/* Specific component overrides */
.cl-header, .cl-chat-header {
    background-color: rgb(var(--primary)) !important;
    color: white !important;
}

.cl-message-user {
    background-color: #FFD100 !important; /* UWC Yellow */
    color: #333333 !important;
}

.cl-message-assistant {
    background-color: #78BE20 !important; /* UWC Green */
    color: white !important;
}
</style>
