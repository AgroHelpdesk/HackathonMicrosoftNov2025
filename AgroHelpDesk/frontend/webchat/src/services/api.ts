import axios, { AxiosInstance } from 'axios';
import { API_BASE_URL, TIMEOUTS } from '../constants';

/**
 * Axios instance with default configuration
 */
const api: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: TIMEOUTS.API_REQUEST,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for debugging
api.interceptors.request.use(
    (config) => {
        console.log('API Request:', config.method?.toUpperCase(), config.url);
        return config;
    },
    (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => {
        console.log('API Response:', response.status, response.config.url);
        return response;
    },
    (error) => {
        console.error('API Response Error:', error.response?.status, error.message);
        return Promise.reject(error);
    }
);

export default api;
