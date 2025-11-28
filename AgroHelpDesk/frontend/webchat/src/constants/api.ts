// API Endpoints - Adjusted for AgroHelpDesk backend
export const API_ENDPOINTS = {
    START_SESSION: '/chat/start_session',
    SEND_MESSAGE: '/chat/send_message',
    GET_HISTORY: '/chat/history',
    CLOSE_SESSION: '/chat/close_session',
} as const;

// API Base URL
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Timeouts (in milliseconds)
export const TIMEOUTS = {
    API_REQUEST: 30000, // 30 seconds
} as const;

// HTTP Status Codes
export const HTTP_STATUS = {
    OK: 200,
    CREATED: 201,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    INTERNAL_SERVER_ERROR: 500,
} as const;
