/**
 * AASHIMA Enterprise Atelier & Dry-Clean ERP - Admin Web Portal Controller
 * Visual Reference: Google Stitch Regal Atelier Enterprise Dashboard
 */

const API_BASE = window.location.origin + '/api/v1';

class AdminApp {
    constructor() {
        this.currentTab = 'overview';
        this.token = localStorage.getItem('aashima_access_token') || null;
        this.orders = [];
        this.metrics = null;

        this.init();
    }

    async init() {
        window.adminApp = this;

        this.bindEvents();
        this.updateOperatorBadge();

        if (!this.token) {
            this.renderLogin();
            return;
        }
        await this.switchTab('overview');
    }

    updateOperatorBadge() {
        const badgeContainer = document.getElementById('operator-badge-container');
        if (!badgeContainer) return;

        if (this.token) {
            let profile = null;
            try {
                profile = JSON.parse(localStorage.getItem('aashima_user_profile') || '{}');
            } catch (e) {}
            const displayName = profile?.full_name || 'AASHIMA Staff';
            const role = profile?.role || 'Staff';
            badgeContainer.innerHTML = `
                <div class="flex flex-col overflow-hidden mr-2">
                    <span class="text-[10px] text-on-surface-variant font-bold uppercase tracking-wider">${role}</span>
                    <span id="operator-name" class="text-xs text-primary font-bold truncate" title="${displayName}">${displayName}</span>
                </div>
                <div class="flex items-center gap-1">
                    <button onclick="window.location.reload()" title="Sync Live Data" class="w-7 h-7 rounded-full bg-surface-container-lowest flex items-center justify-center text-primary shadow-sm hover:scale-105 active:scale-95 transition-transform">
                        <span class="material-symbols-outlined text-[15px]">sync</span>
                    </button>
                    <button onclick="window.adminApp.logout()" title="Sign Out" class="w-7 h-7 rounded-full bg-surface-container-lowest flex items-center justify-center text-error shadow-sm hover:scale-105 active:scale-95 transition-transform">
                        <span class="material-symbols-outlined text-[15px]">logout</span>
                    </button>
                </div>
            `;
        } else {
            badgeContainer.innerHTML = `
                <div class="flex flex-col overflow-hidden mr-2">
                    <span class="text-[10px] text-error font-bold uppercase tracking-wider">Session Inactive</span>
                    <span id="operator-name" class="text-xs text-on-surface-variant font-semibold">Please Sign In</span>
                </div>
                <button onclick="window.adminApp.renderLogin()" title="Sign In" class="px-2.5 py-1 rounded-md bg-primary-container text-white text-[11px] font-bold shadow-sm hover:opacity-90">
                    Sign In
                </button>
            `;
        }
    }

    logout() {
        this.token = null;
        localStorage.removeItem('aashima_access_token');
        localStorage.removeItem('aashima_user_profile');
        this.updateOperatorBadge();
        this.renderLogin('You have been signed out successfully.');
    }

    renderLogin(message = '') {
        const container = document.getElementById('admin-content');
        if (!container) return;
        this.updateOperatorBadge();

        container.innerHTML = `
            <div class="max-w-md mx-auto mt-8 p-8 rounded-2xl bg-surface-container-lowest border border-outline-variant/40 shadow-lg">
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-12 h-12 rounded-xl bg-primary-container text-tertiary-fixed flex items-center justify-center shadow-md">
                        <span class="material-symbols-outlined text-2xl">admin_panel_settings</span>
                    </div>
                    <div>
                        <h1 class="font-serif text-2xl font-bold text-primary leading-tight">Staff Sign In</h1>
                        <p class="text-xs text-on-surface-variant">AASHIMA Atelier & Dry-Clean ERP</p>
                    </div>
                </div>
                <p class="text-xs text-on-surface-variant leading-relaxed">Enter your staff username or registered 10-digit mobile number and password to access the counter terminal.</p>
                ${message ? `<div role="alert" class="mt-4 p-3 rounded-lg bg-error-container text-on-error-container text-xs flex items-center gap-2"><span class="material-symbols-outlined text-sm">info</span><span>${message}</span></div>` : ''}
                <form id="admin-login-form" class="mt-5 space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-on-surface mb-1">Username or mobile</label>
                        <input id="admin-login-identity" autocomplete="username" required value="owner" class="w-full p-3 rounded-lg border border-outline-variant text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none" />
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-on-surface mb-1">Password</label>
                        <input id="admin-login-password" type="password" autocomplete="current-password" required value="Password@123" class="w-full p-3 rounded-lg border border-outline-variant text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none" />
                    </div>
                    <button class="w-full min-h-11 rounded-lg bg-primary-container hover:bg-primary-container/90 text-white font-bold text-sm shadow-md active:scale-98 transition-all flex items-center justify-center gap-2" type="submit">
                        <span class="material-symbols-outlined text-[18px]">lock_open</span>
                        <span>Sign In to Atelier Counter</span>
                    </button>
                </form>
            </div>`;

        const form = document.getElementById('admin-login-form');
        if (form) {
            form.onsubmit = async (event) => {
                event.preventDefault();
                const button = event.currentTarget.querySelector('button[type="submit"]');
                button.disabled = true;
                button.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span><span>Authenticating...</span>`;
                try {
                    const response = await fetch(`${API_BASE}/auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username_or_phone: document.getElementById('admin-login-identity').value.trim(),
                            password: document.getElementById('admin-login-password').value
                        })
                    });
                    const data = await response.json().catch(() => ({}));
                    if (!response.ok) throw new Error(data.detail || 'Sign in failed. Check your credentials.');
                    this.token = data.access_token;
                    localStorage.setItem('aashima_access_token', data.access_token);
                    localStorage.setItem('aashima_user_profile', JSON.stringify({ user_id: data.user_id, full_name: data.full_name, role: data.role }));
                    this.updateOperatorBadge();
                    await this.switchTab(this.currentTab && this.currentTab !== 'login' ? this.currentTab : 'overview');
                } catch (error) {
                    this.renderLogin(error.message);
                }
            };
        }
    }

    async apiRequest(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
        if (res.status === 401) {
            this.token = null;
            localStorage.removeItem('aashima_access_token');
            localStorage.removeItem('aashima_user_profile');
            this.updateOperatorBadge();
            this.renderLogin('Your session has expired. Please sign in again.');
            const authErr = new Error('Session expired. Please sign in again.');
            authErr.isAuthExpired = true;
            throw authErr;
        }
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP Error ${res.status}`);
        }
        return await res.json();
    }

    bindEvents() {
        const searchInput = document.getElementById('global-search-input');
        if (searchInput) {
            searchInput.oninput = (e) => {
                const q = e.target.value.toLowerCase().trim();
                this.filterOrders(q);
            };
        }
    }

    async switchTab(tabName) {
        this.currentTab = tabName;
        const container = document.getElementById('admin-content');
        if (!container) return;

        if (!this.token) {
            this.renderLogin();
            return;
        }

        // Update nav tabs styling
        document.querySelectorAll('.nav-tab').forEach(btn => {
            if (btn.dataset.tab === tabName) {
                btn.className = 'nav-tab w-full flex items-center justify-between px-space-md py-space-sm rounded-lg transition-all bg-primary-container text-on-primary font-bold shadow-sm text-xs text-left';
            } else {
                btn.className = 'nav-tab w-full flex items-center justify-between px-space-md py-space-sm rounded-lg text-on-surface-variant hover:bg-surface-container-high transition-all text-xs font-semibold text-left';
            }
        });

        container.innerHTML = `
            <div class="flex items-center justify-center h-64">
                <div class="w-10 h-10 rounded-full border-4 border-primary-container border-t-transparent animate-spin"></div>
            </div>
        `;

        try {
            switch (tabName) {
                case 'overview':
                    await this.renderOverview(container);
                    break;
                case 'pipeline':
                    await this.renderPipeline(container);
                    break;
                case 'customers':
                    await this.renderCustomers(container);
                    break;
                case 'measurements':
                    await this.renderMeasurementBook(container);
                    break;
                case 'invoicing':
                    await this.renderInvoicing(container);
                    break;
                case 'qr-thermal':
                    await this.renderQRThermalCentre(container);
                    break;
                case 'expenses':
                    await this.renderExpenses(container);
                    break;
                case 'settings':
                    await this.renderSettings(container);
                    break;
                default:
                    await this.renderOverview(container);
            }
        } catch (err) {
            if (err.isAuthExpired || !this.token) {
                return;
            }
            container.innerHTML = `
                <div class="max-w-lg mx-auto mt-8 p-8 rounded-xl bg-surface-container-lowest border border-error/30 text-center text-error shadow-sm">
                    <span class="material-symbols-outlined text-4xl mb-2 text-error">error</span>
                    <h3 class="font-bold text-base">Error loading module</h3>
                    <p class="text-xs text-on-surface-variant mt-1">${err.message}</p>
                    <div class="mt-5 flex gap-2 justify-center">
                        <button onclick="window.adminApp.switchTab('${tabName}')" class="px-4 py-2 rounded-lg bg-primary-container text-white text-xs font-semibold hover:opacity-90">Retry</button>
                        <button onclick="window.adminApp.renderLogin()" class="px-4 py-2 rounded-lg bg-surface-container text-on-surface text-xs font-semibold">Sign In Again</button>
                    </div>
                </div>
            `;
        }
    }

    // ==========================================
    // MODULE 1: OVERVIEW DASHBOARD
    // ==========================================
    async renderOverview(container) {
        const metrics = await this.apiRequest('/reports/dashboard-metrics');
        const daybook = metrics.daybook || {};
        const pipeline = metrics.pipeline || {};
        const urgent = metrics.urgent_orders || [];
        this.orders = await this.apiRequest('/bookings');

        // Update pipeline count badge in sidebar
        const badge = document.getElementById('badge-pipeline-count');
        const totalInFloor = Number(pipeline.total_in_floor || 0);
        if (badge) badge.innerText = totalInFloor;

        const altCount = Number(pipeline.alteration_count || 0);
        const cleanCount = Number(pipeline.deep_clean_count || 0);
        const steamCount = Number(pipeline.steam_finishing_count || 0);
        const readyCount = Number(pipeline.trial_ready_count || 0);

        const altW = totalInFloor > 0 ? (altCount / totalInFloor * 100) : 0;
        const cleanW = totalInFloor > 0 ? (cleanCount / totalInFloor * 100) : 0;
        const steamW = totalInFloor > 0 ? (steamCount / totalInFloor * 100) : 0;
        const readyW = totalInFloor > 0 ? (readyCount / totalInFloor * 100) : 0;

        container.innerHTML = `
            <!-- Stat Cards Grid (4 High Impact Stitch Cards) -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-space-md mb-space-lg">
                <!-- Card 1: Gross Daybook Collection -->
                <div class="relative overflow-hidden rounded-xl bg-surface-container-lowest p-space-lg shadow-sm border border-outline-variant/40 flex flex-col justify-between">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Gross Daybook Total</span>
                        <span class="px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container text-[10px] font-bold">Shift #1</span>
                    </div>
                    <div class="my-space-sm flex items-baseline gap-1">
                        <span class="font-serif text-3xl font-bold text-primary leading-none">₹${Number(daybook.collected_today || 0).toLocaleString('en-IN')}</span>
                    </div>
                    <div class="flex items-center justify-between text-xs text-on-surface-variant">
                        <span>Avg Ticket: ₹${Number(daybook.avg_ticket_value || 0).toFixed(0)}</span>
                        <span class="font-bold text-on-tertiary-container">${daybook.slips_billed_count || 0} Slips Billed</span>
                    </div>
                </div>

                <!-- Card 2: Karkhana Live Pipeline -->
                <div class="relative overflow-hidden rounded-xl bg-surface-container-lowest p-space-lg shadow-sm border border-outline-variant/40 flex flex-col justify-between">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Karkhana Live Pipeline</span>
                        <span class="px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container text-[10px] font-bold">${totalInFloor} In Floor</span>
                    </div>
                    <div class="my-space-sm flex items-baseline gap-1">
                        <span class="font-serif text-3xl font-bold text-on-surface leading-none">${totalInFloor}</span>
                        <span class="text-xs text-on-surface-variant">pieces in workshop</span>
                    </div>
                    <!-- Micro breakdown bar -->
                    <div class="flex flex-col gap-1">
                        <div class="h-2 w-full rounded-full bg-surface-container flex overflow-hidden">
                            <div class="h-full bg-tertiary-fixed-dim" style="width: ${altW}%" title="Alterations"></div>
                            <div class="h-full bg-secondary" style="width: ${cleanW}%" title="Deep Clean"></div>
                            <div class="h-full bg-primary-container" style="width: ${steamW}%" title="Steam Finishing"></div>
                            <div class="h-full bg-success" style="width: ${readyW}%" title="Ready for Handover"></div>
                        </div>
                        <div class="flex justify-between text-[10px] text-on-surface-variant">
                            <span>${altCount} Alt</span>
                            <span>${cleanCount} Clean</span>
                            <span>${steamCount} Steam</span>
                            <span>${readyCount} Ready</span>
                        </div>
                    </div>
                </div>

                <!-- Card 3: Urgent Deliveries -->
                <div class="relative overflow-hidden rounded-xl bg-surface-container-lowest p-space-lg shadow-sm border border-outline-variant/40 flex flex-col justify-between">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Urgent Deliveries</span>
                        <span class="px-2 py-0.5 rounded-full ${urgent.length > 0 ? 'bg-error-container text-on-error-container' : 'bg-surface-container text-on-surface-variant'} text-[10px] font-bold flex items-center gap-0.5">
                            <span class="material-symbols-outlined text-[13px]">alarm</span>
                            ${urgent.length} Critical
                        </span>
                    </div>
                    <div class="my-space-sm flex items-baseline gap-1">
                        <span class="font-serif text-3xl font-bold ${urgent.length > 0 ? 'text-error' : 'text-on-surface'} leading-none">${urgent.length}</span>
                        <span class="text-xs text-on-surface-variant">${urgent.length > 0 ? 'Expedited Orders' : 'On Schedule'}</span>
                    </div>
                    <div class="flex items-center justify-between text-xs text-on-surface-variant">
                        <span>${urgent.length > 0 ? 'Prioritized at Counter' : 'No Critical Flags'}</span>
                        <span class="${urgent.length > 0 ? 'text-error font-bold' : 'text-success font-semibold'}">${urgent.length > 0 ? `${urgent.length} pending handover` : 'All Timelines Clear'}</span>
                    </div>
                </div>

                <!-- Card 4: Cash & UPI Daybook Position -->
                <div class="relative overflow-hidden rounded-xl bg-surface-container-lowest p-space-lg shadow-sm border border-outline-variant/40 flex flex-col justify-between">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Counter Daybook Ledger</span>
                        <span class="px-2 py-0.5 rounded-full bg-surface-container-high text-on-surface text-[10px] font-semibold">Shift Active</span>
                    </div>
                    <div class="my-space-sm flex items-baseline justify-between">
                        <div>
                            <span class="text-[10px] text-on-surface-variant block">Collected</span>
                            <span class="font-serif text-xl font-bold text-primary">₹${Number(daybook.collected_today || 0).toLocaleString('en-IN')}</span>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-on-surface-variant block">Pending Balance</span>
                            <span class="font-serif text-xl font-bold text-error">₹${Number(daybook.pending_balance || 0).toLocaleString('en-IN')}</span>
                        </div>
                    </div>
                    <div class="flex items-center justify-between text-[11px] text-on-surface-variant">
                        <span>UPI: ₹${Number(daybook.upi_collected || 0).toLocaleString('en-IN')}</span>
                        <span>Cash: ₹${Number(daybook.cash_collected || 0).toLocaleString('en-IN')}</span>
                    </div>
                </div>
            </div>

            <!-- Quick Counter Actions Toolbar -->
            <div class="rounded-xl bg-surface-container-lowest p-space-md shadow-sm border border-outline-variant/40 flex flex-wrap items-center justify-between gap-space-md mb-space-lg">
                <div class="flex flex-wrap items-center gap-space-sm">
                    <button onclick="window.adminApp.openNewBookingModal()" class="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-primary-container text-on-primary text-xs font-bold shadow-sm hover:brightness-110 active:scale-95 transition-all">
                        <span class="material-symbols-outlined text-[16px]">add_circle</span>
                        <span>New Intake Order</span>
                    </button>
                    <button onclick="window.adminApp.switchTab('pipeline')" class="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-surface-container hover:bg-surface-container-high text-on-surface text-xs font-semibold transition-all">
                        <span class="material-symbols-outlined text-[16px] text-secondary">view_kanban</span>
                        <span>Interactive Kanban</span>
                    </button>
                    <button onclick="window.adminApp.switchTab('qr-thermal')" class="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-surface-container hover:bg-surface-container-high text-on-surface text-xs font-semibold transition-all">
                        <span class="material-symbols-outlined text-[16px] text-tertiary">print</span>
                        <span>Batch Thermal Roll</span>
                    </button>
                </div>
                <div class="text-xs text-on-surface-variant">
                    Showing <b class="text-primary">${this.orders.length}</b> live production orders
                </div>
            </div>

            <!-- Active Production Orders Table (Stitch Reference) -->
            <div class="rounded-xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm overflow-hidden">
                <div class="p-4 border-b border-outline-variant/30 flex items-center justify-between">
                    <div>
                        <h3 class="font-serif text-base font-bold text-primary">Active Production Orders</h3>
                        <p class="text-xs text-on-surface-variant">Real-time atelier queue synchronized across Turab Nagar counter and karigari stations</p>
                    </div>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-surface-container-low text-on-surface-variant font-bold uppercase tracking-wider text-[10px] border-b border-outline-variant/30">
                            <tr>
                                <th class="p-3.5">Order ID</th>
                                <th class="p-3.5">Client & Contact</th>
                                <th class="p-3.5">Articles & Services</th>
                                <th class="p-3.5">Karigar / Wing</th>
                                <th class="p-3.5">Fitting Deadline</th>
                                <th class="p-3.5">Billing Status</th>
                                <th class="p-3.5">Workflow Stage</th>
                                <th class="p-3.5 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="orders-table-body" class="divide-y divide-outline-variant/20">
                            ${this.renderOrderRows(this.orders)}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    renderOrderRows(orders) {
        if (!orders || orders.length === 0) {
            return `<tr><td colspan="8" class="p-12 text-center text-xs text-on-surface-variant"><div class="flex flex-col items-center justify-center gap-2"><span class="material-symbols-outlined text-[36px] text-outline">inventory_2</span><span class="font-bold text-sm text-primary">No Active Production Orders</span><span>Intake your first customer order via the POS counter to populate the workshop queue.</span></div></td></tr>`;
        }

        return orders.map(o => {
            const firstGarment = o.garments && o.garments[0];
            const garmentCount = o.garments ? o.garments.length : 1;
            const isDueSoon = o.is_urgent;

            return `
                <tr class="hover:bg-surface-container-low/60 transition-colors">
                    <td class="p-3.5 font-mono font-bold text-primary whitespace-nowrap">
                        #${o.booking_number}
                        ${o.is_urgent ? '<span class="ml-1 px-1.5 py-0.2 rounded bg-error-container text-on-error-container text-[9px] font-bold">URGENT</span>' : ''}
                    </td>
                    <td class="p-3.5">
                        <div class="font-bold text-on-surface">${o.customer?.full_name || 'Counter Customer'}</div>
                        <div class="text-[11px] text-on-surface-variant">${o.customer?.phone || 'N/A'}${o.customer?.unit_reference ? ` • ${o.customer.unit_reference}` : ''}</div>
                    </td>
                    <td class="p-3.5">
                        <div class="font-semibold text-on-surface">${firstGarment?.garment_name || 'Bespoke Garment'}</div>
                        <div class="text-[11px] text-on-surface-variant">${garmentCount > 1 ? `+${garmentCount - 1} more articles • ` : ''}${o.division}</div>
                    </td>
                    <td class="p-3.5">
                        <div class="font-semibold text-on-surface">${firstGarment?.karigar_name || 'Workshop Floor'}</div>
                        <div class="text-[10px] text-secondary font-mono">${firstGarment?.rack_location || 'Intake Counter'}</div>
                    </td>
                    <td class="p-3.5 whitespace-nowrap">
                        <div class="font-semibold ${isDueSoon ? 'text-error font-bold' : 'text-on-surface'}">
                            ${new Date(o.delivery_due_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                        </div>
                        <div class="text-[10px] text-on-surface-variant">Trial: ${o.trial_due_date ? new Date(o.trial_due_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }) : 'Standard'}</div>
                    </td>
                    <td class="p-3.5 whitespace-nowrap">
                        <div class="font-mono font-bold text-on-surface">₹${Number(o.net_amount).toFixed(2)}</div>
                        <div class="text-[10px] ${o.balance_due > 0 ? 'text-error font-bold' : 'text-success'}">
                            ${o.balance_due > 0 ? `Due: ₹${Number(o.balance_due).toFixed(2)}` : 'Fully Settled'}
                        </div>
                    </td>
                    <td class="p-3.5 whitespace-nowrap">
                        <span class="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                            o.current_status === 'Delivered' ? 'bg-success/15 text-success' :
                            o.current_status === 'Ready for Delivery' ? 'bg-tertiary-fixed text-on-tertiary-fixed' :
                            'bg-secondary-container text-on-secondary-container'
                        }">
                            ${o.current_status}
                        </span>
                    </td>
                    <td class="p-3.5 text-right whitespace-nowrap">
                        <div class="flex items-center justify-end gap-1">
                            <button onclick="window.adminApp.openThermalSlip(${o.id})" title="Print 80mm Slip" class="w-7 h-7 rounded-lg bg-surface-container flex items-center justify-center text-primary hover:bg-primary-container hover:text-white transition-colors">
                                <span class="material-symbols-outlined text-[16px]">receipt_long</span>
                            </button>
                            <a href="/api/v1/billing/invoices/${o.id}/pdf" target="_blank" title="Download Tax Invoice" class="w-7 h-7 rounded-lg bg-surface-container flex items-center justify-center text-secondary hover:bg-secondary hover:text-white transition-colors">
                                <span class="material-symbols-outlined text-[16px]">download</span>
                            </a>
                            <button onclick="window.adminApp.deleteBooking(${o.id}, '${o.booking_number}')" title="Delete Order Entry" class="w-7 h-7 rounded-lg bg-error-container/20 flex items-center justify-center text-error hover:bg-error hover:text-white transition-colors">
                                <span class="material-symbols-outlined text-[16px]">delete</span>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    filterOrders(query) {
        const filtered = this.orders.filter(o => {
            const num = (o.booking_number || '').toLowerCase();
            const name = (o.customer?.full_name || '').toLowerCase();
            const phone = (o.customer?.phone || '').toLowerCase();
            return num.includes(query) || name.includes(query) || phone.includes(query);
        });
        const tbody = document.getElementById('orders-table-body');
        if (tbody) tbody.innerHTML = this.renderOrderRows(filtered);
    }

    // ==========================================
    // MODULE 2: KARKHANA PIPELINE (KANBAN)
    // ==========================================
    async renderPipeline(container) {
        const columns = [
            { key: 'Booking Received', title: 'Intake & Inspection', color: 'bg-surface-container-high' },
            { key: 'Alteration', title: 'Alteration & Karigari', color: 'bg-tertiary-fixed-dim/40' },
            { key: 'Deep Cleaning', title: 'Deep Cleaning Care', color: 'bg-secondary-container/40' },
            { key: 'Finishing', title: 'Steam Polish & Finishing', color: 'bg-primary-fixed/40' },
            { key: 'Ready for Delivery', title: 'Ready for Trial / Handover', color: 'bg-tertiary-fixed/60' },
            { key: 'Delivered', title: 'Handed Over / Delivered', color: 'bg-success/15' }
        ];

        const allBookings = await this.apiRequest('/bookings');

        container.innerHTML = `
            <div class="mb-4 flex items-center justify-between">
                <div>
                    <h2 class="font-serif text-xl font-bold text-primary">Karkhana Live Pipeline Board</h2>
                    <p class="text-xs text-on-surface-variant">Real-time floor flow across Turab Nagar artisan stations</p>
                </div>
                <div class="flex items-center gap-2">
                    <span class="px-2.5 py-1 rounded-full bg-secondary-container text-on-secondary-container text-xs font-bold">Auto-sync 30s</span>
                </div>
            </div>

            <!-- Kanban Column Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3 min-h-[600px]">
                ${columns.map(col => {
                    const colOrders = allBookings.filter(b => b.current_status === col.key);
                    return `
                        <div class="flex flex-col rounded-xl bg-surface-container-low border border-outline-variant/40 p-2.5 shadow-sm">
                            <div class="flex items-center justify-between pb-2 mb-2 border-b border-outline-variant/30">
                                <span class="text-xs font-bold text-on-surface truncate">${col.title}</span>
                                <span class="px-2 py-0.2 rounded-full ${col.color} text-on-surface font-bold text-[10px]">${colOrders.length}</span>
                            </div>

                            <div class="flex-1 space-y-2 overflow-y-auto max-h-[700px]">
                                ${colOrders.length > 0 ? colOrders.map(o => `
                                    <div class="p-3 rounded-lg bg-surface-container-lowest border border-outline-variant/40 shadow-sm space-y-1.5 hover:shadow-md transition-shadow">
                                        <div class="flex justify-between items-start">
                                            <span class="font-mono text-[10px] font-bold text-primary">#${o.booking_number}</span>
                                            <span class="text-[9px] font-bold text-on-surface-variant">${new Date(o.delivery_due_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })}</span>
                                        </div>
                                        <h4 class="text-xs font-bold text-on-surface truncate">${o.customer?.full_name}</h4>
                                        <p class="text-[11px] text-on-surface-variant truncate">${o.garments[0]?.garment_name || 'Bespoke Garment'}</p>
                                        <div class="pt-1 flex items-center justify-between border-t border-outline-variant/20 text-[10px]">
                                            <a href="/?booking=${o.booking_number}" target="_blank" class="text-secondary hover:underline font-bold" title="Open Customer Live Tracker">Track</a>
                                            <div class="flex items-center gap-2">
                                                <button onclick="window.adminApp.openThermalSlip(${o.id})" class="text-primary hover:underline font-bold">Print Tag</button>
                                                <button onclick="window.adminApp.deleteBooking(${o.id}, '${o.booking_number}')" class="text-error hover:underline font-bold" title="Delete Order">Delete</button>
                                            </div>
                                        </div>
                                    </div>
                                `).join('') : `
                                    <div class="h-28 rounded-lg border border-dashed border-outline-variant/50 flex flex-col items-center justify-center p-2 text-center text-[10px] text-outline">
                                        <span class="material-symbols-outlined text-[18px] mb-0.5 opacity-60">hourglass_empty</span>
                                        <span>No items in queue</span>
                                    </div>
                                `}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }

    // ==========================================
    // MODULE 3: CUSTOMER REGISTRY
    // ==========================================
    async renderCustomers(container) {
        const customers = await this.apiRequest('/customers');
        container.innerHTML = `
            <div class="rounded-xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm overflow-hidden">
                <div class="p-4 border-b border-outline-variant/30 flex items-center justify-between">
                    <div>
                        <h3 class="font-serif text-base font-bold text-primary">Patron Registry Ledger</h3>
                        <p class="text-xs text-on-surface-variant">Permanent archive of client fittings, lifetime spend, and past dues</p>
                    </div>
                    <span class="text-xs font-bold text-on-surface-variant">${customers.length} Registered Patrons</span>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-surface-container-low text-on-surface-variant font-bold uppercase tracking-wider text-[10px] border-b border-outline-variant/30">
                            <tr>
                                <th class="p-3.5">Code</th>
                                <th class="p-3.5">Client Name</th>
                                <th class="p-3.5">Registered Phone</th>
                                <th class="p-3.5">Patron Tier</th>
                                <th class="p-3.5">Unit Reference</th>
                                <th class="p-3.5">Total Orders</th>
                                <th class="p-3.5">Lifetime Spend</th>
                                <th class="p-3.5">Outstanding Dues</th>
                                <th class="p-3.5 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-outline-variant/20">
                            ${customers.length > 0 ? customers.map(c => `
                                <tr class="hover:bg-surface-container-low/60 transition-colors">
                                    <td class="p-3.5 font-mono font-bold text-primary">${c.customer_code}</td>
                                    <td class="p-3.5 font-bold text-on-surface">${c.full_name}</td>
                                    <td class="p-3.5 font-mono text-on-surface-variant">${c.phone}</td>
                                    <td class="p-3.5">
                                        <span class="px-2 py-0.5 rounded-full bg-tertiary-fixed text-on-tertiary-fixed text-[10px] font-bold">
                                            ${c.patron_tier}
                                        </span>
                                    </td>
                                    <td class="p-3.5 text-on-surface-variant">${c.unit_reference || 'Counter'}</td>
                                    <td class="p-3.5 font-bold text-on-surface">${c.total_orders}</td>
                                    <td class="p-3.5 font-mono text-primary font-bold">₹${Number(c.lifetime_spend).toFixed(2)}</td>
                                    <td class="p-3.5 font-mono ${c.outstanding_dues > 0 ? 'text-error font-bold' : 'text-success'}">₹${Number(c.outstanding_dues).toFixed(2)}</td>
                                    <td class="p-3.5 text-right whitespace-nowrap">
                                        <button onclick="window.adminApp.deleteCustomer(${c.id}, '${c.full_name}')" title="Delete Patron" class="w-7 h-7 rounded-lg bg-error-container/20 flex items-center justify-center text-error hover:bg-error hover:text-white transition-colors ml-auto">
                                            <span class="material-symbols-outlined text-[16px]">delete</span>
                                        </button>
                                    </td>
                                </tr>
                            `).join('') : `
                                <tr><td colspan="9" class="p-12 text-center text-xs text-on-surface-variant"><div class="flex flex-col items-center justify-center gap-2"><span class="material-symbols-outlined text-[36px] text-outline">people</span><span class="font-bold text-sm text-primary">No Registered Patrons</span><span>Customer profiles and lifetime fitting dossiers are created automatically during POS order intake.</span></div></td></tr>
                            `}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // ==========================================
    // MODULE 4: MEASUREMENT BOOK (MEN'S & WOMEN'S)
    // ==========================================
    async renderMeasurementBook(container, filterGender = 'All') {
        const [templates, recorded] = await Promise.all([
            this.apiRequest('/services/templates/measurement'),
            this.apiRequest('/services/measurements/records').catch(() => [])
        ]);

        const filteredTemplates = filterGender === 'All'
            ? templates
            : templates.filter(t => (t.silhouette_icon || 'Women').toLowerCase() === filterGender.toLowerCase());

        const mensCount = templates.filter(t => (t.silhouette_icon || '').toLowerCase() === 'men').length;
        const womensCount = templates.filter(t => (t.silhouette_icon || '').toLowerCase() !== 'men').length;

        container.innerHTML = `
            <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div>
                    <h2 class="font-serif text-xl font-bold text-primary">Atelier Measurement Master Book</h2>
                    <p class="text-xs text-on-surface-variant">Bespoke tailoring matrices for Men's Stitchers 'N' Drapers & Women's World</p>
                </div>
                <div class="flex items-center gap-1.5 bg-surface-container p-1 rounded-xl border border-outline-variant/40">
                    <button onclick="window.adminApp.renderMeasurementBook(document.getElementById('admin-content'), 'All')" class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${filterGender === 'All' ? 'bg-primary-container text-on-primary shadow-sm' : 'text-on-surface-variant hover:text-primary'}">
                        All (${templates.length})
                    </button>
                    <button onclick="window.adminApp.renderMeasurementBook(document.getElementById('admin-content'), 'Men')" class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${filterGender === 'Men' ? 'bg-primary-container text-on-primary shadow-sm' : 'text-on-surface-variant hover:text-primary'}">
                        Men's Tailoring (${mensCount})
                    </button>
                    <button onclick="window.adminApp.renderMeasurementBook(document.getElementById('admin-content'), 'Women')" class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${filterGender === 'Women' ? 'bg-primary-container text-on-primary shadow-sm' : 'text-on-surface-variant hover:text-primary'}">
                        Women's Couture (${womensCount})
                    </button>
                </div>
            </div>

            <!-- Measurement Specification Matrices -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-space-md mb-8">
                ${filteredTemplates.map(t => {
                    const fields = JSON.parse(t.anchor_fields || '[]');
                    const isMen = (t.silhouette_icon || '').toLowerCase() === 'men';
                    return `
                        <div class="p-4 rounded-xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm space-y-3 flex flex-col justify-between">
                            <div>
                                <div class="flex items-center justify-between pb-2 border-b border-outline-variant/30 gap-2">
                                    <div class="min-w-0">
                                        <span class="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider ${isMen ? 'bg-primary/10 text-primary' : 'bg-secondary-container text-on-secondary-container'}">
                                            ${isMen ? "Men's Bespoke" : "Women's Couture"}
                                        </span>
                                        <h3 class="font-serif text-sm font-bold text-primary mt-1 truncate">${t.display_title}</h3>
                                    </div>
                                    <span class="px-2 py-0.5 rounded bg-surface-container text-[10px] font-bold text-secondary shrink-0">Step: ${t.step_increment}"</span>
                                </div>

                                <div class="grid grid-cols-2 gap-1.5 text-xs mt-3">
                                    ${fields.map(f => `
                                        <div class="p-2 rounded bg-surface-container-low flex flex-col justify-between border border-outline-variant/20">
                                            <span class="text-[11px] font-semibold text-on-surface">${f.label}</span>
                                            <span class="font-mono text-[10px] text-on-surface-variant">Spec: ${f.min}"–${f.max}"</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>

                            <p class="text-[11px] text-on-surface-variant bg-surface-container-low p-2.5 rounded border border-outline-variant/20">
                                <b>Tailoring Notes:</b> ${t.special_directives_placeholder || 'Standard atelier fitting allowance'}
                            </p>
                        </div>
                    `;
                }).join('')}
            </div>

            <!-- Real Recorded Client Measurements Ledger -->
            <div class="rounded-xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm overflow-hidden">
                <div class="p-4 border-b border-outline-variant/30 flex items-center justify-between">
                    <div>
                        <h3 class="font-serif text-base font-bold text-primary">Recorded Client Measurements</h3>
                        <p class="text-xs text-on-surface-variant">Live saved tailoring dimensions linked to customer bookings</p>
                    </div>
                    <span class="text-xs font-bold text-on-surface-variant">${recorded.length} Saved Dossiers</span>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-surface-container-low text-on-surface-variant font-bold uppercase tracking-wider text-[10px] border-b border-outline-variant/30">
                            <tr>
                                <th class="p-3.5">Booking #</th>
                                <th class="p-3.5">Client & Phone</th>
                                <th class="p-3.5">Garment & Matrix</th>
                                <th class="p-3.5">Recorded Dimensions</th>
                                <th class="p-3.5">Karigar Directives</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-outline-variant/20">
                            ${recorded.length > 0 ? recorded.map(r => {
                                const dims = Object.entries(r.measurements || {})
                                    .map(([k, v]) => `<span class="inline-block px-1.5 py-0.5 rounded bg-surface-container font-mono text-[10px] mr-1 mb-1"><b>${k.replace(/_/g, ' ')}:</b> ${v}${r.unit === 'CM' ? 'cm' : '"'}</span>`)
                                    .join('');
                                return `
                                    <tr class="hover:bg-surface-container-low/60 transition-colors">
                                        <td class="p-3.5 font-mono font-bold text-primary whitespace-nowrap">#${r.booking_number}</td>
                                        <td class="p-3.5">
                                            <div class="font-bold text-on-surface">${r.customer_name}</div>
                                            <div class="text-[11px] font-mono text-on-surface-variant">${r.customer_phone}</div>
                                        </td>
                                        <td class="p-3.5">
                                            <div class="font-semibold text-on-surface">${r.garment_name}</div>
                                            <div class="text-[10px] text-secondary font-bold">${r.garment_type}</div>
                                        </td>
                                        <td class="p-3.5 max-w-md">${dims || '<span class="text-outline">No dimensions</span>'}</td>
                                        <td class="p-3.5 text-on-surface-variant">${r.karigar_directives || '—'}</td>
                                    </tr>
                                `;
                            }).join('') : `
                                <tr>
                                    <td colspan="5" class="p-10 text-center text-xs text-on-surface-variant">
                                        <div class="flex flex-col items-center justify-center gap-2">
                                            <span class="material-symbols-outlined text-[32px] text-outline">straighten</span>
                                            <span class="font-bold text-sm text-primary">No Client Measurements Recorded Yet</span>
                                            <span>Capture real Men's or Women's tailoring measurements during New Counter Booking or Mobile POS intake.</span>
                                        </div>
                                    </td>
                                </tr>
                            `}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // ==========================================
    // MODULE 5: GST INVOICING & FINANCIALS
    // ==========================================
    async renderInvoicing(container) {
        const invoices = await this.apiRequest('/billing/invoices');
        container.innerHTML = `
            <div class="rounded-xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm overflow-hidden">
                <div class="p-4 border-b border-outline-variant/30 flex items-center justify-between">
                    <div>
                        <h3 class="font-serif text-base font-bold text-primary">GST Invoicing & Tax Ledger</h3>
                        <p class="text-xs text-on-surface-variant">581 Turab Nagar Flagship • GSTIN: 09AABCA1234F1Z8</p>
                    </div>
                    <span class="text-xs font-bold text-on-surface-variant">${invoices.length} Invoices Generated</span>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-surface-container-low text-on-surface-variant font-bold uppercase tracking-wider text-[10px] border-b border-outline-variant/30">
                            <tr>
                                <th class="p-3.5">Invoice #</th>
                                <th class="p-3.5">Date</th>
                                <th class="p-3.5">Type</th>
                                <th class="p-3.5">Subtotal</th>
                                <th class="p-3.5">CGST (2.5%)</th>
                                <th class="p-3.5">SGST (2.5%)</th>
                                <th class="p-3.5">Grand Total</th>
                                <th class="p-3.5">Paid</th>
                                <th class="p-3.5">Balance</th>
                                <th class="p-3.5 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-outline-variant/20">
                            ${invoices.length > 0 ? invoices.map(inv => `
                                <tr class="hover:bg-surface-container-low/60 transition-colors">
                                    <td class="p-3.5 font-mono font-bold text-primary">${inv.invoice_number}</td>
                                    <td class="p-3.5 text-on-surface-variant">${new Date(inv.invoice_date).toLocaleDateString('en-GB')}</td>
                                    <td class="p-3.5">
                                        <span class="px-2 py-0.5 rounded bg-surface-container font-bold text-[10px]">${inv.invoice_type}</span>
                                    </td>
                                    <td class="p-3.5 font-mono">₹${Number(inv.subtotal_amount).toFixed(2)}</td>
                                    <td class="p-3.5 font-mono">₹${Number(inv.cgst_amount).toFixed(2)}</td>
                                    <td class="p-3.5 font-mono">₹${Number(inv.sgst_amount).toFixed(2)}</td>
                                    <td class="p-3.5 font-mono font-bold text-primary">₹${Number(inv.grand_total).toFixed(2)}</td>
                                    <td class="p-3.5 font-mono text-success">₹${Number(inv.paid_amount).toFixed(2)}</td>
                                    <td class="p-3.5 font-mono ${inv.outstanding_balance > 0 ? 'text-error font-bold' : 'text-on-surface-variant'}">₹${Number(inv.outstanding_balance).toFixed(2)}</td>
                                    <td class="p-3.5 text-right whitespace-nowrap">
                                        <div class="flex items-center justify-end gap-1">
                                            <a href="/api/v1/billing/invoices/${inv.id}/pdf" target="_blank" title="Download Tax Invoice" class="px-2.5 py-1.5 rounded-lg bg-primary-container text-white text-[11px] font-bold inline-flex items-center gap-1 hover:brightness-110">
                                                <span class="material-symbols-outlined text-[14px]">download</span>
                                                <span>Tax PDF</span>
                                            </a>
                                            <button onclick="window.adminApp.deleteInvoice(${inv.id}, '${inv.invoice_number}')" title="Delete Invoice Entry" class="w-7 h-7 rounded-lg bg-error-container/20 flex items-center justify-center text-error hover:bg-error hover:text-white transition-colors">
                                                <span class="material-symbols-outlined text-[16px]">delete</span>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            `).join('') : `
                                <tr><td colspan="10" class="p-12 text-center text-xs text-on-surface-variant"><div class="flex flex-col items-center justify-center gap-2"><span class="material-symbols-outlined text-[36px] text-outline">receipt</span><span class="font-bold text-sm text-primary">No Tax Invoices Generated</span><span>Invoices are compiled with legal GST/Non-GST compliance automatically upon booking settlement.</span></div></td></tr>
                            `}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // ==========================================
    // MODULE 6: QR & THERMAL ROLL PRINTING
    // ==========================================
    async renderQRThermalCentre(container) {
        const bookings = await this.apiRequest('/bookings');
        container.innerHTML = `
            <div class="mb-4">
                <h2 class="font-serif text-xl font-bold text-primary">QR Barcode & Thermal Roll Printing Centre</h2>
                <p class="text-xs text-on-surface-variant">Batch printing for 58mm & 80mm ESC/POS rolls and A4 adhesive label sheets</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-space-md">
                ${bookings.length > 0 ? bookings.slice(0, 6).map(b => `
                    <div class="p-4 rounded-xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm space-y-3">
                        <div class="flex justify-between items-start">
                            <div>
                                <span class="font-mono text-xs font-bold text-primary">#${b.booking_number}</span>
                                <h4 class="text-xs font-bold text-on-surface mt-0.5">${b.customer?.full_name}</h4>
                            </div>
                            <span class="px-2 py-0.5 rounded-full bg-surface-container text-xs font-bold text-secondary">${b.garments?.length || 1} Tags</span>
                        </div>

                        <div class="bg-surface-container-low p-2.5 rounded-lg text-xs font-mono space-y-1">
                            <div>Article: ${b.garments[0]?.garment_name}</div>
                            <div>Rack: ${b.garments[0]?.rack_location || 'Floor Queue'}</div>
                            <div>Due: ${new Date(b.delivery_due_date).toLocaleDateString()}</div>
                        </div>

                        <div class="flex gap-2">
                            <button onclick="window.adminApp.openThermalSlip(${b.id})" class="flex-1 py-2 rounded-lg bg-primary-container text-white text-xs font-bold shadow flex items-center justify-center gap-1">
                                <span class="material-symbols-outlined text-[16px]">receipt_long</span>
                                <span>80mm Slip</span>
                            </button>
                            <button onclick="window.print()" class="px-3 py-2 rounded-lg bg-surface-container text-on-surface text-xs font-bold">
                                A4 Sheet
                            </button>
                        </div>
                    </div>
                `).join('') : `
                    <div class="col-span-full p-12 rounded-xl bg-surface-container-lowest border border-outline-variant/40 text-center text-xs text-on-surface-variant">
                        <div class="flex flex-col items-center justify-center gap-2">
                            <span class="material-symbols-outlined text-[36px] text-outline">qr_code_2</span>
                            <span class="font-bold text-sm text-primary">No Active Print Batches</span>
                            <span>Garment QR tags will be available for batch thermal printing once new counter orders are placed.</span>
                        </div>
                    </div>
                `}
            </div>
        `;
    }

    // ==========================================
    // MODULE 7: EXPENSES
    // ==========================================
    async renderExpenses(container) {
        const expenses = await this.apiRequest('/billing/expenses');
        container.innerHTML = `
            <div class="rounded-xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm overflow-hidden">
                <div class="p-4 border-b border-outline-variant/30 flex items-center justify-between">
                    <div>
                        <h3 class="font-serif text-base font-bold text-primary">Atelier Expense Ledger</h3>
                        <p class="text-xs text-on-surface-variant">Materials, threads, chemicals, karigar advances, and shop overheads</p>
                    </div>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-surface-container-low text-on-surface-variant font-bold uppercase tracking-wider text-[10px] border-b border-outline-variant/30">
                            <tr>
                                <th class="p-3.5">Expense #</th>
                                <th class="p-3.5">Category</th>
                                <th class="p-3.5">Title</th>
                                <th class="p-3.5">Paid To</th>
                                <th class="p-3.5">Mode</th>
                                <th class="p-3.5">Amount</th>
                                <th class="p-3.5 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-outline-variant/20">
                            ${expenses.length > 0 ? expenses.map(e => `
                                <tr>
                                    <td class="p-3.5 font-mono font-bold text-primary">${e.expense_number}</td>
                                    <td class="p-3.5">${e.category}</td>
                                    <td class="p-3.5 font-semibold text-on-surface">${e.title}</td>
                                    <td class="p-3.5">${e.paid_to}</td>
                                    <td class="p-3.5">${e.payment_mode}</td>
                                    <td class="p-3.5 font-mono font-bold text-error">₹${Number(e.amount).toFixed(2)}</td>
                                    <td class="p-3.5 text-right whitespace-nowrap">
                                        <button onclick="window.adminApp.deleteExpense(${e.id}, '${e.expense_number}')" title="Delete Expense" class="w-7 h-7 rounded-lg bg-error-container/20 flex items-center justify-center text-error hover:bg-error hover:text-white transition-colors ml-auto">
                                            <span class="material-symbols-outlined text-[16px]">delete</span>
                                        </button>
                                    </td>
                                </tr>
                            `).join('') : `
                                <tr><td colspan="7" class="p-8 text-center text-xs text-on-surface-variant">No workshop expenses recorded today.</td></tr>
                            `}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // ==========================================
    // MODULE 8: SETTINGS
    // ==========================================
    async renderSettings(container) {
        container.innerHTML = `
            <div class="max-w-2xl bg-surface-container-lowest rounded-xl border border-outline-variant/40 p-6 shadow-sm space-y-4">
                <h3 class="font-serif text-lg font-bold text-primary">Atelier Business & Hardware Configuration</h3>

                <div class="space-y-3 text-xs">
                    <div>
                        <label class="font-bold text-on-surface-variant block mb-1">Business Name</label>
                        <input type="text" value="AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers" class="w-full p-2.5 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none"/>
                    </div>
                    <div>
                        <label class="font-bold text-on-surface-variant block mb-1">Flagship Address</label>
                        <input type="text" value="581, Turab Nagar, Ghaziabad, Uttar Pradesh, 201001, India" class="w-full p-2.5 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none"/>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="font-bold text-on-surface-variant block mb-1">GSTIN</label>
                            <input type="text" value="09AABCA1234F1Z8" class="w-full p-2.5 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none font-mono"/>
                        </div>
                        <div>
                            <label class="font-bold text-on-surface-variant block mb-1">Phone</label>
                            <input type="text" value="+91 98102 44321" class="w-full p-2.5 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none"/>
                        </div>
                    </div>
                    <div>
                        <label class="font-bold text-on-surface-variant block mb-1">Default Thermal Printer Width</label>
                        <select class="w-full p-2.5 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none">
                            <option value="80mm" selected>80mm ESC/POS Roll (Standard Counter)</option>
                            <option value="58mm">58mm ESC/POS Roll (Portable Handheld)</option>
                            <option value="A4">A4 Full Sheet (Laser Printer)</option>
                        </select>
                    </div>
                </div>

                <button class="mt-4 px-6 py-2.5 rounded-lg bg-primary-container text-white font-bold text-xs shadow hover:brightness-110 active:scale-95 transition-all">Save Changes</button>
            </div>
        `;
    }

    // ==========================================
    // NEW COUNTER INTAKE ORDER MODAL
    // ==========================================
    async openNewBookingModal() {
        if (!this.token) {
            this.renderLogin('Please sign in to access counter booking.');
            return;
        }

        const modal = document.getElementById('modal-new-booking');
        const modalBody = document.getElementById('modal-new-booking-body');
        if (!modal || !modalBody) return;

        modalBody.innerHTML = `
            <div class="flex flex-col items-center justify-center p-12 text-center">
                <div class="w-8 h-8 rounded-full border-4 border-primary-container border-t-transparent animate-spin mb-3"></div>
                <p class="text-xs font-bold text-primary">Fetching Atelier Catalog & Patrons...</p>
            </div>
        `;
        modal.classList.remove('hidden');

        try {
            const [services, customers, templates] = await Promise.all([
                this.apiRequest('/services'),
                this.apiRequest('/customers'),
                this.apiRequest('/services/templates/measurement')
            ]);
            this.modalServices = services || [];
            this.modalCustomers = customers || [];
            this.modalTemplates = templates || [];
            this.modalGarments = [
                {
                    name: '',
                    category: 'Coat / Blazer',
                    fabric: '',
                    color: '',
                    qty: 1,
                    rack: '',
                    serviceIds: [],
                    instructions: '',
                    measurementTemplate: '',
                    measurementUnit: 'INCH',
                    measurements: {}
                }
            ];
            this.renderNewBookingForm();
        } catch (err) {
            modalBody.innerHTML = `<div class="p-6 text-center text-error">Failed to initialize intake dialog: ${err.message}</div>`;
        }
    }

    closeNewBookingModal() {
        const modal = document.getElementById('modal-new-booking');
        if (modal) modal.classList.add('hidden');
    }

    syncModalGarmentsFromDOM() {
        this.modalGarments.forEach((g, idx) => {
            const nameEl = document.getElementById(`g-name-${idx}`);
            if (!nameEl) return;
            g.name = nameEl.value;
            g.category = document.getElementById(`g-cat-${idx}`)?.value || g.category;
            g.rack = document.getElementById(`g-rack-${idx}`)?.value || '';
            g.fabric = document.getElementById(`g-fabric-${idx}`)?.value || '';
            g.color = document.getElementById(`g-color-${idx}`)?.value || '';
            g.qty = Number(document.getElementById(`g-qty-${idx}`)?.value) || 1;
            g.instructions = document.getElementById(`g-notes-${idx}`)?.value || '';
            const checked = document.querySelectorAll(`input[name="g-srv-${idx}"]:checked`);
            g.serviceIds = Array.from(checked).map(cb => Number(cb.value));
            g.measurementTemplate = document.getElementById(`g-meas-tmpl-${idx}`)?.value || '';
            g.measurementUnit = document.getElementById(`g-meas-unit-${idx}`)?.value || 'INCH';
            const measInputs = document.querySelectorAll(`[data-meas-idx="${idx}"]`);
            const mObj = {};
            measInputs.forEach(inp => {
                if (inp.value !== '') mObj[inp.dataset.measKey] = parseFloat(inp.value);
            });
            g.measurements = mObj;
        });
    }

    onModalTemplateChange(idx, templateType) {
        this.syncModalGarmentsFromDOM();
        this.modalGarments[idx].measurementTemplate = templateType;
        this.modalGarments[idx].measurements = {};
        this.renderNewBookingForm();
    }

    addGarmentToModal() {
        this.syncModalGarmentsFromDOM();
        this.modalGarments.push({
            name: '',
            category: 'Formal Shirt',
            fabric: '',
            color: '',
            qty: 1,
            rack: '',
            serviceIds: [],
            instructions: '',
            measurementTemplate: '',
            measurementUnit: 'INCH',
            measurements: {}
        });
        this.renderNewBookingForm();
    }

    removeGarmentFromModal(idx) {
        if (this.modalGarments.length <= 1) {
            alert('At least one garment is required for an intake booking.');
            return;
        }
        this.syncModalGarmentsFromDOM();
        this.modalGarments.splice(idx, 1);
        this.renderNewBookingForm();
    }

    renderNewBookingForm() {
        const modalBody = document.getElementById('modal-new-booking-body');
        if (!modalBody) return;

        // Default due date: +3 days from now formatted for datetime-local
        const d = new Date();
        d.setDate(d.getDate() + 3);
        const defaultDueDate = d.toISOString().slice(0, 16);

        modalBody.innerHTML = `
            <form id="intake-order-form" class="space-y-4">
                <!-- SECTION 1: CUSTOMER SELECTION / REGISTRATION -->
                <div class="p-3.5 rounded-xl bg-surface-container-low border border-outline-variant/40 space-y-3">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-primary uppercase tracking-wider flex items-center gap-1.5">
                            <span class="material-symbols-outlined text-[16px]">person</span>
                            <span>Patron Information</span>
                        </span>
                        <div class="flex items-center gap-2">
                            <label class="text-[11px] font-semibold text-on-surface-variant flex items-center gap-1 cursor-pointer">
                                <input type="radio" name="cust-mode" value="new" checked onchange="window.adminApp.toggleCustomerMode('new')"/>
                                <span>New Client</span>
                            </label>
                            ${this.modalCustomers.length > 0 ? `
                                <label class="text-[11px] font-semibold text-on-surface-variant flex items-center gap-1 cursor-pointer">
                                    <input type="radio" name="cust-mode" value="existing" onchange="window.adminApp.toggleCustomerMode('existing')"/>
                                    <span>Existing Client</span>
                                </label>
                            ` : ''}
                        </div>
                    </div>

                    <!-- New Customer Fields -->
                    <div id="new-cust-fields" class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                            <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Full Name *</label>
                            <input type="text" id="cust-fullname" required placeholder="e.g. Smt. Neha Kapoor" class="w-full px-3 py-2 rounded-lg bg-surface-container-lowest border border-outline-variant text-xs outline-none focus:border-primary-container"/>
                        </div>
                        <div>
                            <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Mobile Phone (10-Digit) *</label>
                            <input type="tel" id="cust-phone" required placeholder="e.g. 9810233445" maxlength="10" class="w-full px-3 py-2 rounded-lg bg-surface-container-lowest border border-outline-variant text-xs font-mono outline-none focus:border-primary-container"/>
                        </div>
                        <div>
                            <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Patron Tier</label>
                            <select id="cust-tier" class="w-full px-3 py-2 rounded-lg bg-surface-container-lowest border border-outline-variant text-xs outline-none focus:border-primary-container">
                                <option value="Regular Patron" selected>Regular Patron</option>
                                <option value="Silver Patron">Silver Patron</option>
                                <option value="Gold Patron">Gold Patron</option>
                                <option value="Diamond Patron">Diamond Patron</option>
                            </select>
                        </div>
                    </div>

                    <!-- Existing Customer Selector (Hidden by default) -->
                    <div id="existing-cust-fields" class="hidden">
                        <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Select Registered Patron</label>
                        <select id="select-existing-cust" class="w-full px-3 py-2 rounded-lg bg-surface-container-lowest border border-outline-variant text-xs outline-none focus:border-primary-container">
                            ${this.modalCustomers.map(c => `
                                <option value="${c.id}">${c.full_name} (${c.phone}) • ${c.patron_tier}</option>
                            `).join('')}
                        </select>
                    </div>
                </div>

                <!-- SECTION 2: ORDER DIVISION & TIMELINE -->
                <div class="p-3.5 rounded-xl bg-surface-container-low border border-outline-variant/40 space-y-3">
                    <span class="text-xs font-bold text-primary uppercase tracking-wider flex items-center gap-1.5">
                        <span class="material-symbols-outlined text-[16px]">tune</span>
                        <span>Division & Timeline</span>
                    </span>

                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                            <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Business Wing</label>
                            <select id="order-division" class="w-full px-3 py-2 rounded-lg bg-surface-container-lowest border border-outline-variant text-xs font-bold text-primary outline-none">
                                <option value="AASHIMA Women's World" selected>AASHIMA Women's World</option>
                                <option value="AASHIMA Stitchers 'N' Drapers">AASHIMA Stitchers 'N' Drapers</option>
                            </select>
                        </div>
                        <div>
                            <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Order Type</label>
                            <select id="order-type" class="w-full px-3 py-2 rounded-lg bg-surface-container-lowest border border-outline-variant text-xs outline-none">
                                <option value="Counter Intake" selected>Counter Intake</option>
                                <option value="Bridal Atelier">Bridal Atelier</option>
                                <option value="Express Fabric Care">Express Fabric Care</option>
                            </select>
                        </div>
                        <div>
                            <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Delivery Due Date *</label>
                            <input type="datetime-local" id="order-due-date" value="${defaultDueDate}" required class="w-full px-3 py-2 rounded-lg bg-surface-container-lowest border border-outline-variant text-xs outline-none"/>
                        </div>
                    </div>

                    <div class="flex items-center gap-2 pt-1 border-t border-outline-variant/30">
                        <label class="flex items-center gap-1.5 cursor-pointer">
                            <input type="checkbox" id="order-is-urgent" class="rounded accent-primary"/>
                            <span class="text-[11px] font-bold text-error">Mark as Urgent / Priority Handover</span>
                        </label>
                        <input type="text" id="order-urgent-reason" placeholder="Reason (e.g. Wedding Event, Travel)" class="flex-1 px-3 py-1.5 rounded-lg bg-surface-container-lowest border border-outline-variant text-xs outline-none"/>
                    </div>
                </div>

                <!-- SECTION 3: GARMENTS INTAKE MATRIX -->
                <div class="p-3.5 rounded-xl bg-surface-container-low border border-outline-variant/40 space-y-3">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-primary uppercase tracking-wider flex items-center gap-1.5">
                            <span class="material-symbols-outlined text-[16px]">styler</span>
                            <span>Garments Intake (${this.modalGarments.length})</span>
                        </span>
                        <button type="button" onclick="window.adminApp.addGarmentToModal()" class="px-3 py-1.5 rounded-lg bg-primary-container text-white text-[11px] font-bold flex items-center gap-1 shadow hover:brightness-110">
                            <span class="material-symbols-outlined text-[14px]">add</span>
                            <span>Add Garment</span>
                        </button>
                    </div>

                    <div class="space-y-3">
                        ${this.modalGarments.map((g, idx) => `
                            <div class="p-3 rounded-lg bg-surface-container-lowest border border-outline-variant/50 space-y-2.5 shadow-sm">
                                <div class="flex items-center justify-between pb-1.5 border-b border-outline-variant/30">
                                    <span class="font-mono text-[11px] font-bold text-primary">Garment #${idx + 1}</span>
                                    ${this.modalGarments.length > 1 ? `
                                        <button type="button" onclick="window.adminApp.removeGarmentFromModal(${idx})" class="text-error hover:underline text-[10px] font-bold flex items-center gap-0.5">
                                            <span class="material-symbols-outlined text-[14px]">delete</span>
                                            <span>Remove</span>
                                        </button>
                                    ` : ''}
                                </div>

                                <div class="grid grid-cols-1 sm:grid-cols-4 gap-2">
                                    <div class="sm:col-span-2">
                                        <label class="text-[10px] font-bold text-on-surface-variant block mb-0.5">Garment Name *</label>
                                        <input type="text" id="g-name-${idx}" value="${g.name}" required placeholder="e.g. Navy Wool Coat / Silk Saree" class="w-full px-2.5 py-1.5 rounded bg-surface-container-low border border-outline-variant text-xs outline-none"/>
                                    </div>
                                    <div>
                                        <label class="text-[10px] font-bold text-on-surface-variant block mb-0.5">Category</label>
                                        <select id="g-cat-${idx}" class="w-full px-2.5 py-1.5 rounded bg-surface-container-low border border-outline-variant text-xs outline-none">
                                            <optgroup label="Men's Bespoke & Formal">
                                                <option value="Coat / Blazer" ${g.category === 'Coat / Blazer' ? 'selected' : ''}>Coat / Blazer</option>
                                                <option value="Formal Shirt" ${g.category === 'Formal Shirt' ? 'selected' : ''}>Formal Shirt</option>
                                                <option value="Formal Trouser / Pant" ${g.category === 'Formal Trouser / Pant' ? 'selected' : ''}>Formal Trouser / Pant</option>
                                                <option value="Kurta Pajama" ${g.category === 'Kurta Pajama' ? 'selected' : ''}>Kurta Pajama</option>
                                                <option value="Sherwani / Bandhgala" ${g.category === 'Sherwani / Bandhgala' ? 'selected' : ''}>Sherwani / Bandhgala</option>
                                                <option value="Waistcoat / Nehru Jacket" ${g.category === 'Waistcoat / Nehru Jacket' ? 'selected' : ''}>Waistcoat / Nehru Jacket</option>
                                                <option value="Men's Suit" ${g.category === "Men's Suit" ? 'selected' : ''}>Men's Suit (2pc/3pc)</option>
                                            </optgroup>
                                            <optgroup label="Women's Couture & Ethnic">
                                                <option value="Saree" ${g.category === 'Saree' ? 'selected' : ''}>Saree</option>
                                                <option value="Lehenga" ${g.category === 'Lehenga' ? 'selected' : ''}>Lehenga</option>
                                                <option value="Blouse" ${g.category === 'Blouse' ? 'selected' : ''}>Blouse</option>
                                                <option value="Kurti" ${g.category === 'Kurti' ? 'selected' : ''}>Kurti / Kameez</option>
                                                <option value="Salwar / Palazzo" ${g.category === 'Salwar / Palazzo' ? 'selected' : ''}>Salwar / Palazzo</option>
                                                <option value="Western / Gown" ${g.category === 'Western / Gown' ? 'selected' : ''}>Western / Gown</option>
                                            </optgroup>
                                        </select>
                                    </div>
                                    <div>
                                        <label class="text-[10px] font-bold text-on-surface-variant block mb-0.5">Rack Location</label>
                                        <input type="text" id="g-rack-${idx}" value="${g.rack}" placeholder="e.g. Rack #A-01" class="w-full px-2.5 py-1.5 rounded bg-surface-container-low border border-outline-variant text-xs outline-none"/>
                                    </div>
                                </div>

                                <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
                                    <div>
                                        <label class="text-[10px] font-bold text-on-surface-variant block mb-0.5">Fabric</label>
                                        <input type="text" id="g-fabric-${idx}" value="${g.fabric}" placeholder="e.g. Linen, Wool, Pure Silk" class="w-full px-2.5 py-1.5 rounded bg-surface-container-low border border-outline-variant text-xs outline-none"/>
                                    </div>
                                    <div>
                                        <label class="text-[10px] font-bold text-on-surface-variant block mb-0.5">Color</label>
                                        <input type="text" id="g-color-${idx}" value="${g.color}" placeholder="e.g. Charcoal Navy" class="w-full px-2.5 py-1.5 rounded bg-surface-container-low border border-outline-variant text-xs outline-none"/>
                                    </div>
                                    <div>
                                        <label class="text-[10px] font-bold text-on-surface-variant block mb-0.5">Quantity</label>
                                        <input type="number" id="g-qty-${idx}" value="${g.qty || 1}" min="1" max="50" class="w-full px-2.5 py-1.5 rounded bg-surface-container-low border border-outline-variant text-xs outline-none"/>
                                    </div>
                                </div>

                                <div>
                                    <label class="text-[10px] font-bold text-on-surface-variant block mb-1">Services Assigned *</label>
                                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5 max-h-36 overflow-y-auto p-1.5 bg-surface-container-low rounded border border-outline-variant/30">
                                        ${this.modalServices.map(s => {
                                            const price = s.pricing_tiers[0]?.base_price || '0';
                                            const isChecked = g.serviceIds.includes(s.id);
                                            return `
                                                <label class="flex items-center gap-1.5 p-1 rounded hover:bg-surface-container text-[11px] cursor-pointer">
                                                    <input type="checkbox" name="g-srv-${idx}" value="${s.id}" ${isChecked ? 'checked' : ''} class="rounded accent-primary"/>
                                                    <span class="truncate flex-1">${s.name}</span>
                                                    <span class="font-mono font-bold text-primary">₹${price}</span>
                                                </label>
                                            `;
                                        }).join('')}
                                    </div>
                                </div>

                                <!-- Optional Tailoring Measurements Matrix (Men's & Women's) -->
                                <div class="p-2.5 rounded-lg bg-surface-container-low border border-outline-variant/40 space-y-2">
                                    <div class="flex flex-wrap items-center justify-between gap-2">
                                        <label class="text-[10px] font-bold text-primary uppercase tracking-wider flex items-center gap-1">
                                            <span class="material-symbols-outlined text-[14px]">straighten</span>
                                            <span>Tailoring Measurements (Optional)</span>
                                        </label>
                                        <div class="flex items-center gap-1.5">
                                            <select id="g-meas-tmpl-${idx}" onchange="window.adminApp.onModalTemplateChange(${idx}, this.value)" class="px-2 py-1 rounded bg-surface-container-lowest border border-outline-variant text-[11px] font-semibold outline-none">
                                                <option value="">No Measurements (Dry Clean / Iron Only)</option>
                                                <optgroup label="Men's Tailoring Matrices">
                                                    ${(this.modalTemplates || []).filter(t => (t.silhouette_icon || '').toLowerCase() === 'men').map(t => `
                                                        <option value="${t.garment_type}" ${g.measurementTemplate === t.garment_type ? 'selected' : ''}>${t.display_title}</option>
                                                    `).join('')}
                                                </optgroup>
                                                <optgroup label="Women's Couture Matrices">
                                                    ${(this.modalTemplates || []).filter(t => (t.silhouette_icon || '').toLowerCase() !== 'men').map(t => `
                                                        <option value="${t.garment_type}" ${g.measurementTemplate === t.garment_type ? 'selected' : ''}>${t.display_title}</option>
                                                    `).join('')}
                                                </optgroup>
                                            </select>
                                            ${g.measurementTemplate ? `
                                                <select id="g-meas-unit-${idx}" class="px-1.5 py-1 rounded bg-surface-container-lowest border border-outline-variant text-[10px] font-bold outline-none">
                                                    <option value="INCH" ${g.measurementUnit === 'INCH' ? 'selected' : ''}>INCH</option>
                                                    <option value="CM" ${g.measurementUnit === 'CM' ? 'selected' : ''}>CM</option>
                                                </select>
                                            ` : ''}
                                        </div>
                                    </div>
                                    ${(() => {
                                        if (!g.measurementTemplate) return '';
                                        const tmpl = (this.modalTemplates || []).find(t => t.garment_type === g.measurementTemplate);
                                        if (!tmpl) return '';
                                        const fields = JSON.parse(tmpl.anchor_fields || '[]');
                                        return `
                                            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
                                                ${fields.map(f => `
                                                    <div>
                                                        <label class="text-[9px] font-bold text-on-surface-variant block mb-0.5 truncate" title="${f.label}">${f.label}</label>
                                                        <input type="number" step="0.25" min="0" data-meas-idx="${idx}" data-meas-key="${f.name}" value="${g.measurements?.[f.name] ?? ''}" placeholder="${f.min}–${f.max}" class="w-full px-2 py-1 rounded bg-surface-container-lowest border border-outline-variant text-xs font-mono outline-none focus:border-primary-container"/>
                                                    </div>
                                                `).join('')}
                                            </div>
                                        `;
                                    })()}
                                </div>

                                <div>
                                    <label class="text-[10px] font-bold text-on-surface-variant block mb-0.5">Special Artisan Directives</label>
                                    <input type="text" id="g-notes-${idx}" value="${g.instructions || ''}" placeholder="e.g. Slim fit, double vent, padding, delicate steam finish" class="w-full px-2.5 py-1.5 rounded bg-surface-container-low border border-outline-variant text-xs outline-none"/>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- SECTION 4: SETTLEMENT & ADVANCE PAYMENT -->
                <div class="p-3.5 rounded-xl bg-surface-container-low border border-outline-variant/40 space-y-3">
                    <span class="text-xs font-bold text-primary uppercase tracking-wider flex items-center gap-1.5">
                        <span class="material-symbols-outlined text-[16px]">payments</span>
                        <span>Counter Settlement & Advance</span>
                    </span>

                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                            <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Advance Collected (₹)</label>
                            <input type="number" id="order-advance" value="0" min="0" step="1" class="w-full px-3 py-2 rounded-lg bg-surface-container-lowest border border-outline-variant text-xs font-mono font-bold text-primary outline-none"/>
                        </div>
                        <div>
                            <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Payment Mode</label>
                            <select id="order-pay-mode" class="w-full px-3 py-2 rounded-lg bg-surface-container-lowest border border-outline-variant text-xs outline-none">
                                <option value="UPI" selected>UPI / QR Scan</option>
                                <option value="Cash">Cash Counter</option>
                                <option value="Card">POS Card Swipe</option>
                            </select>
                        </div>
                        <div>
                            <label class="text-[11px] font-bold text-on-surface-variant block mb-1">UTR / Reference No.</label>
                            <input type="text" id="order-txn-id" placeholder="Optional transaction ID" class="w-full px-3 py-2 rounded-lg bg-surface-container-lowest border border-outline-variant text-xs font-mono outline-none"/>
                        </div>
                    </div>
                </div>

                <!-- ACTION BUTTONS -->
                <div class="pt-2 flex items-center justify-end gap-2">
                    <button type="button" onclick="window.adminApp.closeNewBookingModal()" class="px-5 py-2.5 rounded-xl bg-surface-container text-on-surface font-semibold text-xs hover:bg-surface-container-high transition-colors">
                        Cancel
                    </button>
                    <button type="submit" id="btn-submit-intake" class="px-6 py-2.5 rounded-xl bg-primary-container text-white font-bold text-xs flex items-center gap-1.5 shadow-md hover:brightness-110 active:scale-95 transition-all">
                        <span class="material-symbols-outlined text-[16px]">verified</span>
                        <span>Confirm Intake & Issue QR Tags</span>
                    </button>
                </div>
            </form>
        `;

        document.getElementById('intake-order-form').onsubmit = (e) => this.handleCreateBooking(e);
    }

    toggleCustomerMode(mode) {
        const newFields = document.getElementById('new-cust-fields');
        const existingFields = document.getElementById('existing-cust-fields');
        if (mode === 'new') {
            newFields?.classList.remove('hidden');
            existingFields?.classList.add('hidden');
        } else {
            newFields?.classList.add('hidden');
            existingFields?.classList.remove('hidden');
        }
    }

    async handleCreateBooking(e) {
        e.preventDefault();
        const submitBtn = document.getElementById('btn-submit-intake');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">refresh</span><span>Processing Intake...</span>`;
        }

        try {
            // 1. Resolve Customer ID
            let customerId = null;
            const custMode = document.querySelector('input[name="cust-mode"]:checked')?.value || 'new';

            if (custMode === 'existing') {
                customerId = Number(document.getElementById('select-existing-cust').value);
            } else {
                const fullName = document.getElementById('cust-fullname').value.trim();
                const phone = document.getElementById('cust-phone').value.trim();
                const tier = document.getElementById('cust-tier').value;

                if (!fullName || !phone) {
                    throw new Error('Please provide customer name and mobile phone.');
                }

                // Check if customer with phone already exists
                const existing = this.modalCustomers.find(c => c.phone.endsWith(phone.slice(-10)));
                if (existing) {
                    customerId = existing.id;
                } else {
                    // Create new customer
                    const newCust = await this.apiRequest('/customers', {
                        method: 'POST',
                        body: JSON.stringify({
                            full_name: fullName,
                            phone: phone,
                            patron_tier: tier,
                            notes: 'Counter registered patron'
                        })
                    });
                    customerId = newCust.id;
                }
            }

            // 2. Build Garments List (with optional Men's/Women's Measurements)
            const garmentsPayload = [];
            for (let i = 0; i < this.modalGarments.length; i++) {
                const name = document.getElementById(`g-name-${i}`)?.value.trim();
                if (!name) {
                    throw new Error(`Please enter a garment name for Garment #${i + 1}.`);
                }
                const cat = document.getElementById(`g-cat-${i}`)?.value || 'Coat / Blazer';
                const rack = document.getElementById(`g-rack-${i}`)?.value.trim() || 'Intake Counter';
                const fabric = document.getElementById(`g-fabric-${i}`)?.value.trim() || 'Standard';
                const color = document.getElementById(`g-color-${i}`)?.value.trim() || 'Standard';
                const qty = Number(document.getElementById(`g-qty-${i}`)?.value) || 1;
                const notes = document.getElementById(`g-notes-${i}`)?.value.trim() || '';

                const checkedBoxes = document.querySelectorAll(`input[name="g-srv-${i}"]:checked`);
                const serviceIds = Array.from(checkedBoxes).map(cb => Number(cb.value));

                if (serviceIds.length === 0) {
                    throw new Error(`Please assign at least one service to Garment #${i + 1} (${name}).`);
                }

                // Collect tailoring measurements if a template was selected
                let measurementObj = null;
                const measTmpl = document.getElementById(`g-meas-tmpl-${i}`)?.value || '';
                if (measTmpl) {
                    const measUnit = document.getElementById(`g-meas-unit-${i}`)?.value || 'INCH';
                    const measInputs = document.querySelectorAll(`[data-meas-idx="${i}"]`);
                    const mValues = {};
                    measInputs.forEach(inp => {
                        if (inp.value !== '') {
                            mValues[inp.dataset.measKey] = parseFloat(inp.value);
                        }
                    });
                    if (Object.keys(mValues).length > 0) {
                        measurementObj = {
                            template_garment_type: measTmpl,
                            unit: measUnit,
                            measurements: mValues,
                            karigar_directives: notes || null
                        };
                    }
                }

                garmentsPayload.push({
                    garment_name: name,
                    category: cat,
                    fabric_type: fabric,
                    color: color,
                    quantity: qty,
                    rack_location: rack,
                    special_instructions: notes,
                    service_ids: serviceIds,
                    measurement: measurementObj
                });
            }

            // 3. Construct Booking Payload
            const division = document.getElementById('order-division').value;
            const orderType = document.getElementById('order-type').value;
            const dueDate = document.getElementById('order-due-date').value;
            const isUrgent = document.getElementById('order-is-urgent').checked;
            const urgentReason = document.getElementById('order-urgent-reason')?.value.trim() || (isUrgent ? 'Priority Handover' : null);
            const advance = Number(document.getElementById('order-advance').value) || 0;
            const payMode = document.getElementById('order-pay-mode').value;
            const txnId = document.getElementById('order-txn-id')?.value.trim() || null;

            const bookingPayload = {
                customer_id: customerId,
                division: division,
                order_type: orderType,
                delivery_due_date: new Date(dueDate).toISOString(),
                is_urgent: isUrgent,
                urgent_reason: urgentReason,
                advance_payment_amount: advance,
                advance_payment_mode: payMode,
                advance_transaction_id: txnId,
                garments: garmentsPayload
            };

            // 4. Send API Request
            const newBooking = await this.apiRequest('/bookings', {
                method: 'POST',
                body: JSON.stringify(bookingPayload)
            });

            // 5. Success Handling
            this.closeNewBookingModal();
            alert(`🎉 Booking #${newBooking.booking_number} generated successfully with 80mm tracking tokens!`);
            
            // Reload active tab and open thermal drawer for printing
            await this.switchTab(this.currentTab || 'overview');
            await this.openThermalSlip(newBooking.id);

        } catch (err) {
            alert('Intake Error: ' + err.message);
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<span class="material-symbols-outlined text-[16px]">verified</span><span>Confirm Intake & Issue QR Tags</span>`;
            }
        }
    }

    // ==========================================
    // THERMAL SLIP DRAWER
    // ==========================================
    async openThermalSlip(bookingId) {
        try {
            const booking = await this.apiRequest(`/bookings/${bookingId}`);
            const garmentIds = booking.garments.map(g => g.id);
            const slips = await this.apiRequest('/qr/print-slips', {
                method: 'POST',
                body: JSON.stringify({ garment_ids: garmentIds, format: '80mm' })
            });

            const slip = slips.slips[0] || {};
            const drawerContent = document.getElementById('drawer-thermal-content');
            drawerContent.innerHTML = `
                <div class="flex flex-col items-center mb-3">
                    <img src="${slip.qr_image_data_uri}" alt="QR code" class="w-32 h-32 border border-black/10 rounded p-1 mb-2"/>
                    <span class="font-bold text-xs">${slip.qr_code_identifier || ''}</span>
                </div>
                <div>${slip.thermal_text}</div>
            `;

            document.getElementById('drawer-thermal').classList.remove('translate-x-full');
        } catch (e) {
            alert('Failed to load thermal preview: ' + e.message);
        }
    }

    closeThermalDrawer() {
        document.getElementById('drawer-thermal').classList.add('translate-x-full');
    }

    // ==========================================
    // DELETION ACTIONS & TOAST
    // ==========================================
    async deleteBooking(bookingId, bookingNumber) {
        const confirmed = confirm(`Are you sure you want to delete Order #${bookingNumber}?\n\nThis will remove the entry from the workshop queue and active daybook.`);
        if (!confirmed) return;

        try {
            const res = await this.apiRequest(`/bookings/${bookingId}`, {
                method: 'DELETE'
            });
            this.showToast(res.message || `Order #${bookingNumber} deleted.`);
            await this.switchTab(this.currentTab || 'overview');
        } catch (err) {
            alert(`Failed to delete order: ${err.message}`);
        }
    }

    async deleteCustomer(customerId, customerName) {
        const confirmed = confirm(`Are you sure you want to delete Customer "${customerName}"?\n\nThis will remove the patron record from the registry.`);
        if (!confirmed) return;

        try {
            const res = await this.apiRequest(`/customers/${customerId}`, {
                method: 'DELETE'
            });
            this.showToast(res.message || `Customer "${customerName}" deleted.`);
            await this.switchTab('customers');
        } catch (err) {
            alert(`Failed to delete customer: ${err.message}`);
        }
    }

    async deleteExpense(expenseId, expenseNumber) {
        const confirmed = confirm(`Are you sure you want to delete Expense ${expenseNumber}?`);
        if (!confirmed) return;

        try {
            const res = await this.apiRequest(`/billing/expenses/${expenseId}`, {
                method: 'DELETE'
            });
            this.showToast(res.message || `Expense ${expenseNumber} deleted.`);
            await this.switchTab('expenses');
        } catch (err) {
            alert(`Failed to delete expense: ${err.message}`);
        }
    }

    async deleteInvoice(invoiceId, invoiceNumber) {
        const confirmed = confirm(`Are you sure you want to delete Invoice ${invoiceNumber}?\n\nThis will remove the tax record from the GST ledger.`);
        if (!confirmed) return;

        try {
            const res = await this.apiRequest(`/billing/invoices/${invoiceId}`, {
                method: 'DELETE'
            });
            this.showToast(res.message || `Invoice ${invoiceNumber} deleted.`);
            await this.switchTab('invoicing');
        } catch (err) {
            alert(`Failed to delete invoice: ${err.message}`);
        }
    }

    showToast(message, type = 'success') {
        let toast = document.getElementById('admin-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'admin-toast';
            document.body.appendChild(toast);
        }
        toast.className = `fixed bottom-5 right-5 z-50 px-4 py-3 rounded-xl shadow-xl font-bold text-xs flex items-center gap-2 transition-all duration-300 ${
            type === 'error' ? 'bg-error text-white' : 'bg-primary-container text-on-primary'
        }`;
        toast.innerHTML = `
            <span class="material-symbols-outlined text-[18px]">${type === 'error' ? 'error' : 'check_circle'}</span>
            <span>${message}</span>
        `;
        toast.style.display = 'flex';
        setTimeout(() => {
            if (toast) toast.style.display = 'none';
        }, 3500);
    }
}

new AdminApp();
