// Application Configuration
export const APP_CONFIG = {
    APP_NAME: 'AgroHelpDesk',
    APP_DESCRIPTION: 'Technical assistance for Agriculture',
    SUPPORT_TITLE: 'Technical assistance for Agriculture',
    DEFAULT_USER_NAME: 'User',
    BOT_NAME: 'Technical assistance for Agriculture',
} as const;

// UI Configuration
export const UI_CONFIG = {
    CHAT_HEIGHT: '700px',
    MAX_MESSAGE_WIDTH: 'max-w-2xl',
    SCROLL_BEHAVIOR: 'smooth' as const,
} as const;

// Feature Flags
export const FEATURES = {
    ENABLE_ERROR_BOUNDARY: true,
    ENABLE_LAZY_LOADING: true,
    ENABLE_AUTO_SCROLL: true,
} as const;
