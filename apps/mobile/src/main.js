/**
 * AASHIMA ERP Android Application Main Controller
 * Implements Google Stitch Regal Atelier Mobile Design System
 */

import { api } from './api.js';

class MobileApp {
    constructor() {
        this.currentScreen = 'dashboard';
        this.activeBooking = null;
        this.activeGarment = null;
        this.html5QrCode = null;
        this.measurementUnit = 'inch';
        this.measurementValues = {};

        this.init();
    }

    init() {
        // Expose navigation globally
        window.navigateTo = (screen, params) => this.navigateTo(screen, params);
        window.mobileApp = this;

        // Check authentication
        if (!api.token) {
            this.navigateTo('login');
        } else {
            this.navigateTo('dashboard');
        }

        window.addEventListener('auth:expired', () => {
            this.showToast('Session expired. Please log in.');
            this.navigateTo('login');
        });
    }

    async navigateTo(screen, params = {}) {
        this.currentScreen = screen;
        const container = document.getElementById('screen-container');
        const bottomNav = document.getElementById('bottom-nav');

        // Stop QR scanner if navigating away
        if (this.html5QrCode && screen !== 'qr-scan') {
            try {
                await this.html5QrCode.stop();
                this.html5QrCode = null;
            } catch (e) {
                // Ignore scanner stop error
            }
        }

        // Toggle bottom nav visibility
        if (screen === 'login' || screen === 'splash') {
            bottomNav.classList.add('hidden');
        } else {
            bottomNav.classList.remove('hidden');
            // Update active nav button
            document.querySelectorAll('.nav-item').forEach(btn => {
                if (btn.dataset.screen === screen) {
                    btn.classList.add('text-primary', 'font-bold');
                    btn.classList.remove('text-on-surface-variant');
                } else {
                    btn.classList.remove('text-primary', 'font-bold');
                    btn.classList.add('text-on-surface-variant');
                }
            });
        }

        // Render appropriate screen
        switch (screen) {
            case 'login':
                this.renderLogin(container);
                break;
            case 'dashboard':
                await this.renderDashboard(container);
                break;
            case 'new-booking':
                await this.renderNewBooking(container);
                break;
            case 'qr-scan':
                await this.renderQRScanner(container);
                break;
            case 'stage-update':
                await this.renderStageUpdate(container, params);
                break;
            case 'measurements':
                await this.renderMeasurementMatrix(container, params);
                break;
            case 'orders':
                await this.renderOrderManagement(container);
                break;
            case 'departments':
                await this.renderDepartmentQueue(container, params);
                break;
            case 'payments':
                await this.renderPayments(container);
                break;
            case 'thermal-print':
                await this.renderThermalPrint(container, params);
                break;
            case 'settings':
                this.renderSettings(container);
                break;
            default:
                await this.renderDashboard(container);
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showToast(message, isError = false) {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-xl shadow-lg text-sm font-semibold flex items-center gap-2 transition-all ${
            isError ? 'bg-error text-on-error' : 'bg-primary-container text-on-primary'
        }`;
        toast.innerHTML = `
            <span class="material-symbols-outlined text-[18px]">${isError ? 'error' : 'check_circle'}</span>
            <span>${message}</span>
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3500);
    }

    // ==========================================
    // SCREEN 1: LOGIN & CREDENTIALS
    // ==========================================
    renderLogin(container) {
        container.innerHTML = `
            <div class="flex-1 flex flex-col justify-between p-6 bg-surface">
                <div class="pt-8 flex flex-col items-center text-center">
                    <div class="w-16 h-16 rounded-2xl bg-primary-container text-on-primary flex items-center justify-center shadow-lg mb-4">
                        <span class="material-symbols-outlined text-[36px] text-tertiary-fixed">hotel_class</span>
                    </div>
                    <h1 class="font-serif text-3xl font-bold text-primary tracking-wide">AASHIMA</h1>
                    <p class="font-sans text-xs uppercase tracking-widest text-on-tertiary-container mt-1 font-semibold">Women's World & Stitchers 'N' Drapers</p>
                    <span class="text-xs text-on-surface-variant mt-0.5">581, Turab Nagar, Ghaziabad</span>
                </div>

                <div class="my-auto py-6 space-y-4">
                    <div class="p-4 rounded-xl bg-surface-container-low border border-outline-variant/50">
                        <span class="text-xs font-semibold text-secondary uppercase tracking-wider block mb-3">Atelier Staff Sign In</span>
                        
                        <div class="space-y-3">
                            <div>
                                <label class="text-xs font-bold text-on-surface-variant block mb-1">Username or Mobile</label>
                                <div class="flex items-center px-3 py-2.5 rounded-lg bg-surface-container-lowest border border-outline-variant focus-within:border-primary-container">
                                    <span class="material-symbols-outlined text-[18px] text-outline mr-2">person</span>
                                    <input type="text" id="login-username" value="" placeholder="Enter staff username or mobile" class="w-full text-sm bg-transparent outline-none text-on-surface"/>
                                </div>
                            </div>

                            <div>
                                <label class="text-xs font-bold text-on-surface-variant block mb-1">Password</label>
                                <div class="flex items-center px-3 py-2.5 rounded-lg bg-surface-container-lowest border border-outline-variant focus-within:border-primary-container">
                                    <span class="material-symbols-outlined text-[18px] text-outline mr-2">lock</span>
                                    <input type="password" id="login-password" value="" placeholder="Enter password" class="w-full text-sm bg-transparent outline-none text-on-surface"/>
                                </div>
                            </div>
                        </div>

                        <button id="btn-do-login" class="w-full mt-5 py-3 rounded-lg bg-primary-container text-on-primary font-bold text-sm shadow-md active:scale-95 transition-transform flex items-center justify-center gap-2">
                            <span>Open Atelier Counter</span>
                            <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
                        </button>
                    </div>
                </div>

                <div class="text-center text-[11px] text-on-surface-variant pb-2">
                    AASHIMA Enterprise Atelier ERP v2.4 • Secured Session
                </div>
            </div>
        `;

        document.getElementById('btn-do-login').onclick = async () => {
            const u = document.getElementById('login-username').value.trim();
            const p = document.getElementById('login-password').value.trim();
            if (!u || !p) {
                this.showToast('Please enter both username and password', true);
                return;
            }
            try {
                const res = await api.login(u, p);
                this.showToast(`Namaste ${res.full_name}! Counter unlocked.`);
                this.navigateTo('dashboard');
            } catch (err) {
                this.showToast(err.message || 'Login failed', true);
            }
        };
    }

    // ==========================================
    // SCREEN 2: DASHBOARD (Stitch Atelier Dashboard)
    // ==========================================
    async renderDashboard(container) {
        try {
            const metrics = await api.getDashboardMetrics();
            const daybook = metrics.daybook || {};
            const pipeline = metrics.pipeline || {};
            const urgentOrders = metrics.urgent_orders || [];

            container.innerHTML = `
                <!-- Sticky Atelier Header -->
                <header class="sticky top-0 z-30 bg-primary-container text-on-primary px-4 py-3 shadow-md flex items-center justify-between">
                    <div class="flex items-center gap-2.5">
                        <div class="w-8 h-8 rounded-lg bg-surface-container-lowest/10 border border-white/20 flex items-center justify-center text-tertiary-fixed">
                            <span class="material-symbols-outlined text-[20px]">hotel_class</span>
                        </div>
                        <div>
                            <h1 class="font-serif text-lg font-bold leading-tight tracking-wide">AASHIMA</h1>
                            <p class="text-[10px] text-tertiary-fixed font-medium uppercase tracking-widest leading-none">Turab Nagar Flagship</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded-full bg-white/10 text-[10px] font-semibold border border-white/15">Shift #1 Active</span>
                        <button onclick="window.navigateTo('settings')" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-95">
                            <span class="material-symbols-outlined text-[18px]">account_circle</span>
                        </button>
                    </div>
                </header>

                <!-- Primary Order Intake CTA Banner -->
                <div class="px-3 pt-3">
                    <button onclick="window.navigateTo('new-booking')" class="w-full py-3 px-4 rounded-xl bg-primary-container text-on-primary shadow-md active:scale-[0.98] transition-all flex items-center justify-between">
                        <div class="flex items-center gap-2.5 text-left">
                            <div class="w-9 h-9 rounded-lg bg-white/15 flex items-center justify-center text-tertiary-fixed shrink-0">
                                <span class="material-symbols-outlined text-[22px]">add_shopping_cart</span>
                            </div>
                            <div>
                                <div class="font-serif text-sm font-bold leading-tight">New Order Intake</div>
                                <div class="text-[10px] text-tertiary-fixed/90">Book Men's / Women's garments & issue QR tags</div>
                            </div>
                        </div>
                        <span class="material-symbols-outlined text-[20px] text-tertiary-fixed">arrow_forward</span>
                    </button>
                </div>

                <!-- Metric Cards Grid -->
                <section class="p-3 grid grid-cols-2 gap-2.5">
                    <!-- Stat 1: In-Process Jobs -->
                    <div class="bg-surface-container-lowest rounded-xl p-3.5 shadow-sm border border-outline-variant/40 flex flex-col justify-between">
                        <div class="flex items-center justify-between">
                            <span class="text-xs text-on-surface-variant font-medium">In-Process Jobs</span>
                            <div class="w-7 h-7 rounded-full bg-secondary-container/50 text-secondary flex items-center justify-center">
                                <span class="material-symbols-outlined text-[16px]">precision_manufacturing</span>
                            </div>
                        </div>
                        <div class="mt-2">
                            <div class="flex items-baseline">
                                <span class="font-serif text-2xl font-bold text-on-surface leading-none">${pipeline.total_in_floor || 0}</span>
                                <span class="text-xs text-on-surface-variant ml-1">Pieces</span>
                            </div>
                            <div class="flex items-center gap-1 mt-1 text-on-tertiary-container text-[11px]">
                                <span class="material-symbols-outlined text-[12px]">schedule</span>
                                <span>${pipeline.alteration_count || 0} in alteration</span>
                            </div>
                        </div>
                    </div>

                    <!-- Stat 2: Pending Balance -->
                    <div class="bg-surface-container-lowest rounded-xl p-3.5 shadow-sm border border-outline-variant/40 flex flex-col justify-between">
                        <div class="flex items-center justify-between">
                            <span class="text-xs text-on-surface-variant font-medium">Pending Balance</span>
                            <div class="w-7 h-7 rounded-full bg-error-container text-on-error-container flex items-center justify-center">
                                <span class="material-symbols-outlined text-[16px]">pending_actions</span>
                            </div>
                        </div>
                        <div class="mt-2">
                            <div class="flex items-baseline">
                                <span class="font-serif text-2xl font-bold text-error leading-none">₹${Number(daybook.pending_balance || 0).toLocaleString('en-IN')}</span>
                            </div>
                            <div class="text-on-surface-variant text-[11px] mt-1 truncate">
                                Across uncollected orders
                            </div>
                        </div>
                    </div>

                    <!-- Stat 3: Ready for Trial -->
                    <div class="bg-surface-container-lowest rounded-xl p-3.5 shadow-sm border border-outline-variant/40 flex flex-col justify-between">
                        <div class="flex items-center justify-between">
                            <span class="text-xs text-on-surface-variant font-medium">Ready for Trial</span>
                            <div class="w-7 h-7 rounded-full bg-tertiary-fixed text-on-tertiary-fixed flex items-center justify-center">
                                <span class="material-symbols-outlined text-[16px]">check_circle</span>
                            </div>
                        </div>
                        <div class="mt-2">
                            <div class="flex items-baseline">
                                <span class="font-serif text-2xl font-bold text-tertiary leading-none">${pipeline.trial_ready_count || 0}</span>
                                <span class="text-xs text-on-surface-variant ml-1">Garments</span>
                            </div>
                            <div class="text-secondary text-[11px] mt-1 flex items-center gap-0.5">
                                <span class="material-symbols-outlined text-[12px]">verified</span>
                                <span>Q.C. Inspected</span>
                            </div>
                        </div>
                    </div>

                    <!-- Stat 4: Daybook Collected -->
                    <div class="bg-surface-container-lowest rounded-xl p-3.5 shadow-sm border border-outline-variant/40 flex flex-col justify-between">
                        <div class="flex items-center justify-between">
                            <span class="text-xs text-on-surface-variant font-medium">Daybook Collected</span>
                            <div class="w-7 h-7 rounded-full bg-surface-container-high text-primary flex items-center justify-center">
                                <span class="material-symbols-outlined text-[16px]">currency_rupee</span>
                            </div>
                        </div>
                        <div class="mt-2">
                            <div class="flex items-baseline">
                                <span class="font-serif text-xl font-bold text-primary leading-none">₹${Number(daybook.collected_today || 0).toLocaleString('en-IN')}</span>
                            </div>
                            <div class="text-[11px] text-on-surface-variant mt-1 flex items-center justify-between">
                                <span>UPI: ₹${Number(daybook.upi_collected || 0).toLocaleString('en-IN')}</span>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- Counter Shortcuts 5-Icon Grid (Exact Stitch Layout) -->
                <section class="px-3 py-1">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-xs font-bold text-on-surface uppercase tracking-wider">Counter Shortcuts</span>
                        <span class="text-[11px] text-secondary font-semibold">POS v2.4</span>
                    </div>
                    <div class="grid grid-cols-5 gap-1.5 text-center">
                        <button onclick="window.navigateTo('new-booking')" class="flex flex-col items-center gap-1 group focus:outline-none">
                            <div class="w-12 h-12 rounded-xl bg-primary-container text-tertiary-fixed flex items-center justify-center shadow-md active:scale-90 transition-transform">
                                <span class="material-symbols-outlined text-[24px]">add_circle</span>
                            </div>
                            <span class="text-[11px] text-on-surface font-semibold truncate w-full">Order Intake</span>
                        </button>

                        <button onclick="window.navigateTo('qr-scan')" class="flex flex-col items-center gap-1 group focus:outline-none">
                            <div class="w-12 h-12 rounded-xl bg-surface-container-lowest text-primary border border-outline-variant/40 flex items-center justify-center shadow-sm active:scale-90 transition-transform">
                                <span class="material-symbols-outlined text-[24px] text-on-tertiary-container">qr_code_scanner</span>
                            </div>
                            <span class="text-[11px] text-on-surface font-semibold truncate w-full">Scan Tag</span>
                        </button>

                        <button onclick="window.navigateTo('payments')" class="flex flex-col items-center gap-1 group focus:outline-none">
                            <div class="w-12 h-12 rounded-xl bg-surface-container-lowest text-primary border border-outline-variant/40 flex items-center justify-center shadow-sm active:scale-90 transition-transform">
                                <span class="material-symbols-outlined text-[24px] text-secondary">currency_rupee</span>
                            </div>
                            <span class="text-[11px] text-on-surface font-semibold truncate w-full">Collect Pay</span>
                        </button>

                        <button onclick="window.navigateTo('measurements')" class="flex flex-col items-center gap-1 group focus:outline-none">
                            <div class="w-12 h-12 rounded-xl bg-surface-container-lowest text-primary border border-outline-variant/40 flex items-center justify-center shadow-sm active:scale-90 transition-transform">
                                <span class="material-symbols-outlined text-[24px] text-tertiary">straighten</span>
                            </div>
                            <span class="text-[11px] text-on-surface font-semibold truncate w-full">Fitting Book</span>
                        </button>

                        <button onclick="window.navigateTo('thermal-print')" class="flex flex-col items-center gap-1 group focus:outline-none">
                            <div class="w-12 h-12 rounded-xl bg-surface-container-lowest text-primary border border-outline-variant/40 flex items-center justify-center shadow-sm active:scale-90 transition-transform">
                                <span class="material-symbols-outlined text-[24px] text-outline">receipt_long</span>
                            </div>
                            <span class="text-[11px] text-on-surface font-semibold truncate w-full">Print Slip</span>
                        </button>
                    </div>
                </section>

                <!-- Urgent Attention / Red Flags Section -->
                <section class="px-3 pt-3">
                    <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center gap-1.5">
                            <span class="material-symbols-outlined text-error text-[18px]">alarm</span>
                            <span class="text-xs font-bold text-on-surface uppercase tracking-wider">Urgent Deliveries (${urgentOrders.length})</span>
                        </div>
                        <span class="px-1.5 py-0.5 rounded bg-error-container text-on-error-container text-[10px] font-bold">Priority Handover</span>
                    </div>

                    <div class="space-y-2">
                        ${urgentOrders.length > 0 ? urgentOrders.map(o => `
                            <div onclick="window.navigateTo('orders')" class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm flex items-center justify-between active:scale-[0.98] transition-transform">
                                <div class="min-w-0 pr-2">
                                    <div class="flex items-center gap-1.5">
                                        <span class="font-mono text-xs font-bold text-primary-container">#${o.booking_number}</span>
                                        <span class="px-1.5 py-0.2 rounded bg-tertiary-fixed text-on-tertiary-fixed text-[9px] font-bold">${o.urgent_reason}</span>
                                    </div>
                                    <p class="text-xs font-semibold text-on-surface truncate mt-0.5">${o.customer_name}</p>
                                    <p class="text-[10px] text-on-surface-variant flex items-center gap-1">
                                        <span class="material-symbols-outlined text-[11px] text-secondary">schedule</span>
                                        <span>Due: ${o.due_date}</span>
                                    </p>
                                </div>
                                <div class="flex flex-col items-end shrink-0">
                                    <span class="px-2 py-0.5 rounded-full bg-surface-container-high text-primary font-bold text-[10px] uppercase">${o.stage}</span>
                                    <span class="text-[10px] text-error font-semibold mt-1">Due Soon</span>
                                </div>
                            </div>
                        `).join('') : `
                            <div class="p-4 rounded-xl bg-surface-container-lowest border border-outline-variant/30 text-center text-xs text-on-surface-variant">
                                No urgent overdue bridal handovers at this hour.
                            </div>
                        `}
                    </div>
                </section>

                <!-- Workshop Wings Progress Breakdown -->
                <section class="p-3 pt-4">
                    <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm">
                        <span class="text-xs font-bold text-on-surface-variant uppercase tracking-wider block mb-2">Live Karkhana Wings</span>
                        <div class="grid grid-cols-4 gap-2 text-center text-xs">
                            <div onclick="window.navigateTo('departments', { dept: 'alteration' })" class="p-2 rounded-lg bg-surface-container hover:bg-secondary-container/30 transition-colors">
                                <span class="font-serif text-lg font-bold text-primary block">${pipeline.alteration_count || 0}</span>
                                <span class="text-[10px] text-on-surface-variant font-medium">Alteration</span>
                            </div>
                            <div onclick="window.navigateTo('departments', { dept: 'deep-cleaning' })" class="p-2 rounded-lg bg-surface-container hover:bg-secondary-container/30 transition-colors">
                                <span class="font-serif text-lg font-bold text-secondary block">${pipeline.deep_clean_count || 0}</span>
                                <span class="text-[10px] text-on-surface-variant font-medium">Deep Clean</span>
                            </div>
                            <div onclick="window.navigateTo('departments', { dept: 'finishing' })" class="p-2 rounded-lg bg-surface-container hover:bg-secondary-container/30 transition-colors">
                                <span class="font-serif text-lg font-bold text-tertiary block">${pipeline.steam_finishing_count || 0}</span>
                                <span class="text-[10px] text-on-surface-variant font-medium">Finishing</span>
                            </div>
                            <div onclick="window.navigateTo('departments', { dept: 'delivery-centre' })" class="p-2 rounded-lg bg-surface-container hover:bg-secondary-container/30 transition-colors">
                                <span class="font-serif text-lg font-bold text-success block">${pipeline.trial_ready_count || 0}</span>
                                <span class="text-[10px] text-on-surface-variant font-medium">Ready</span>
                            </div>
                        </div>
                    </div>
                </section>
            `;
        } catch (err) {
            container.innerHTML = `
                <div class="p-6 text-center text-error">
                    <span class="material-symbols-outlined text-4xl mb-2">warning</span>
                    <p class="font-bold">Failed to load live dashboard</p>
                    <p class="text-xs text-on-surface-variant mt-1">${err.message}</p>
                    <button onclick="window.navigateTo('dashboard')" class="mt-4 px-4 py-2 rounded-lg bg-primary-container text-white text-xs font-bold">Retry Connection</button>
                </div>
            `;
        }
    }

    // ==========================================
    // SCREEN 3: NEW BOOKING (Production Multi-Garment POS)
    // ==========================================
    async renderNewBooking(container) {
        try {
            const [customers, services] = await Promise.all([
                api.getCustomers(),
                api.getServices()
            ]);

            if (!this.draftBooking) {
                this.draftBooking = {
                    customerMode: customers.length > 0 ? 'existing' : 'new',
                    selectedCustomerId: customers[0]?.id || null,
                    newCustName: '',
                    newCustPhone: '',
                    division: "AASHIMA Stitchers 'N' Drapers",
                    advance: 0,
                    payMode: 'UPI',
                    dueDate: new Date(Date.now() + 3 * 24 * 3600 * 1000).toISOString().split('T')[0],
                    garments: [
                        {
                            id: Date.now(),
                            name: '',
                            category: 'Coat / Blazer',
                            fabric: '',
                            color: '',
                            qty: 1,
                            serviceId: services[0]?.id || '',
                            instructions: '',
                            measurement: null
                        }
                    ]
                };
            }

            const draft = this.draftBooking;

            const syncDraftFromDOM = () => {
                const nameInp = document.getElementById('pos-new-cust-name');
                const phoneInp = document.getElementById('pos-new-cust-phone');
                if (nameInp) draft.newCustName = nameInp.value;
                if (phoneInp) draft.newCustPhone = phoneInp.value;
                const advInp = document.getElementById('input-advance');
                if (advInp) draft.advance = parseFloat(advInp.value) || 0;
                const modeSel = document.getElementById('select-pay-mode');
                if (modeSel) draft.payMode = modeSel.value;
                const dateInp = document.getElementById('input-due-date');
                if (dateInp) draft.dueDate = dateInp.value;

                draft.garments.forEach((g, idx) => {
                    const gName = document.getElementById(`pos-g-name-${idx}`);
                    if (!gName) return;
                    g.name = gName.value;
                    g.category = document.getElementById(`pos-g-cat-${idx}`)?.value || g.category;
                    g.fabric = document.getElementById(`pos-g-fabric-${idx}`)?.value || '';
                    g.color = document.getElementById(`pos-g-color-${idx}`)?.value || '';
                    g.serviceId = Number(document.getElementById(`pos-g-srv-${idx}`)?.value) || '';
                    g.instructions = document.getElementById(`pos-g-notes-${idx}`)?.value || '';
                });
            };

            const getServicePrice = (serviceId) => {
                const srv = services.find(s => s.id === Number(serviceId));
                return Number(srv?.pricing_tiers?.[0]?.base_price || 0);
            };

            const updateRender = () => {
                const selectedCustomer = customers.find(c => c.id == draft.selectedCustomerId) || null;
                const subtotal = draft.garments.reduce((acc, g) => acc + (getServicePrice(g.serviceId) * (g.qty || 1)), 0);
                const tax = subtotal * 0.05;
                const net = subtotal + tax;

                container.innerHTML = `
                    <header class="sticky top-0 z-30 bg-surface-container-lowest border-b border-outline-variant/40 px-3 py-2.5 flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <button onclick="window.navigateTo('dashboard')" class="w-8 h-8 rounded-full bg-surface-container flex items-center justify-center text-on-surface active:scale-90">
                                <span class="material-symbols-outlined text-[18px]">arrow_back</span>
                            </button>
                            <h2 class="font-serif text-base font-bold text-primary">New Garment Intake</h2>
                        </div>
                        <span class="px-2 py-0.5 rounded-full bg-tertiary-fixed text-on-tertiary-fixed text-[10px] font-bold">POS Entry</span>
                    </header>

                    <div class="p-3 space-y-3">
                        <!-- Customer Patron Selector / Quick Register -->
                        <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-on-surface-variant uppercase tracking-wider">Client Registry</span>
                                <div class="flex gap-1 text-[10px] font-bold">
                                    <button type="button" id="btn-mode-new" class="px-2 py-0.5 rounded ${draft.customerMode === 'new' ? 'bg-primary-container text-white' : 'bg-surface-container text-on-surface-variant'}">+ New</button>
                                    ${customers.length > 0 ? `<button type="button" id="btn-mode-existing" class="px-2 py-0.5 rounded ${draft.customerMode === 'existing' ? 'bg-primary-container text-white' : 'bg-surface-container text-on-surface-variant'}">Existing</button>` : ''}
                                </div>
                            </div>

                            ${draft.customerMode === 'existing' && customers.length > 0 ? `
                                <select id="select-customer" class="w-full text-xs font-semibold px-3 py-2 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none">
                                    ${customers.map(c => `
                                        <option value="${c.id}" ${c.id == draft.selectedCustomerId ? 'selected' : ''}>${c.full_name} (${c.phone})</option>
                                    `).join('')}
                                </select>
                                <div class="text-[11px] text-on-surface-variant flex items-center justify-between pt-1">
                                    <span>Tier: <b class="text-primary">${selectedCustomer?.patron_tier || 'Standard'}</b></span>
                                    <span>Dues: <b class="text-error">₹${Number(selectedCustomer?.outstanding_dues || 0).toFixed(2)}</b></span>
                                </div>
                            ` : `
                                <div class="space-y-2">
                                    <input type="text" id="pos-new-cust-name" value="${draft.newCustName}" placeholder="Customer Full Name *" class="w-full text-xs px-3 py-2 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none"/>
                                    <input type="tel" id="pos-new-cust-phone" value="${draft.newCustPhone}" placeholder="10-Digit Mobile Number *" maxlength="10" class="w-full text-xs font-mono px-3 py-2 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none"/>
                                </div>
                            `}
                        </div>

                        <!-- Business Division Selector Tabs -->
                        <div class="space-y-1">
                            <label class="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Atelier Department</label>
                            <div class="grid grid-cols-2 gap-1 p-1 bg-surface-container rounded-xl">
                                <button type="button" id="tab-div-sd" class="py-2 px-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1 transition-all ${
                                    draft.division === "AASHIMA Stitchers 'N' Drapers" ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-on-surface-variant'
                                }">
                                    <span class="material-symbols-outlined text-[16px]">strikethrough_s</span>
                                    <span class="truncate">Stitchers 'N' Drapers</span>
                                </button>
                                <button type="button" id="tab-div-ww" class="py-2 px-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1 transition-all ${
                                    draft.division === "AASHIMA Women's World" ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-on-surface-variant'
                                }">
                                    <span class="material-symbols-outlined text-[16px]">dry_cleaning</span>
                                    <span class="truncate">Women's World</span>
                                </button>
                            </div>
                        </div>

                        <!-- Garment Items List -->
                        <div class="space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-on-surface uppercase tracking-wider flex items-center gap-1">
                                    <span class="material-symbols-outlined text-primary text-[18px]">checkroom</span>
                                    <span>Articles in Booking (${draft.garments.length})</span>
                                </span>
                                <button type="button" id="btn-add-garment" class="text-xs font-bold text-primary flex items-center gap-0.5 hover:underline">
                                    <span class="material-symbols-outlined text-[16px]">add_circle</span>
                                    <span>Add Article</span>
                                </button>
                            </div>

                            ${draft.garments.map((g, i) => `
                                <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-2">
                                    <div class="flex items-center justify-between">
                                        <span class="px-1.5 py-0.5 rounded bg-surface-container text-primary font-mono text-[10px] font-bold">Article #0${i + 1}</span>
                                        <span class="px-2 py-0.5 rounded-full bg-surface-container text-[10px] font-bold text-primary">₹${getServicePrice(g.serviceId).toFixed(2)}</span>
                                    </div>

                                    <input type="text" id="pos-g-name-${i}" value="${g.name}" placeholder="Garment name (e.g. Navy Coat / Silk Saree) *" class="w-full text-xs px-2.5 py-1.5 rounded-lg bg-surface-container-low border border-outline-variant outline-none"/>

                                    <div class="grid grid-cols-2 gap-1.5">
                                        <select id="pos-g-cat-${i}" class="w-full text-[11px] px-2 py-1.5 rounded-lg bg-surface-container-low border border-outline-variant outline-none">
                                            <optgroup label="Men's Bespoke">
                                                <option value="Coat / Blazer" ${g.category === 'Coat / Blazer' ? 'selected' : ''}>Coat / Blazer</option>
                                                <option value="Formal Shirt" ${g.category === 'Formal Shirt' ? 'selected' : ''}>Formal Shirt</option>
                                                <option value="Formal Trouser / Pant" ${g.category === 'Formal Trouser / Pant' ? 'selected' : ''}>Formal Trouser / Pant</option>
                                                <option value="Kurta Pajama" ${g.category === 'Kurta Pajama' ? 'selected' : ''}>Kurta Pajama</option>
                                                <option value="Sherwani / Bandhgala" ${g.category === 'Sherwani / Bandhgala' ? 'selected' : ''}>Sherwani / Bandhgala</option>
                                                <option value="Waistcoat / Nehru Jacket" ${g.category === 'Waistcoat / Nehru Jacket' ? 'selected' : ''}>Waistcoat / Nehru Jacket</option>
                                            </optgroup>
                                            <optgroup label="Women's Couture">
                                                <option value="Saree" ${g.category === 'Saree' ? 'selected' : ''}>Saree</option>
                                                <option value="Lehenga" ${g.category === 'Lehenga' ? 'selected' : ''}>Lehenga</option>
                                                <option value="Blouse" ${g.category === 'Blouse' ? 'selected' : ''}>Blouse</option>
                                                <option value="Kurti" ${g.category === 'Kurti' ? 'selected' : ''}>Kurti / Kameez</option>
                                                <option value="Salwar / Palazzo" ${g.category === 'Salwar / Palazzo' ? 'selected' : ''}>Salwar / Palazzo</option>
                                            </optgroup>
                                        </select>
                                        <input type="text" id="pos-g-fabric-${i}" value="${g.fabric}" placeholder="Fabric (Wool, Silk...)" class="w-full text-[11px] px-2 py-1.5 rounded-lg bg-surface-container-low border border-outline-variant outline-none"/>
                                    </div>

                                    <div class="grid grid-cols-2 gap-1.5">
                                        <input type="text" id="pos-g-color-${i}" value="${g.color}" placeholder="Color" class="w-full text-[11px] px-2 py-1.5 rounded-lg bg-surface-container-low border border-outline-variant outline-none"/>
                                        <select id="pos-g-srv-${i}" class="pos-srv-sel w-full text-[11px] px-2 py-1.5 rounded-lg bg-surface-container-low border border-outline-variant outline-none">
                                            ${services.map(s => `<option value="${s.id}" ${Number(g.serviceId) === s.id ? 'selected' : ''}>${s.name} (₹${s.pricing_tiers?.[0]?.base_price || 0})</option>`).join('')}
                                        </select>
                                    </div>

                                    <input type="text" id="pos-g-notes-${i}" value="${g.instructions}" placeholder="Tailor / cleaning directives (optional)" class="w-full text-[11px] px-2.5 py-1.5 rounded-lg bg-surface-container-low border border-outline-variant outline-none"/>

                                    <div class="flex items-center justify-between pt-1">
                                        <button type="button" onclick="window.posOpenMeasurements(${i})" class="text-[11px] ${g.measurement ? 'text-success' : 'text-secondary'} font-bold flex items-center gap-0.5 hover:underline">
                                            <span class="material-symbols-outlined text-[14px]">straighten</span>
                                            <span>${g.measurement ? `Measurements Linked (${g.measurement.template_garment_type})` : 'Add Men/Women Measurements'}</span>
                                        </button>
                                        ${draft.garments.length > 1 ? `
                                            <button type="button" onclick="window.removeGarment(${i})" class="text-[11px] text-error hover:underline">Remove</button>
                                        ` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>

                        <!-- Financial Summary & Advance -->
                        <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-2">
                            <span class="text-xs font-bold text-on-surface-variant uppercase tracking-wider block">Billing & Advance Payment</span>

                            <div class="space-y-1 text-xs">
                                <div class="flex justify-between text-on-surface-variant">
                                    <span>Articles Subtotal:</span>
                                    <span class="font-mono">₹${subtotal.toFixed(2)}</span>
                                </div>
                                <div class="flex justify-between text-on-surface-variant">
                                    <span>Estimated GST (5%):</span>
                                    <span class="font-mono">₹${tax.toFixed(2)}</span>
                                </div>
                                <div class="flex justify-between font-bold text-sm text-primary pt-1 border-t border-outline-variant/30">
                                    <span>Total Payable:</span>
                                    <span class="font-mono">₹${net.toFixed(2)}</span>
                                </div>
                            </div>

                            <div class="pt-2">
                                <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Advance Collected (₹)</label>
                                <div class="flex gap-2">
                                    <input type="number" id="input-advance" value="${draft.advance}" min="0" class="flex-1 px-3 py-2 rounded-lg bg-surface-container-low border border-outline-variant font-mono text-sm font-bold text-primary outline-none"/>
                                    <select id="select-pay-mode" class="px-2 py-2 rounded-lg bg-surface-container-low border border-outline-variant text-xs font-bold text-on-surface">
                                        <option value="UPI" ${draft.payMode === 'UPI' ? 'selected' : ''}>UPI</option>
                                        <option value="Cash" ${draft.payMode === 'Cash' ? 'selected' : ''}>Cash</option>
                                        <option value="Card" ${draft.payMode === 'Card' ? 'selected' : ''}>Card</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!-- Expected Handover Date -->
                        <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-1.5">
                            <label class="text-xs font-bold text-on-surface-variant uppercase tracking-wider block">Target Delivery Date</label>
                            <input type="date" id="input-due-date" value="${draft.dueDate}" class="w-full text-xs font-semibold px-3 py-2 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none"/>
                        </div>

                        <!-- Final Submission Button -->
                        <button id="btn-submit-booking" class="w-full py-3.5 rounded-xl bg-primary-container text-on-primary font-bold text-sm shadow-lg active:scale-95 transition-transform flex items-center justify-center gap-2">
                            <span class="material-symbols-outlined text-[20px] text-tertiary-fixed">qr_code_scanner</span>
                            <span>Generate Unique QR & Save Booking</span>
                        </button>
                    </div>
                `;

                const btnNew = document.getElementById('btn-mode-new');
                if (btnNew) btnNew.onclick = () => { syncDraftFromDOM(); draft.customerMode = 'new'; updateRender(); };
                const btnExisting = document.getElementById('btn-mode-existing');
                if (btnExisting) btnExisting.onclick = () => { syncDraftFromDOM(); draft.customerMode = 'existing'; updateRender(); };

                const selCust = document.getElementById('select-customer');
                if (selCust) selCust.onchange = (e) => { syncDraftFromDOM(); draft.selectedCustomerId = e.target.value; updateRender(); };

                container.querySelectorAll('.pos-srv-sel').forEach(sel => {
                    sel.onchange = () => { syncDraftFromDOM(); updateRender(); };
                });

                document.getElementById('tab-div-ww').onclick = () => {
                    syncDraftFromDOM();
                    draft.division = "AASHIMA Women's World";
                    updateRender();
                };

                document.getElementById('tab-div-sd').onclick = () => {
                    syncDraftFromDOM();
                    draft.division = "AASHIMA Stitchers 'N' Drapers";
                    updateRender();
                };

                document.getElementById('btn-add-garment').onclick = () => {
                    syncDraftFromDOM();
                    draft.garments.push({
                        id: Date.now(),
                        name: '',
                        category: 'Formal Shirt',
                        fabric: '',
                        color: '',
                        qty: 1,
                        serviceId: services[0]?.id || '',
                        instructions: '',
                        measurement: null
                    });
                    updateRender();
                };

                window.removeGarment = (index) => {
                    syncDraftFromDOM();
                    draft.garments.splice(index, 1);
                    updateRender();
                };

                window.posOpenMeasurements = (index) => {
                    syncDraftFromDOM();
                    this.navigateTo('measurements', { garmentIndex: index });
                };

                document.getElementById('btn-submit-booking').onclick = async () => {
                    syncDraftFromDOM();
                    try {
                        let customerId = draft.selectedCustomerId;
                        if (draft.customerMode === 'new' || !customerId) {
                            const fullName = draft.newCustName.trim();
                            const phone = draft.newCustPhone.replace(/\D/g, '').slice(-10);
                            if (!fullName || phone.length < 10) {
                                this.showToast('Enter customer name and valid 10-digit phone', true);
                                return;
                            }
                            const existingMatch = customers.find(c => c.phone.endsWith(phone));
                            if (existingMatch) {
                                customerId = existingMatch.id;
                            } else {
                                const createdCust = await api.createCustomer({
                                    full_name: fullName,
                                    phone: phone,
                                    patron_tier: 'Standard'
                                });
                                customerId = createdCust.id;
                            }
                        }

                        for (let i = 0; i < draft.garments.length; i++) {
                            if (!draft.garments[i].name.trim()) {
                                this.showToast(`Enter garment name for Article #0${i + 1}`, true);
                                return;
                            }
                        }

                        const payload = {
                            customer_id: Number(customerId),
                            division: draft.division,
                            order_type: 'Counter',
                            delivery_due_date: new Date(draft.dueDate).toISOString(),
                            is_urgent: false,
                            advance_payment_amount: draft.advance || 0,
                            advance_payment_mode: draft.payMode,
                            garments: draft.garments.map(g => ({
                                garment_name: g.name.trim(),
                                category: g.category,
                                fabric_type: g.fabric.trim() || 'Standard',
                                color: g.color.trim() || 'Standard',
                                quantity: g.qty || 1,
                                rack_location: 'Intake Counter',
                                special_instructions: g.instructions.trim() || '',
                                service_ids: [Number(g.serviceId)],
                                measurement: g.measurement || null
                            }))
                        };

                        const newBooking = await api.createBooking(payload);
                        this.draftBooking = null;
                        this.showToast(`Booking #${newBooking.booking_number} generated with QR tags!`);
                        this.navigateTo('thermal-print', { bookingId: newBooking.id });
                    } catch (err) {
                        this.showToast(err.message || 'Failed to create booking', true);
                    }
                };
            };

            updateRender();
        } catch (err) {
            container.innerHTML = `<div class="p-6 text-center text-error">${err.message}</div>`;
        }
    }

    // ==========================================
    // SCREEN 4: QR SCANNER (Camera + Tag Decoder)
    // ==========================================
    async renderQRScanner(container) {
        container.innerHTML = `
            <header class="sticky top-0 z-30 bg-primary-container text-on-primary px-3 py-2.5 flex items-center justify-between shadow-md">
                <div class="flex items-center gap-2">
                    <button onclick="window.navigateTo('dashboard')" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-90">
                        <span class="material-symbols-outlined text-[18px]">arrow_back</span>
                    </button>
                    <h2 class="font-serif text-base font-bold tracking-wide">Live Tag Scanner</h2>
                </div>
                <span class="text-[10px] text-tertiary-fixed font-semibold uppercase tracking-wider">Garment QR</span>
            </header>

            <div class="p-4 flex-1 flex flex-col justify-between">
                <div>
                    <!-- Camera Viewfinder -->
                    <div class="relative w-full aspect-square max-h-[300px] rounded-2xl overflow-hidden bg-black flex items-center justify-center shadow-inner border-2 border-primary-container">
                        <div id="reader" class="w-full h-full"></div>
                        <div class="absolute inset-8 border-2 border-dashed border-tertiary-fixed/80 rounded-xl pointer-events-none flex items-center justify-center">
                            <span class="text-[11px] text-white/90 bg-black/60 px-2 py-0.5 rounded font-mono">Frame Barcode Tag</span>
                        </div>
                    </div>

                    <!-- Manual Fallback Input -->
                    <div class="mt-4 p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-2">
                        <label class="text-xs font-bold text-on-surface-variant block">Manual Code / Token Input</label>
                        <div class="flex gap-2">
                            <input type="text" id="manual-qr-input" placeholder="e.g. QR-ASH-1001-G01" value="" class="flex-1 px-3 py-2 rounded-lg bg-surface-container-low border border-outline-variant text-xs font-mono font-bold text-primary outline-none focus:border-primary-container"/>
                            <button id="btn-manual-scan" class="px-4 py-2 rounded-lg bg-primary-container text-on-primary text-xs font-bold active:scale-95 shadow">Match</button>
                        </div>
                    </div>
                </div>

                <div class="text-center text-xs text-on-surface-variant py-2">
                    <p>Point camera at 58mm/80mm thermal tag.</p>
                    <p class="text-[10px] text-secondary mt-0.5">Scans trigger instant Stage Transition Dossier.</p>
                </div>
            </div>
        `;

        const onScanSuccess = async (decodedText) => {
            if (this.html5QrCode) {
                try { await this.html5QrCode.stop(); } catch(e){}
            }
            this.handleScanResult(decodedText);
        };

        // Try initializing Camera if supported
        if (typeof Html5Qrcode !== 'undefined') {
            try {
                this.html5QrCode = new Html5Qrcode("reader");
                await this.html5QrCode.start(
                    { facingMode: "environment" },
                    { fps: 10, qrbox: { width: 220, height: 220 } },
                    onScanSuccess,
                    () => {}
                );
            } catch (err) {
                console.warn("Camera auto-start not permitted or unavailable:", err);
            }
        }

        document.getElementById('btn-manual-scan').onclick = () => {
            const val = document.getElementById('manual-qr-input').value.trim();
            if (val) this.handleScanResult(val);
        };
    }

    async handleScanResult(scannedText) {
        try {
            const res = await api.scanQR(scannedText);
            this.showToast(`Matched: ${res.garment_code}`);
            this.navigateTo('stage-update', { scanData: res });
        } catch (err) {
            this.showToast(err.message || 'QR tag not recognized', true);
        }
    }

    // ==========================================
    // SCREEN 5: STAGE UPDATE (Stitch QR Tracking)
    // ==========================================
    async renderStageUpdate(container, params = {}) {
        if (!params.scanData) {
            container.innerHTML = `
                <header class="sticky top-0 z-30 bg-primary-container text-on-primary px-3 py-2.5 flex items-center justify-between shadow-md">
                    <div class="flex items-center gap-2">
                        <button onclick="window.navigateTo('qr-scan')" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-90">
                            <span class="material-symbols-outlined text-[18px]">arrow_back</span>
                        </button>
                        <h2 class="font-serif text-base font-bold tracking-wide">Garment Dossier</h2>
                    </div>
                </header>
                <div class="p-8 text-center space-y-3">
                    <div class="w-16 h-16 rounded-2xl bg-surface-container flex items-center justify-center mx-auto text-outline">
                        <span class="material-symbols-outlined text-[36px]">qr_code_scanner</span>
                    </div>
                    <h3 class="font-serif text-lg font-bold text-primary">No Garment Scanned</h3>
                    <p class="text-xs text-on-surface-variant max-w-xs mx-auto">Please scan a garment thermal QR tag or select a garment from Orders / Floor to update its workflow stage.</p>
                    <div class="pt-2 flex justify-center gap-2">
                        <button onclick="window.navigateTo('qr-scan')" class="px-4 py-2 rounded-xl bg-primary-container text-white font-bold text-xs shadow-md">Open QR Scanner</button>
                        <button onclick="window.navigateTo('departments')" class="px-4 py-2 rounded-xl bg-surface-container text-primary font-bold text-xs border border-outline-variant/40">Floor Queue</button>
                    </div>
                </div>
            `;
            return;
        }

        const data = params.scanData;

        const stages = [
            'Booking Received',
            'Alteration',
            'Deep Cleaning',
            'Finishing',
            'Delivery Centre',
            'Ready for Delivery',
            'Delivered'
        ];

        let selectedStage = data.current_stage;

        container.innerHTML = `
            <header class="sticky top-0 z-30 bg-primary-container text-on-primary px-3 py-2.5 flex items-center justify-between shadow-md">
                <div class="flex items-center gap-2">
                    <button onclick="window.navigateTo('qr-scan')" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-90">
                        <span class="material-symbols-outlined text-[18px]">arrow_back</span>
                    </button>
                    <h2 class="font-serif text-base font-bold tracking-wide">Garment Dossier</h2>
                </div>
                <span class="text-[10px] text-tertiary-fixed font-semibold uppercase">Floor Update</span>
            </header>

            <div class="p-3 space-y-3">
                <!-- Verified Identifier Banner -->
                <div class="p-2.5 rounded-xl bg-surface-container-low border border-outline-variant/60 shadow-sm flex items-center justify-between">
                    <div class="flex items-center gap-2 min-w-0">
                        <div class="w-8 h-8 rounded-full bg-secondary-container text-on-secondary-container flex items-center justify-center shrink-0">
                            <span class="material-symbols-outlined text-[18px]">check_circle</span>
                        </div>
                        <div class="min-w-0">
                            <span class="text-[10px] font-bold text-on-surface-variant uppercase">Scanned Tag</span>
                            <p class="font-mono text-xs font-bold text-primary truncate">${data.garment_code}</p>
                        </div>
                    </div>
                    <span class="px-2 py-0.5 rounded bg-tertiary-fixed text-on-tertiary-fixed text-[10px] font-bold">100% Match</span>
                </div>

                <!-- Customer & Article Card -->
                <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-2">
                    <div class="flex justify-between items-start">
                        <div>
                            <span class="px-2 py-0.2 rounded-full bg-surface-container text-primary font-mono text-[9px] font-bold uppercase">${data.article_tag || 'ARTICLE'}</span>
                            <h3 class="font-serif text-base font-bold text-on-surface mt-0.5">${data.garment_name}</h3>
                            <p class="text-[11px] text-on-surface-variant">${data.fabric_type} • ${data.color}</p>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-on-surface-variant block uppercase font-bold">Booking</span>
                            <span class="font-mono text-xs font-bold text-primary">#${data.booking_number}</span>
                        </div>
                    </div>

                    <!-- Client Summary -->
                    <div class="p-2 rounded-lg bg-surface-container flex items-center justify-between">
                        <div class="min-w-0 pr-2">
                            <p class="text-xs font-bold text-on-surface truncate">${data.customer_name}</p>
                            <p class="text-[10px] text-on-surface-variant">${data.customer_phone} • ${data.customer_unit || 'Counter'}</p>
                        </div>
                        <div class="flex items-center gap-1">
                            <a href="tel:${data.customer_phone}" class="w-7 h-7 rounded-full bg-surface-container-lowest flex items-center justify-center text-primary shadow-sm">
                                <span class="material-symbols-outlined text-[14px]">call</span>
                            </a>
                            <a href="https://wa.me/91${data.customer_phone}" target="_blank" class="w-7 h-7 rounded-full bg-surface-container-lowest flex items-center justify-center text-success shadow-sm">
                                <span class="material-symbols-outlined text-[14px]">chat</span>
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Intake Photographic Proof Snapshot -->
                ${data.photo_urls && data.photo_urls.length > 0 ? `
                    <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-1.5">
                        <span class="text-xs font-bold text-on-surface-variant uppercase tracking-wider block">Intake Visual Proof</span>
                        <div class="relative h-32 rounded-lg overflow-hidden border border-outline-variant/40">
                            <img src="${data.photo_urls[0]}" alt="Intake proof" class="w-full h-full object-cover"/>
                            <span class="absolute bottom-1 left-1 bg-black/70 text-white text-[9px] px-1.5 py-0.5 rounded font-mono">Intake Inspection</span>
                        </div>
                    </div>
                ` : ''}

                <!-- Stage Transition Selector -->
                <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-2">
                    <span class="text-xs font-bold text-on-surface-variant uppercase tracking-wider block">Advance Workflow Stage</span>
                    <div class="grid grid-cols-2 gap-1.5">
                        ${stages.map(st => `
                            <button type="button" class="stage-btn py-2 px-2 rounded-lg text-xs font-bold text-center border transition-all ${
                                st === selectedStage
                                    ? 'bg-primary-container text-white border-primary-container shadow'
                                    : 'bg-surface-container-low text-on-surface-variant border-outline-variant/40 hover:bg-surface-container'
                            }" data-stage="${st}">
                                ${st}
                            </button>
                        `).join('')}
                    </div>

                    <!-- Karigar Assignment & Notes -->
                    <div class="pt-2 space-y-2">
                        <div>
                            <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Assign Tailor / Staff</label>
                            <input type="text" id="select-karigar" value="${data.karigar_name || ''}" placeholder="Enter assigned tailor or staff name" class="w-full text-xs font-semibold px-2.5 py-2 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none focus:border-primary-container"/>
                        </div>

                        <div>
                            <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Floor Remarks / Directive</label>
                            <input type="text" id="stage-remarks" placeholder="e.g. QC passed, steam finish completed." value="" class="w-full text-xs px-2.5 py-2 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none focus:border-primary-container"/>
                        </div>
                    </div>
                </div>

                <!-- Submit Transition -->
                <button id="btn-save-stage" class="w-full py-3.5 rounded-xl bg-primary-container text-on-primary font-bold text-sm shadow-md active:scale-95 transition-transform flex items-center justify-center gap-2">
                    <span class="material-symbols-outlined text-[18px]">verified</span>
                    <span>Complete Stage Transition</span>
                </button>
            </div>
        `;

        // Handle stage click
        container.querySelectorAll('.stage-btn').forEach(btn => {
            btn.onclick = () => {
                container.querySelectorAll('.stage-btn').forEach(b => {
                    b.classList.remove('bg-primary-container', 'text-white', 'shadow');
                    b.classList.add('bg-surface-container-low', 'text-on-surface-variant');
                });
                btn.classList.add('bg-primary-container', 'text-white', 'shadow');
                btn.classList.remove('bg-surface-container-low', 'text-on-surface-variant');
                selectedStage = btn.dataset.stage;
            };
        });

        document.getElementById('btn-save-stage').onclick = async () => {
            const remarks = document.getElementById('stage-remarks').value;
            const karigar = document.getElementById('select-karigar').value;
            try {
                await api.transitionGarmentStage(data.garment_id, {
                    new_stage: selectedStage,
                    remarks: remarks,
                    assigned_karigar_name: karigar
                });
                this.showToast(`Updated to ${selectedStage}! Customer notified.`);
                this.navigateTo('dashboard');
            } catch (err) {
                this.showToast(err.message || 'Stage transition failed', true);
            }
        };
    }

    // ==========================================
    // SCREEN 6: MEASUREMENT MATRIX (Men's & Women's)
    // ==========================================
    async renderMeasurementMatrix(container, params = {}) {
        const templates = await api.getMeasurementTemplates();
        const garmentIndex = params.garmentIndex;
        const draftGarment = (typeof garmentIndex === 'number' && this.draftBooking?.garments?.[garmentIndex])
            ? this.draftBooking.garments[garmentIndex]
            : null;

        let activeGender = 'Men';
        let activeTemplate = templates.find(t => t.garment_type === draftGarment?.measurement?.template_garment_type)
            || templates.find(t => (t.silhouette_icon || '').toLowerCase() === 'men')
            || templates[0];

        if (activeTemplate) {
            activeGender = (activeTemplate.silhouette_icon || 'Men').toLowerCase() === 'men' ? 'Men' : 'Women';
        }

        let currentValues = { ...(draftGarment?.measurement?.measurements || {}) };
        let karigarNotes = draftGarment?.measurement?.karigar_directives || '';

        const updateMatrix = () => {
            const genderTemplates = templates.filter(t =>
                activeGender === 'Men'
                    ? (t.silhouette_icon || '').toLowerCase() === 'men'
                    : (t.silhouette_icon || '').toLowerCase() !== 'men'
            );

            if (!activeTemplate || !genderTemplates.some(t => t.garment_type === activeTemplate.garment_type)) {
                activeTemplate = genderTemplates[0] || templates[0];
            }

            const fields = activeTemplate ? JSON.parse(activeTemplate.anchor_fields || '[]') : [];

            container.innerHTML = `
                <header class="sticky top-0 z-30 bg-primary-container text-on-primary px-3 py-2.5 flex items-center justify-between shadow-md">
                    <div class="flex items-center gap-2">
                        <button onclick="window.navigateTo('${draftGarment ? 'new-booking' : 'dashboard'}')" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-90">
                            <span class="material-symbols-outlined text-[18px]">arrow_back</span>
                        </button>
                        <h2 class="font-serif text-base font-bold tracking-wide">Measurement Book</h2>
                    </div>
                    <!-- Unit Switcher -->
                    <div class="bg-white/10 rounded-full p-0.5 flex border border-white/20">
                        <button id="btn-unit-inch" class="px-2.5 py-0.5 rounded-full text-[10px] font-bold transition-all ${
                            this.measurementUnit === 'inch' ? 'bg-white text-primary shadow' : 'text-white/80'
                        }">INCH (")</button>
                        <button id="btn-unit-cm" class="px-2.5 py-0.5 rounded-full text-[10px] font-bold transition-all ${
                            this.measurementUnit === 'cm' ? 'bg-white text-primary shadow' : 'text-white/80'
                        }">CM</button>
                    </div>
                </header>

                <div class="p-3 space-y-3">
                    <!-- Men's / Women's Switcher -->
                    <div class="grid grid-cols-2 gap-1 p-1 bg-surface-container rounded-xl">
                        <button type="button" id="btn-gender-men" class="py-2 rounded-lg text-xs font-bold transition-all ${
                            activeGender === 'Men' ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-on-surface-variant'
                        }">Men's Tailoring</button>
                        <button type="button" id="btn-gender-women" class="py-2 rounded-lg text-xs font-bold transition-all ${
                            activeGender === 'Women' ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-on-surface-variant'
                        }">Women's Couture</button>
                    </div>

                    <!-- Garment Template Selector -->
                    <div class="p-2.5 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-1">
                        <label class="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">Select Garment Matrix</label>
                        <select id="sel-meas-template" class="w-full text-xs font-bold px-2.5 py-2 rounded-lg bg-surface-container-low border border-outline-variant text-primary outline-none">
                            ${genderTemplates.map(t => `
                                <option value="${t.garment_type}" ${t.garment_type === activeTemplate?.garment_type ? 'selected' : ''}>${t.display_title}</option>
                            `).join('')}
                        </select>
                        <p class="text-[10px] text-on-surface-variant pt-0.5">${fields.length} tailoring anchor points • Step ${activeTemplate?.step_increment || 0.25}"</p>
                    </div>

                    <!-- Granular 2-Column Matrix Grid -->
                    <div class="grid grid-cols-2 gap-2">
                        ${fields.map(f => {
                            const hasVal = currentValues[f.name] !== undefined && currentValues[f.name] !== '';
                            const val = hasVal ? Number(currentValues[f.name]) : '';
                            return `
                                <div class="p-2.5 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm flex flex-col justify-between">
                                    <div class="flex items-center justify-between gap-1">
                                        <span class="text-[11px] font-bold text-on-surface truncate" title="${f.label}">${f.label}</span>
                                        <span class="text-[9px] text-outline font-mono shrink-0">${f.min}–${f.max}</span>
                                    </div>
                                    <div class="flex items-center justify-between gap-1 mt-2">
                                        <button type="button" onclick="window.stepMeasurement('${f.name}', -0.25, ${f.min})" class="w-7 h-7 rounded-lg bg-surface-container flex items-center justify-center font-bold text-primary active:scale-90 text-sm shrink-0">-</button>
                                        <input type="number" step="0.25" min="0" data-pos-meas="${f.name}" value="${val}" placeholder="--" class="w-full text-center font-mono text-sm font-bold text-primary bg-surface-container-low rounded py-1 border border-outline-variant/40 outline-none"/>
                                        <button type="button" onclick="window.stepMeasurement('${f.name}', 0.25, ${f.min})" class="w-7 h-7 rounded-lg bg-surface-container flex items-center justify-center font-bold text-primary active:scale-90 text-sm shrink-0">+</button>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>

                    <!-- Karigar Directives -->
                    <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-1.5">
                        <label class="text-xs font-bold text-on-surface-variant uppercase tracking-wider block">Special Tailor Directives</label>
                        <textarea id="karigar-notes" rows="2" class="w-full text-xs p-2.5 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none focus:border-primary-container" placeholder="${activeTemplate?.special_directives_placeholder || 'Enter bespoke cutting or fitting notes'}">${karigarNotes}</textarea>
                    </div>

                    <!-- Save & Link Button -->
                    <button id="btn-save-measurements" class="w-full py-3.5 rounded-xl bg-primary-container text-on-primary font-bold text-sm shadow-md active:scale-95 transition-transform flex items-center justify-center gap-2">
                        <span class="material-symbols-outlined text-[18px]">save</span>
                        <span>${draftGarment ? 'Link Measurements to Article' : 'Save & Start New Booking'}</span>
                    </button>
                </div>
            `;

            const syncInputs = () => {
                container.querySelectorAll('[data-pos-meas]').forEach(inp => {
                    const key = inp.dataset.posMeas;
                    if (inp.value === '') {
                        delete currentValues[key];
                    } else {
                        currentValues[key] = parseFloat(inp.value);
                    }
                });
                karigarNotes = document.getElementById('karigar-notes')?.value || '';
            };

            container.querySelectorAll('[data-pos-meas]').forEach(inp => {
                inp.onchange = syncInputs;
            });

            document.getElementById('btn-gender-men').onclick = () => {
                syncInputs();
                activeGender = 'Men';
                currentValues = {};
                updateMatrix();
            };

            document.getElementById('btn-gender-women').onclick = () => {
                syncInputs();
                activeGender = 'Women';
                currentValues = {};
                updateMatrix();
            };

            document.getElementById('sel-meas-template').onchange = (e) => {
                syncInputs();
                activeTemplate = templates.find(t => t.garment_type === e.target.value);
                currentValues = {};
                updateMatrix();
            };

            document.getElementById('btn-unit-inch').onclick = () => {
                syncInputs();
                this.measurementUnit = 'inch';
                updateMatrix();
            };

            document.getElementById('btn-unit-cm').onclick = () => {
                syncInputs();
                this.measurementUnit = 'cm';
                updateMatrix();
            };

            window.stepMeasurement = (key, delta, minVal) => {
                syncInputs();
                const current = currentValues[key] !== undefined ? Number(currentValues[key]) : Number(minVal || 10);
                currentValues[key] = Math.max(0.25, Math.round((current + delta) * 100) / 100);
                updateMatrix();
            };

            document.getElementById('btn-save-measurements').onclick = () => {
                syncInputs();
                if (Object.keys(currentValues).length === 0) {
                    this.showToast('Please enter at least one measurement value', true);
                    return;
                }
                const measPayload = {
                    template_garment_type: activeTemplate.garment_type,
                    unit: this.measurementUnit.toUpperCase(),
                    measurements: { ...currentValues },
                    karigar_directives: karigarNotes.trim() || null
                };
                if (draftGarment) {
                    draftGarment.measurement = measPayload;
                    this.showToast(`Linked ${activeTemplate.display_title} measurements!`);
                } else {
                    this.showToast(`Saved ${activeTemplate.display_title} measurements!`);
                }
                this.navigateTo('new-booking');
            };
        };

        updateMatrix();
    }

    // ==========================================
    // SCREEN 7: ORDER MANAGEMENT & TIMELINE
    // ==========================================
    async renderOrderManagement(container) {
        try {
            const bookings = await api.getBookings();
            container.innerHTML = `
                <header class="sticky top-0 z-30 bg-primary-container text-on-primary px-3 py-2.5 flex items-center justify-between shadow-md">
                    <div class="flex items-center gap-2">
                        <button onclick="window.navigateTo('dashboard')" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-90">
                            <span class="material-symbols-outlined text-[18px]">arrow_back</span>
                        </button>
                        <div>
                            <h2 class="font-serif text-base font-bold tracking-wide leading-tight">Production Orders</h2>
                            <span class="text-[10px] text-tertiary-fixed font-semibold uppercase">${bookings.length} Active Slips</span>
                        </div>
                    </div>
                    <button onclick="window.navigateTo('new-booking')" class="px-2.5 py-1.5 rounded-lg bg-tertiary-fixed text-on-tertiary-fixed font-bold text-xs flex items-center gap-1 shadow active:scale-95">
                        <span class="material-symbols-outlined text-[16px]">add_circle</span>
                        <span>Intake</span>
                    </button>
                </header>

                <div class="p-3 space-y-2">
                    ${bookings.length > 0 ? bookings.map(b => `
                        <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-2">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="flex items-center gap-1.5">
                                        <span class="font-mono text-xs font-bold text-primary">#${b.booking_number}</span>
                                        <span class="px-2 py-0.2 rounded-full text-[9px] font-bold ${
                                            b.current_status === 'Delivered' ? 'bg-success/20 text-success' : 'bg-secondary-container text-on-secondary-container'
                                        }">${b.current_status}</span>
                                    </div>
                                    <h4 class="text-xs font-bold text-on-surface mt-0.5">${b.customer?.full_name || 'Counter Patron'}</h4>
                                </div>
                                <div class="text-right">
                                    <span class="font-serif text-xs font-bold text-primary">₹${b.net_amount}</span>
                                    <span class="text-[10px] block ${b.balance_due > 0 ? 'text-error' : 'text-success'}">
                                        ${b.balance_due > 0 ? `Due: ₹${b.balance_due}` : 'Fully Paid'}
                                    </span>
                                </div>
                            </div>

                            <div class="text-[11px] text-on-surface-variant bg-surface-container-low p-2 rounded-lg space-y-1">
                                <div class="flex justify-between">
                                    <span>Division: ${b.division}</span>
                                    <span>Articles: ${b.garments?.length || 1}</span>
                                </div>
                                <div>Due: ${new Date(b.delivery_due_date).toLocaleDateString()}</div>
                            </div>

                            <div class="flex gap-2 pt-1">
                                <button onclick="window.navigateTo('thermal-print', { bookingId: ${b.id} })" class="flex-1 py-1.5 rounded-lg bg-surface-container text-primary font-bold text-xs flex items-center justify-center gap-1 hover:bg-primary hover:text-white transition-colors">
                                    <span class="material-symbols-outlined text-[14px]">receipt_long</span>
                                    <span>Print Tag</span>
                                </button>
                                <button onclick="window.navigateTo('stage-update', { scanData: { booking_id: ${b.id}, garment_id: ${b.garments[0]?.id || 1}, garment_code: '${b.booking_number}-G01', garment_name: '${b.garments[0]?.garment_name || 'Garment'}', booking_number: '${b.booking_number}', customer_name: '${b.customer?.full_name}', customer_phone: '${b.customer?.phone}', current_stage: '${b.current_status}' } })" class="flex-1 py-1.5 rounded-lg bg-primary-container text-white font-bold text-xs flex items-center justify-center gap-1">
                                    <span class="material-symbols-outlined text-[14px]">update</span>
                                    <span>Update Stage</span>
                                </button>
                            </div>
                        </div>
                    `).join('') : `
                        <div class="p-8 rounded-2xl bg-surface-container-lowest border border-outline-variant/40 text-center space-y-3 my-6">
                            <div class="w-14 h-14 rounded-2xl bg-surface-container flex items-center justify-center mx-auto text-outline">
                                <span class="material-symbols-outlined text-[32px]">inventory_2</span>
                            </div>
                            <h3 class="font-serif text-base font-bold text-primary">No Active Orders</h3>
                            <p class="text-xs text-on-surface-variant">Start a new garment intake booking right from the mobile counter.</p>
                            <button onclick="window.navigateTo('new-booking')" class="px-5 py-2.5 rounded-xl bg-primary-container text-on-primary font-bold text-xs inline-flex items-center gap-1.5 shadow-md active:scale-95">
                                <span class="material-symbols-outlined text-[16px]">add_circle</span>
                                <span>New Order Intake</span>
                            </button>
                        </div>
                    `}
                </div>
            `;
        } catch (err) {
            container.innerHTML = `<div class="p-6 text-center text-error">${err.message}</div>`;
        }
    }

    // ==========================================
    // SCREEN 8: DEPARTMENT QUEUES
    // ==========================================
    async renderDepartmentQueue(container, params = {}) {
        const activeDept = params.dept || 'alteration';
        try {
            const garments = await api.getDepartmentQueue(activeDept);
            const deptTitles = {
                'alteration': 'Alteration & Karigari Wing',
                'deep-cleaning': 'Organic Dry Cleaning Hub',
                'finishing': 'Steam Polish & Finishing',
                'delivery-centre': 'Delivery Centre & Handover'
            };

            container.innerHTML = `
                <header class="sticky top-0 z-30 bg-primary-container text-on-primary px-3 py-2.5 flex items-center justify-between shadow-md">
                    <div class="flex items-center gap-2">
                        <button onclick="window.navigateTo('dashboard')" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-90">
                            <span class="material-symbols-outlined text-[18px]">arrow_back</span>
                        </button>
                        <h2 class="font-serif text-base font-bold tracking-wide">${deptTitles[activeDept]}</h2>
                    </div>
                    <span class="text-[10px] text-tertiary-fixed font-semibold uppercase">${garments.length} Active</span>
                </header>

                <!-- Department Tabs -->
                <div class="p-2 bg-surface-container flex gap-1 overflow-x-auto no-scrollbar">
                    <button onclick="window.navigateTo('departments', { dept: 'alteration' })" class="px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap ${
                        activeDept === 'alteration' ? 'bg-primary-container text-white' : 'bg-surface text-on-surface-variant'
                    }">Alteration</button>
                    <button onclick="window.navigateTo('departments', { dept: 'deep-cleaning' })" class="px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap ${
                        activeDept === 'deep-cleaning' ? 'bg-primary-container text-white' : 'bg-surface text-on-surface-variant'
                    }">Deep Clean</button>
                    <button onclick="window.navigateTo('departments', { dept: 'finishing' })" class="px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap ${
                        activeDept === 'finishing' ? 'bg-primary-container text-white' : 'bg-surface text-on-surface-variant'
                    }">Finishing</button>
                    <button onclick="window.navigateTo('departments', { dept: 'delivery-centre' })" class="px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap ${
                        activeDept === 'delivery-centre' ? 'bg-primary-container text-white' : 'bg-surface text-on-surface-variant'
                    }">Delivery Centre</button>
                </div>

                <div class="p-3 space-y-2">
                    ${garments.length > 0 ? garments.map(g => `
                        <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm flex items-center justify-between">
                            <div>
                                <span class="font-mono text-[10px] font-bold text-primary">${g.garment_code}</span>
                                <h4 class="text-xs font-bold text-on-surface">${g.garment_name}</h4>
                                <p class="text-[10px] text-on-surface-variant">Rack: ${g.rack_location || 'Floor'} • Karigar: ${g.karigar_name || 'Unassigned'}</p>
                            </div>
                            <button onclick="window.navigateTo('stage-update', { scanData: { garment_id: ${g.id}, garment_code: '${g.garment_code}', garment_name: '${g.garment_name}', current_stage: '${g.current_stage}', booking_number: '${g.garment_code.split('-G')[0]}', customer_name: '${g.booking?.customer?.full_name || 'Counter Patron'}', customer_phone: '${g.booking?.customer?.phone || ''}' } })" class="px-3 py-1.5 rounded-lg bg-primary-container text-white text-xs font-bold">
                                Next Stage
                            </button>
                        </div>
                    `).join('') : `
                        <div class="p-6 text-center text-xs text-on-surface-variant">
                            No garments currently queued in this wing.
                        </div>
                    `}
                </div>
            `;
        } catch (err) {
            container.innerHTML = `<div class="p-6 text-center text-error">${err.message}</div>`;
        }
    }

    // ==========================================
    // SCREEN 9: PAYMENTS COLLECTION
    // ==========================================
    async renderPayments(container) {
        try {
            const daybook = await api.getDaybookSummary();
            const bookings = await api.getBookings();
            const unpaidBookings = bookings.filter(b => b.payment_status !== 'Paid');

            container.innerHTML = `
                <header class="sticky top-0 z-30 bg-primary-container text-on-primary px-3 py-2.5 flex items-center justify-between shadow-md">
                    <div class="flex items-center gap-2">
                        <button onclick="window.navigateTo('dashboard')" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-90">
                            <span class="material-symbols-outlined text-[18px]">arrow_back</span>
                        </button>
                        <h2 class="font-serif text-base font-bold tracking-wide">Collect Payment</h2>
                    </div>
                    <span class="text-[10px] text-tertiary-fixed font-semibold uppercase">Counter Ledger</span>
                </header>

                <div class="p-3 space-y-3">
                    <!-- Daybook Position -->
                    <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm flex items-center justify-between">
                        <div>
                            <span class="text-[10px] text-on-surface-variant font-bold uppercase">Shift Collection</span>
                            <p class="font-serif text-xl font-bold text-primary">₹${Number(daybook.collected_today).toLocaleString('en-IN')}</p>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-on-surface-variant font-bold uppercase">Outstanding Dues</span>
                            <p class="font-serif text-xl font-bold text-error">₹${Number(daybook.pending_balance).toLocaleString('en-IN')}</p>
                        </div>
                    </div>

                    <!-- Payment Form -->
                    ${unpaidBookings.length > 0 ? `
                    <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-3">
                        <span class="text-xs font-bold text-on-surface-variant uppercase tracking-wider block">Record Balance Handover</span>

                        <div>
                            <label class="text-xs font-bold text-on-surface-variant block mb-1">Select Order with Pending Balance</label>
                            <select id="select-unpaid-order" class="w-full text-xs font-semibold px-3 py-2.5 rounded-lg bg-surface-container-low border border-outline-variant text-on-surface outline-none">
                                ${unpaidBookings.map(b => `
                                    <option value="${b.id}" data-due="${b.balance_due}">#${b.booking_number} - ${b.customer?.full_name} (Due: ₹${b.balance_due})</option>
                                `).join('')}
                            </select>
                        </div>

                        <div>
                            <label class="text-xs font-bold text-on-surface-variant block mb-1">Payment Amount (₹)</label>
                            <input type="number" id="pay-amount" value="${unpaidBookings[0]?.balance_due || 0}" class="w-full px-3 py-2.5 rounded-lg bg-surface-container-low border border-outline-variant text-sm font-mono font-bold text-primary outline-none"/>
                        </div>

                        <div class="grid grid-cols-3 gap-1.5">
                            <button type="button" class="pay-mode-btn py-2 rounded-lg text-xs font-bold border border-primary-container bg-primary-container text-white" data-mode="UPI">UPI</button>
                            <button type="button" class="pay-mode-btn py-2 rounded-lg text-xs font-bold border border-outline-variant bg-surface-container-low text-on-surface" data-mode="Cash">Cash</button>
                            <button type="button" class="pay-mode-btn py-2 rounded-lg text-xs font-bold border border-outline-variant bg-surface-container-low text-on-surface" data-mode="Card">Card</button>
                        </div>

                        <div>
                            <label class="text-xs font-bold text-on-surface-variant block mb-1">UPI UTR / Auth Reference</label>
                            <input type="text" id="pay-txn" placeholder="12-digit UPI UTR or reference (optional)" value="" class="w-full px-3 py-2 rounded-lg bg-surface-container-low border border-outline-variant text-xs outline-none focus:border-primary-container"/>
                        </div>

                        <button id="btn-collect-pay" class="w-full py-3 rounded-xl bg-primary-container text-on-primary font-bold text-sm shadow-md active:scale-95 transition-transform flex items-center justify-center gap-2">
                            <span class="material-symbols-outlined text-[18px]">receipt_long</span>
                            <span>Generate Receipt & Settle</span>
                        </button>
                    </div>
                    ` : `
                    <div class="p-6 rounded-xl bg-surface-container-lowest border border-outline-variant/40 text-center space-y-2">
                        <span class="material-symbols-outlined text-[32px] text-success">verified</span>
                        <h3 class="font-serif text-sm font-bold text-primary">All Dues Settled</h3>
                        <p class="text-xs text-on-surface-variant">No pending order balances to collect right now.</p>
                    </div>
                    `}
                </div>
            `;

            if (unpaidBookings.length === 0) return;

            let selectedMode = 'UPI';
            container.querySelectorAll('.pay-mode-btn').forEach(btn => {
                btn.onclick = () => {
                    container.querySelectorAll('.pay-mode-btn').forEach(b => {
                        b.classList.remove('bg-primary-container', 'text-white', 'border-primary-container');
                        b.classList.add('bg-surface-container-low', 'text-on-surface', 'border-outline-variant');
                    });
                    btn.classList.add('bg-primary-container', 'text-white', 'border-primary-container');
                    btn.classList.remove('bg-surface-container-low', 'text-on-surface', 'border-outline-variant');
                    selectedMode = btn.dataset.mode;
                };
            });

            document.getElementById('select-unpaid-order').onchange = (e) => {
                const opt = e.target.options[e.target.selectedIndex];
                document.getElementById('pay-amount').value = opt.dataset.due || 0;
            };

            document.getElementById('btn-collect-pay').onclick = async () => {
                const bId = parseInt(document.getElementById('select-unpaid-order').value);
                const amt = parseFloat(document.getElementById('pay-amount').value);
                const txn = document.getElementById('pay-txn').value;

                try {
                    await api.addPayment({
                        booking_id: bId,
                        amount: amt,
                        payment_type: 'Partial',
                        payment_mode: selectedMode,
                        transaction_id: txn,
                        notes: 'Counter payment collected via Android POS'
                    });
                    this.showToast('Payment settled and receipt recorded!');
                    this.navigateTo('dashboard');
                } catch (err) {
                    this.showToast(err.message || 'Payment collection failed', true);
                }
            };
        } catch (err) {
            container.innerHTML = `<div class="p-6 text-center text-error">${err.message}</div>`;
        }
    }

    // ==========================================
    // SCREEN 10: THERMAL PRINT PREVIEW & PRINTING
    // ==========================================
    async renderThermalPrint(container, params = {}) {
        try {
            let bookingId = params.bookingId;
            if (!bookingId) {
                const recent = await api.getBookings();
                if (!recent || recent.length === 0) {
                    container.innerHTML = `
                        <header class="sticky top-0 z-30 bg-primary-container text-on-primary px-3 py-2.5 flex items-center justify-between shadow-md">
                            <div class="flex items-center gap-2">
                                <button onclick="window.navigateTo('dashboard')" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-90">
                                    <span class="material-symbols-outlined text-[18px]">arrow_back</span>
                                </button>
                                <h2 class="font-serif text-base font-bold tracking-wide">80mm Thermal Tag</h2>
                            </div>
                        </header>
                        <div class="p-8 text-center space-y-3 my-6">
                            <div class="w-14 h-14 rounded-2xl bg-surface-container flex items-center justify-center mx-auto text-outline">
                                <span class="material-symbols-outlined text-[32px]">receipt_long</span>
                            </div>
                            <h3 class="font-serif text-base font-bold text-primary">No Slips Ready to Print</h3>
                            <p class="text-xs text-on-surface-variant">Create an order intake first to generate 80mm QR thermal tags.</p>
                            <button onclick="window.navigateTo('new-booking')" class="px-5 py-2.5 rounded-xl bg-primary-container text-on-primary font-bold text-xs inline-flex items-center gap-1.5 shadow-md">
                                <span class="material-symbols-outlined text-[16px]">add_circle</span>
                                <span>New Order Intake</span>
                            </button>
                        </div>
                    `;
                    return;
                }
                bookingId = recent[0].id;
            }
            const booking = await api.getBooking(bookingId);
            const garmentIds = booking.garments.map(g => g.id);
            const slipsData = await api.generatePrintSlips(garmentIds, '80mm');
            const slip = slipsData.slips[0] || {};

            container.innerHTML = `
                <header class="sticky top-0 z-30 bg-primary-container text-on-primary px-3 py-2.5 flex items-center justify-between shadow-md">
                    <div class="flex items-center gap-2">
                        <button onclick="window.navigateTo('dashboard')" class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-90">
                            <span class="material-symbols-outlined text-[18px]">arrow_back</span>
                        </button>
                        <h2 class="font-serif text-base font-bold tracking-wide">80mm Thermal Tag</h2>
                    </div>
                    <button id="btn-trigger-print" class="px-3 py-1 rounded-full bg-tertiary-fixed text-on-tertiary-fixed text-xs font-bold flex items-center gap-1 active:scale-95 shadow">
                        <span class="material-symbols-outlined text-[16px]">print</span>
                        <span>Print</span>
                    </button>
                </header>

                <div class="p-3 space-y-3">
                    <!-- Thermal Receipt Paper View (Exact Monospace Stitch Formatting) -->
                    <div class="bg-surface-container-lowest border border-outline-variant/60 rounded-xl p-4 shadow-md font-mono text-[11px] leading-relaxed text-on-surface">
                        <div class="flex flex-col items-center mb-3">
                            <img src="${slip.qr_image_data_uri}" alt="QR Code" class="w-36 h-36 border border-black/10 rounded p-1 mb-2"/>
                            <span class="font-bold text-xs">${slip.qr_code_identifier || ''}</span>
                        </div>
                        <div class="whitespace-pre-wrap font-mono">${slip.thermal_text}</div>
                    </div>
                </div>
            `;

            document.getElementById('btn-trigger-print').onclick = () => {
                const printArea = document.getElementById('print-area');
                printArea.innerHTML = `
                    <div style="font-family: monospace; font-size: 11px; text-align: center;">
                        <img src="${slip.qr_image_data_uri}" style="width: 150px; margin: 0 auto; display: block;"/>
                        <p style="font-weight: bold; margin-top: 5px;">${slip.qr_code_identifier}</p>
                    </div>
                    <pre style="font-family: monospace; font-size: 10px; margin-top: 10px;">${slip.thermal_text}</pre>
                `;
                printArea.classList.remove('hidden');
                window.print();
                printArea.classList.add('hidden');
            };
        } catch (err) {
            container.innerHTML = `<div class="p-6 text-center text-error">${err.message}</div>`;
        }
    }

    // ==========================================
    // SCREEN 11: SETTINGS & ATELIER HARDWARE
    // ==========================================
    renderSettings(container) {
        const user = api.currentUser || { full_name: 'AASHIMA Owner', role: 'Owner' };
        container.innerHTML = `
            <header class="sticky top-0 z-30 bg-primary-container text-on-primary px-3 py-2.5 flex items-center justify-between shadow-md">
                <h2 class="font-serif text-base font-bold tracking-wide">Atelier Preferences</h2>
                <span class="text-[10px] text-tertiary-fixed font-semibold uppercase">v2.4</span>
            </header>

            <div class="p-3 space-y-3">
                <!-- Operator Card -->
                <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm flex items-center justify-between">
                    <div class="flex items-center gap-2.5">
                        <div class="w-10 h-10 rounded-full bg-primary-fixed text-on-primary-fixed flex items-center justify-center font-bold text-sm">
                            ${user.full_name.charAt(0)}
                        </div>
                        <div>
                            <h3 class="text-xs font-bold text-on-surface">${user.full_name}</h3>
                            <span class="px-1.5 py-0.2 rounded bg-tertiary-fixed text-on-tertiary-fixed text-[10px] font-bold">${user.role}</span>
                        </div>
                    </div>
                    <button id="btn-logout" class="px-3 py-1.5 rounded-lg bg-error-container text-on-error-container text-xs font-bold">Sign Out</button>
                </div>

                <!-- Hardware & Thermal Printer -->
                <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-2">
                    <span class="text-xs font-bold text-on-surface-variant uppercase tracking-wider block">Hardware & Printer</span>
                    <div class="flex items-center justify-between py-1 border-b border-outline-variant/30 text-xs">
                        <span>Thermal Format</span>
                        <span class="font-bold text-primary">80mm ESC/POS Roll</span>
                    </div>
                    <div class="flex items-center justify-between py-1 border-b border-outline-variant/30 text-xs">
                        <span>Paired Bluetooth POS</span>
                        <span class="font-mono text-[11px] text-on-surface-variant">Not Paired</span>
                    </div>
                    <div class="flex items-center justify-between py-1 text-xs">
                        <span>Camera Scanner Torch</span>
                        <span class="font-bold text-success">Supported</span>
                    </div>
                </div>

                <!-- Ecosystem Quick Switcher -->
                <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-2">
                    <span class="text-xs font-bold text-on-surface-variant uppercase tracking-wider block">Connected Applications</span>
                    <div class="grid grid-cols-2 gap-2">
                        <a href="/admin/" class="p-2.5 rounded-lg bg-surface-container hover:bg-surface-container-high border border-outline-variant/40 flex items-center gap-2 text-primary font-bold text-xs">
                            <span class="material-symbols-outlined text-[18px]">desktop_windows</span>
                            <span>Admin Portal</span>
                        </a>
                        <a href="/" target="_blank" class="p-2.5 rounded-lg bg-surface-container hover:bg-surface-container-high border border-outline-variant/40 flex items-center gap-2 text-secondary font-bold text-xs">
                            <span class="material-symbols-outlined text-[18px]">public</span>
                            <span>Customer Track</span>
                        </a>
                    </div>
                </div>

                <!-- Shop Profile -->
                <div class="p-3 rounded-xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm space-y-1.5 text-xs">
                    <span class="text-xs font-bold text-on-surface-variant uppercase tracking-wider block">Boutique Registration</span>
                    <p><b>Legal Entity:</b> AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers</p>
                    <p><b>Address:</b> 581, Turab Nagar, Ghaziabad, Uttar Pradesh, 201001, India</p>
                    <p><b>GSTIN:</b> 09AABCA1234F1Z8</p>
                </div>
            </div>
        `;

        document.getElementById('btn-logout').onclick = () => {
            api.clearAuth();
            this.showToast('Signed out of atelier session.');
            this.navigateTo('login');
        };
    }
}

new MobileApp();
