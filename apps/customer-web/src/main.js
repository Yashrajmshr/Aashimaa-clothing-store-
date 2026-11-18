/**
 * AASHIMA Customer Live Tracking Portal Controller
 * Visual Reference: Google Stitch garment_order_live_tracking_aashima_public_portal
 */

const API_BASE = window.location.origin + '/api/v1';

class CustomerPortal {
    constructor() {
        this.currentOrder = null;
        this.customerToken = localStorage.getItem('aashima_cust_token') || null;
        this.init();
    }

    async init() {
        window.customerPortal = this;
        const urlParams = new URLSearchParams(window.location.search);
        const tokenParam = urlParams.get('token');
        const bookingParam = urlParams.get('booking');

        if (tokenParam) {
            await this.loadOrderTracking(tokenParam, null);
        } else if (bookingParam) {
            await this.loadOrderTracking(null, bookingParam);
        } else {
            // Clean initial state: prompt customer to enter their genuine booking ID and phone
            this.renderLookupForm(document.getElementById('customer-main'));
        }
    }

    async loadOrderTracking(token, bookingNumber, phone = null) {
        const main = document.getElementById('customer-main');
        main.innerHTML = `
            <div class="flex flex-col items-center justify-center p-12 text-center">
                <div class="w-10 h-10 rounded-full border-4 border-primary-container border-t-transparent animate-spin mb-3"></div>
                <p class="text-xs font-bold text-primary">Fetching Atelier Tracking Dossier...</p>
            </div>
        `;

        try {
            const params = new URLSearchParams();
            if (token) params.append('token', token);
            if (bookingNumber) params.append('booking_number', bookingNumber);
            if (phone) params.append('phone', phone);

            const res = await fetch(`${API_BASE}/public/track?${params.toString()}`);
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || 'Order tracking not found.');
            }

            this.currentOrder = await res.json();
            this.renderTrackingView(main, this.currentOrder);
        } catch (err) {
            this.renderLookupForm(main, err.message, bookingNumber, phone);
        }
    }

    renderLookupForm(container, errorMsg = '', defaultBooking = '', defaultPhone = '') {
        container.innerHTML = `
            <div class="p-6 sm:p-8 rounded-2xl bg-surface-container-lowest border border-outline-variant/40 shadow-md space-y-4 max-w-md mx-auto my-8">
                <div class="text-center">
                    <span class="material-symbols-outlined text-[36px] text-primary">manage_search</span>
                    <h2 class="font-serif text-2xl font-bold text-primary mt-1">Track Your Garment</h2>
                    <p class="text-xs text-on-surface-variant">Enter your booking details or scan the unique garment QR tag</p>
                </div>

                ${errorMsg ? `<div class="p-3 rounded-lg bg-error-container text-on-error-container text-xs font-semibold text-center">${errorMsg}</div>` : ''}

                <div class="space-y-3">
                    <div>
                        <div class="flex items-center justify-between mb-1">
                            <label class="text-xs font-bold text-on-surface-variant">Booking Number</label>
                            <span class="text-[10px] text-on-surface-variant font-medium">Optional if entering phone</span>
                        </div>
                        <input type="text" id="track-booking-num" value="${defaultBooking || ''}" placeholder="e.g. ASH-8843 or 8843" class="w-full px-3.5 py-2.5 rounded-lg bg-surface-container-low border border-outline-variant text-sm font-mono font-bold text-primary outline-none focus:border-primary-container"/>
                    </div>

                    <div>
                        <label class="text-xs font-bold text-on-surface-variant block mb-1">Registered Mobile Number</label>
                        <input type="tel" id="track-phone" value="${defaultPhone || ''}" placeholder="Enter 10-digit mobile number" class="w-full px-3.5 py-2.5 rounded-lg bg-surface-container-low border border-outline-variant text-sm font-mono text-on-surface outline-none focus:border-primary-container"/>
                    </div>
                </div>

                <button id="btn-request-otp" class="w-full py-3 rounded-xl bg-primary-container text-on-primary font-bold text-sm shadow-md active:scale-95 transition-transform flex items-center justify-center gap-2">
                    <span>Send Verification OTP</span>
                    <span class="material-symbols-outlined text-[18px]">sms</span>
                </button>
            </div>
        `;

        document.getElementById('btn-request-otp').onclick = async () => {
            const bNum = document.getElementById('track-booking-num').value.trim();
            const rawPhone = document.getElementById('track-phone').value.trim();
            const phone = rawPhone.replace(/\D/g, '').slice(-10);
            if (!phone || phone.length < 10) {
                alert('Please enter a valid 10-digit registered mobile number.');
                return;
            }

            const btn = document.getElementById('btn-request-otp');
            const originalText = btn.innerHTML;
            btn.innerHTML = `<span class="inline-block animate-spin mr-2">⏳</span> Sending...`;
            btn.disabled = true;

            try {
                const res = await fetch(`${API_BASE}/auth/customer/send-otp`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone, booking_number: bNum })
                });
                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.detail || 'OTP dispatch failed');
                }
                this.renderOTPModal(container, phone, bNum, data.whatsapp_url, data.sms_delivered, data.message);
            } catch (e) {
                alert(e.message || 'OTP dispatch failed. Please verify your mobile number.');
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        };
    }

    renderOTPModal(container, phone, bookingNumber, whatsappUrl = '', smsDelivered = false, statusMsg = '') {
        const cleanPhone = phone.replace(/\D/g, '').slice(-10);
        const maskedPhone = `+91 ******${cleanPhone.slice(-4)}`;

        container.innerHTML = `
            <div class="p-6 sm:p-8 rounded-2xl bg-surface-container-lowest border border-outline-variant/40 shadow-md space-y-4 max-w-md mx-auto my-8">
                <div class="text-center">
                    <span class="material-symbols-outlined text-[36px] text-secondary">verified_user</span>
                    <h2 class="font-serif text-2xl font-bold text-primary mt-1">Verify Mobile OTP</h2>
                    <p class="text-xs text-on-surface-variant">A 6-digit verification code has been dispatched to <b class="text-on-surface font-mono">${maskedPhone}</b></p>
                </div>

                <!-- Delivery Notification Status -->
                <div class="p-3 rounded-xl ${smsDelivered ? 'bg-emerald-50 border border-emerald-200 text-emerald-800' : 'bg-primary-container/10 border border-primary-container/30 text-primary'} text-xs flex items-center gap-2">
                    <span class="material-symbols-outlined text-sm">${smsDelivered ? 'check_circle' : 'sms'}</span>
                    <span class="flex-1">${statusMsg || (smsDelivered ? 'Live SMS sent via telecom carrier.' : 'Verification code dispatched to your phone.')}</span>
                </div>

                ${whatsappUrl ? `
                    <!-- Direct Instant WhatsApp Delivery Option -->
                    <div class="space-y-1.5">
                        <a href="${whatsappUrl}" target="_blank" rel="noopener noreferrer" class="w-full py-2.5 px-3 rounded-xl bg-[#25D366]/10 hover:bg-[#25D366]/20 border border-[#25D366]/40 text-[#128C7E] font-bold text-xs flex items-center justify-center gap-2 transition-colors">
                            <span class="material-symbols-outlined text-[16px]">chat</span>
                            <span>Receive OTP on WhatsApp</span>
                        </a>
                        <p class="text-[10px] text-center text-on-surface-variant">Instant zero-friction delivery to your WhatsApp</p>
                    </div>
                ` : ''}

                <div>
                    <label class="text-[11px] font-bold text-on-surface-variant block mb-1">Enter 6-Digit Code</label>
                    <input type="text" id="input-otp" value="" placeholder="------" maxlength="6" inputmode="numeric" autocomplete="one-time-code" class="w-full px-4 py-3 rounded-lg bg-surface-container-low border border-outline-variant text-center font-mono text-2xl font-bold tracking-widest text-primary outline-none focus:border-primary-container"/>
                </div>

                <button id="btn-verify-otp" class="w-full py-3 rounded-xl bg-primary-container text-on-primary font-bold text-sm shadow-md active:scale-95 transition-transform flex items-center justify-center gap-2">
                    <span>Verify & Track Garment</span>
                    <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
                </button>

                <div class="flex items-center justify-between text-xs pt-2 border-t border-outline-variant/30">
                    <button id="btn-resend-otp" class="text-secondary font-semibold hover:underline">Resend OTP</button>
                    <button id="btn-change-number" class="text-on-surface-variant hover:text-primary font-semibold">Change Phone</button>
                </div>
            </div>
        `;

        const otpInput = document.getElementById('input-otp');
        if (otpInput) otpInput.focus();

        document.getElementById('btn-verify-otp').onclick = async () => {
            const code = otpInput.value.trim();
            if (code.length < 6) {
                alert('Please enter the full 6-digit OTP code.');
                return;
            }

            const btn = document.getElementById('btn-verify-otp');
            btn.innerHTML = `<span class="inline-block animate-spin mr-2">⏳</span> Verifying...`;
            btn.disabled = true;

            try {
                const res = await fetch(`${API_BASE}/auth/customer/verify-otp`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone, otp: code, booking_number: bookingNumber })
                });
                const authData = await res.json();
                if (!res.ok) {
                    throw new Error(authData.detail || 'Invalid or expired OTP');
                }
                this.customerToken = authData.access_token;
                localStorage.setItem('aashima_cust_token', authData.access_token);
                await this.loadOrderTracking(null, bookingNumber, phone);
            } catch (err) {
                alert(err.message || 'OTP verification failed');
                btn.innerHTML = `<span>Verify & Track Garment</span><span class="material-symbols-outlined text-[18px]">arrow_forward</span>`;
                btn.disabled = false;
            }
        };

        document.getElementById('btn-resend-otp').onclick = () => {
            this.renderLookupForm(container);
            setTimeout(() => {
                const phoneInput = document.getElementById('track-phone');
                if (phoneInput) phoneInput.value = phone;
                const bookInput = document.getElementById('track-booking-num');
                if (bookInput && bookingNumber) bookInput.value = bookingNumber;
                document.getElementById('btn-request-otp')?.click();
            }, 100);
        };

        document.getElementById('btn-change-number').onclick = () => {
            this.renderLookupForm(container);
        };
    }

    renderTrackingView(container, order) {
        container.innerHTML = `
            <div class="space-y-4">
                <!-- Order Summary Header Card -->
                <div class="p-4 sm:p-5 rounded-2xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm space-y-2">
                    <div class="flex items-start justify-between">
                        <div>
                            <span class="px-2.5 py-0.5 rounded-full bg-tertiary-fixed text-on-tertiary-fixed text-[10px] font-bold uppercase tracking-wider inline-flex items-center gap-1">
                                <span class="material-symbols-outlined text-[12px]">workspace_premium</span>
                                ${order.patron_tier}
                            </span>
                            <h2 class="font-serif text-xl sm:text-2xl font-bold text-primary mt-1">${order.primary_garment}</h2>
                            <p class="text-xs text-on-surface-variant font-medium">${order.division} • ${order.customer_unit || 'Turab Nagar'}</p>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] text-on-surface-variant block uppercase font-bold">Booking</span>
                            <span class="font-mono text-sm sm:text-base font-bold text-primary">#${order.booking_number}</span>
                        </div>
                    </div>

                    <div class="pt-2 border-t border-outline-variant/30 flex items-center justify-between text-xs text-on-surface-variant">
                        <span>Expected Ready Date: <b class="text-on-surface">${order.expected_delivery_date}</b></span>
                        <span class="px-2 py-0.5 rounded bg-surface-container font-bold text-primary uppercase text-[10px]">${order.current_status}</span>
                    </div>
                </div>

                <!-- 5-Stage Live Timeline (Exact Stitch Layout with Pulsing Node) -->
                <div class="p-4 sm:p-5 rounded-2xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm space-y-3">
                    <div class="flex items-center justify-between border-b border-outline-variant/30 pb-2">
                        <h3 class="font-serif text-base font-bold text-primary">Artisan Workflow Progress</h3>
                        <span class="text-xs font-semibold text-secondary">${(() => {
                            const activeNode = (order.timeline || []).find(n => n.state === 'Active');
                            if (activeNode) return `Step ${activeNode.stage_number} of ${order.timeline.length} Active`;
                            const completedCount = (order.timeline || []).filter(n => n.state === 'Completed').length;
                            return completedCount === (order.timeline || []).length ? 'All Steps Completed' : `Step ${completedCount + 1} of ${(order.timeline || []).length}`;
                        })()}</span>
                    </div>

                    <div class="relative pl-6 space-y-6 pt-2 before:absolute before:left-2.5 before:top-4 before:bottom-4 before:w-0.5 before:bg-outline-variant/40">
                        ${order.timeline.map(node => {
                            const isCompleted = node.state === 'Completed';
                            const isActive = node.state === 'Active';

                            return `
                                <div class="relative flex items-start gap-3">
                                    <!-- Indicator Node -->
                                    <div class="absolute -left-6 z-10 w-5 h-5 rounded-full flex items-center justify-center text-white ${
                                        isActive ? 'bg-primary shadow-md ring-4 ring-primary-container/20' :
                                        isCompleted ? 'bg-secondary' : 'bg-surface-container-high text-outline'
                                    }">
                                        ${isActive ? '<span class="absolute w-full h-full rounded-full bg-primary-container animate-ping opacity-40"></span>' : ''}
                                        <span class="material-symbols-outlined text-[13px]">${isCompleted ? 'check' : isActive ? 'verified_user' : 'radio_button_unchecked'}</span>
                                    </div>

                                    <!-- Content -->
                                    <div class="flex-1 ${isActive ? 'p-2.5 rounded-lg bg-surface-container-low border border-outline-variant/50 shadow-sm' : ''}">
                                        <div class="flex items-center justify-between">
                                            <span class="text-xs font-bold ${isActive ? 'text-primary' : 'text-on-surface'}">${node.title}</span>
                                            <span class="text-[10px] text-on-surface-variant font-mono">${node.timestamp}</span>
                                        </div>
                                        <p class="text-[11px] text-on-surface-variant mt-0.5">${node.description}</p>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>

                <!-- Intake Photographic Inspection Proof -->
                ${order.intake_photos && order.intake_photos.length > 0 ? `
                    <div class="p-4 sm:p-5 rounded-2xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm space-y-3">
                        <div class="flex items-center justify-between">
                            <div>
                                <span class="text-[10px] uppercase font-bold text-secondary tracking-widest block">Workshop Documentation</span>
                                <h3 class="font-serif text-base font-bold text-primary">Intake Snapshot & Condition Check</h3>
                            </div>
                            <span class="material-symbols-outlined text-secondary text-[22px]">photo_camera</span>
                        </div>

                        <div class="grid grid-cols-2 gap-2.5">
                            ${order.intake_photos.map(p => `
                                <div class="relative h-32 rounded-xl overflow-hidden shadow-sm border border-outline-variant/40">
                                    <img src="${p.photo_url}" alt="Condition check" class="w-full h-full object-cover"/>
                                    <span class="absolute bottom-1.5 left-1.5 bg-black/70 text-white text-[9px] px-2 py-0.5 rounded font-mono">${p.caption}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <!-- Financial Ledger & Download Invoice -->
                <div class="p-4 sm:p-5 rounded-2xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm space-y-3">
                    <h3 class="font-serif text-base font-bold text-primary">Itemized Bill & Settlement</h3>

                    <div class="space-y-1.5 text-xs">
                        <div class="flex justify-between text-on-surface-variant">
                            <span>Order Total (Inclusive of GST):</span>
                            <span class="font-mono font-bold text-on-surface">₹${order.billing.total_amount.toFixed(2)}</span>
                        </div>
                        <div class="flex justify-between text-success">
                            <span>Advance Paid:</span>
                            <span class="font-mono font-bold">₹${order.billing.advance_paid.toFixed(2)}</span>
                        </div>
                        <div class="flex justify-between font-bold text-sm ${order.billing.balance_due > 0 ? 'text-error' : 'text-success'} pt-1.5 border-t border-outline-variant/30">
                            <span>Remaining Balance Due:</span>
                            <span class="font-mono">₹${order.billing.balance_due.toFixed(2)}</span>
                        </div>
                    </div>

                    ${order.billing.invoice_pdf_url ? `
                        <a href="${order.billing.invoice_pdf_url}" target="_blank" class="w-full py-2.5 rounded-xl bg-surface-container hover:bg-surface-container-high text-primary font-bold text-xs flex items-center justify-center gap-1.5 transition-colors border border-outline-variant/40 shadow-sm">
                            <span class="material-symbols-outlined text-[16px]">download</span>
                            <span>Download Official Tax Invoice (PDF)</span>
                        </a>
                    ` : ''}
                </div>

                <!-- Workshop Assistance Buttons -->
                <div class="p-4 rounded-2xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm flex items-center justify-between">
                    <div>
                        <span class="text-xs font-bold text-on-surface block">Need Atelier Assistance?</span>
                        <span class="text-[11px] text-on-surface-variant">Turab Nagar Main Counter</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <a href="tel:+919810244321" class="px-3 py-1.5 rounded-lg bg-surface-container text-primary font-bold text-xs flex items-center gap-1">
                            <span class="material-symbols-outlined text-[14px]">call</span>
                            <span>Call</span>
                        </a>
                        <a href="${order.workshop_contact.whatsapp}" target="_blank" class="px-3 py-1.5 rounded-lg bg-success text-white font-bold text-xs flex items-center gap-1 shadow">
                            <span class="material-symbols-outlined text-[14px]">chat</span>
                            <span>WhatsApp</span>
                        </a>
                    </div>
                </div>
            </div>
        `;
    }
}

new CustomerPortal();
