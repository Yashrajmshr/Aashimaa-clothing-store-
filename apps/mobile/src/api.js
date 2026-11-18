/**
 * AASHIMA ERP Mobile Client API
 * Centralized API client connecting to FastAPI Backend at http://localhost:8000/api/v1
 */

const API_BASE_URL = window.location.origin + '/api/v1';

class ApiClient {
    constructor() {
        this.token = localStorage.getItem('aashima_access_token') || null;
        this.currentUser = JSON.parse(localStorage.getItem('aashima_user_profile') || 'null');
    }

    setAuth(token, user) {
        this.token = token;
        this.currentUser = user;
        localStorage.setItem('aashima_access_token', token);
        localStorage.setItem('aashima_user_profile', JSON.stringify(user));
    }

    clearAuth() {
        this.token = null;
        this.currentUser = null;
        localStorage.removeItem('aashima_access_token');
        localStorage.removeItem('aashima_user_profile');
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, { ...options, headers });
            
            if (response.status === 401) {
                this.clearAuth();
                window.dispatchEvent(new CustomEvent('auth:expired'));
                throw new Error('Session expired. Please log in again.');
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Request failed with status ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error on [${options.method || 'GET'} ${endpoint}]:`, error);
            throw error;
        }
    }

    // Auth
    async login(username_or_phone, password) {
        const res = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username_or_phone, password })
        });
        this.setAuth(res.access_token, {
            user_id: res.user_id,
            full_name: res.full_name,
            role: res.role
        });
        return res;
    }

    // Dashboard & Metrics
    async getDashboardMetrics() {
        return await this.request('/reports/dashboard-metrics');
    }

    // Customers
    async getCustomers(search = '') {
        const query = search ? `?search=${encodeURIComponent(search)}` : '';
        return await this.request(`/customers${query}`);
    }

    async createCustomer(customerData) {
        return await this.request('/customers', {
            method: 'POST',
            body: JSON.stringify(customerData)
        });
    }

    // Services & Templates
    async getServices(division = '') {
        const query = division ? `?division=${encodeURIComponent(division)}` : '';
        return await this.request(`/services${query}`);
    }

    async getMeasurementTemplates(garmentType = '') {
        const query = garmentType ? `?garment_type=${encodeURIComponent(garmentType)}` : '';
        return await this.request(`/services/templates/measurement${query}`);
    }

    // Bookings
    async getBookings(search = '', status = '') {
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (status) params.append('status', status);
        const query = params.toString() ? `?${params.toString()}` : '';
        return await this.request(`/bookings${query}`);
    }

    async getBooking(bookingId) {
        return await this.request(`/bookings/${bookingId}`);
    }

    async createBooking(bookingData) {
        return await this.request('/bookings', {
            method: 'POST',
            body: JSON.stringify(bookingData)
        });
    }

    // Garments & QR
    async getGarment(garmentId) {
        return await this.request(`/garments/${garmentId}`);
    }

    async transitionGarmentStage(garmentId, transitionData) {
        return await this.request(`/garments/${garmentId}/transition`, {
            method: 'POST',
            body: JSON.stringify(transitionData)
        });
    }

    async scanQR(scannedText, scanContext = 'Stage Update') {
        return await this.request('/qr/scan', {
            method: 'POST',
            body: JSON.stringify({ scanned_text: scannedText, scan_context: scanContext })
        });
    }

    async generatePrintSlips(garmentIds, format = '80mm') {
        return await this.request('/qr/print-slips', {
            method: 'POST',
            body: JSON.stringify({ garment_ids: garmentIds, format })
        });
    }

    // Departments
    async getDepartmentQueue(deptName) {
        return await this.request(`/departments/${deptName}`);
    }

    // Billing & Payments
    async getDaybookSummary(dateStr = '') {
        const query = dateStr ? `?date_str=${dateStr}` : '';
        return await this.request(`/billing/daybook-summary${query}`);
    }

    async addPayment(paymentData) {
        return await this.request('/billing/payments', {
            method: 'POST',
            body: JSON.stringify(paymentData)
        });
    }

    async createInvoice(invoiceData) {
        return await this.request('/billing/invoices', {
            method: 'POST',
            body: JSON.stringify(invoiceData)
        });
    }

    // Deliveries
    async getDeliveries() {
        return await this.request('/deliveries');
    }
}

export const api = new ApiClient();
