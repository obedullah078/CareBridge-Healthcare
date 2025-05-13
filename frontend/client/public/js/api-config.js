/**
 * API Configuration File
 * 
 * This file contains the backend API configuration settings.
 * Change this file to update the API URL throughout the application.
 */

// Use relative URLs for API endpoints to work with Vite's proxy
// This will automatically use the same origin as the frontend
const API_BASE_URL = '';

// Set default timezone to Chicago (US Central Time)
const DEFAULT_TIMEZONE = 'America/Chicago';

// API Endpoints
const API_ENDPOINTS = {
    login: `${API_BASE_URL}/api/login`,
    register: `${API_BASE_URL}/api/register`,
    user: `${API_BASE_URL}/api/user`,
    logout: `${API_BASE_URL}/api/logout`,
    doctors: `${API_BASE_URL}/api/doctors`,
    doctorAvailability: (doctorId) => `${API_BASE_URL}/api/doctors/${doctorId}/availability`,
    patientAppointments: `${API_BASE_URL}/api/appointments/patient`,
    doctorAppointments: `${API_BASE_URL}/api/appointments/doctor`,
    createAppointment: `${API_BASE_URL}/api/appointments`,
    updateAppointment: (appointmentId) => `${API_BASE_URL}/api/appointments/${appointmentId}`,
    profile: `${API_BASE_URL}/api/profile`
};

// Helper function to format dates in Chicago timezone
function formatInChicagoTimezone(date, options = {}) {
    // Format date for display in Chicago timezone
    return new Date(date).toLocaleString('en-US', {
        ...options,
        timeZone: DEFAULT_TIMEZONE
    });
}

// Helper function to get a Date object in Chicago timezone reliably
function getChicagoDate(date = new Date()) {
    // Use Intl.DateTimeFormat to extract parts in Chicago timezone
    const formatter = new Intl.DateTimeFormat('en-US', {
        timeZone: DEFAULT_TIMEZONE,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
    const parts = formatter.formatToParts(date);
    const obj = {};
    parts.forEach(({type, value}) => { obj[type] = value; });
    // Construct an ISO-like string
    const isoString = `${obj.year}-${obj.month}-${obj.day}T${obj.hour}:${obj.minute}:${obj.second}`;
    return new Date(isoString);
}