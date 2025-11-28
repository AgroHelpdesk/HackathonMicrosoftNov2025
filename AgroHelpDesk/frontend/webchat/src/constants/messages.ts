// Loading Messages
export const LOADING_MESSAGES = {
    CONNECTING: 'Connecting to assistant...',
    STARTING_SESSION: 'Starting session...',
    SENDING: 'Sending message...',
} as const;

// Error Messages
export const ERROR_MESSAGES = {
    SESSION_FAILED: 'Failed to start session',
    SEND_FAILED: 'Failed to send message',
    NETWORK_ERROR: 'Connection error. Check your internet connection.',
    GENERIC_ERROR: 'An unexpected error occurred',
} as const;

// Placeholder Messages
export const PLACEHOLDER_MESSAGES = {
    DEFAULT: 'Type your question about agriculture...',
    SENDING: 'Sending...',
} as const;

// Success Messages
export const SUCCESS_MESSAGES = {
    MESSAGE_SENT: 'Message sent successfully',
} as const;
