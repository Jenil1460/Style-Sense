import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT
api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  return config;
});

// Response interceptor to handle 401s
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If we get a 401 Unauthorized, we shouldn't automatically redirect in the client wrapper 
    // unless we have a robust refresh token flow here. For now, we pass the error down.
    if (error.response?.status === 401 && !originalRequest._retry) {
        // Here we could implement the refresh token logic if needed.
        // For now, let the AuthContext handle kicking the user to /login.
    }
    
    return Promise.reject(error);
  }
);
