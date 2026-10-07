import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function extractErrorMessage(error: any, defaultMessage: string = "An error occurred"): string {
  if (!error) return defaultMessage;
  
  const data = error.response?.data;
  if (!data) return error.message || defaultMessage;
  
  if (typeof data.detail === 'string') return data.detail;
  if (typeof data.error === 'string') return data.error;
  
  // Handle FastAPI validation array
  if (Array.isArray(data.detail) && data.detail.length > 0) {
    const firstErr = data.detail[0];
    return typeof firstErr.msg === 'string' ? firstErr.msg : JSON.stringify(firstErr);
  }
  
  return defaultMessage;
}
