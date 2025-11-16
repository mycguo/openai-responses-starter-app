// API configuration
// Set NEXT_PUBLIC_API_URL in .env.local to point to Python backend
// Example: NEXT_PUBLIC_API_URL=http://localhost:8000
// If not set, defaults to empty string (uses Next.js API routes)

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

