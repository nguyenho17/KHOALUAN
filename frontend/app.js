// ==============================================================
// app.js — ChatBot AI Luật Hôn Nhân & Gia Đình (LexRAG++)
// ==============================================================
// Tự động phát hiện API URL: hoạt động cả local lẫn HuggingFace
// ==============================================================

// ── Phát hiện base URL của API tự động ─────────────────────────
// Khi chạy local: http://127.0.0.1:8000
// Khi chạy trên HuggingFace: https://username-spacename.hf.space
// Cả hai đều cùng server → dùng window.location.origin
const API_BASE = window.location.origin;

// DEBUG: Bắt chính xác dòng code nào gây reload
window.addEventListener('beforeunload', function() {
    console.trace('🔴 TRANG BỊ RELOAD - Stack trace:');
});

// Đợi cho đến khi toàn bộ giao diện HTML được tải xong
document.addEventListener("DOMContentLoaded", function() {

    // ========================================================
    // PHẦN 1: LOGIC TRANG ĐĂNG NHẬP (login.html)
    // ========================================================
    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async function(event) {
            event.preventDefault();

            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            const errorMessage = document.getElementById("error-message");

            errorMessage.style.display = "none";

            try {
                const response = await fetch(`${API_BASE}/api/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        TenDangNhap: username,
                        MatKhau: password
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    localStorage.setItem("access_token", data.access_token);
                    localStorage.setItem("user_info", JSON.stringify(data.user_info));
                    localStorage.setItem("user_role", data.user_info.ma_vai_tro);
                    localStorage.setItem("user_fullname", data.user_info.ho_ten);
                    localStorage.setItem("username", data.user_info.ten_dang_nhap);

                    alert("Đăng nhập thành công!");

                    if (Number(data.user_info.ma_vai_tro) === 1) {
                        window.location.href = "admin.html";
                    } else {
                        window.location.href = "chat.html";
                    }
                } else {
                    errorMessage.textContent = data.detail || "Đăng nhập thất bại!";
                    errorMessage.style.display = "block";
                }
            } catch (error) {
                console.error("Lỗi:", error);
                errorMessage.textContent = "Không thể kết nối đến máy chủ Backend!";
                errorMessage.style.display = "block";
            }
        });
    }

    // ========================================================
    // PHẦN 2: LOGIC TRANG CHAT (chat.html)
    // ========================================================
    const chatContainer = document.querySelector("main section.flex-1.overflow-y-auto");
    const chatInput = document.querySelector("textarea");
    const sendButton = document.querySelector("footer button.primary-gradient");

    const displayUsername = document.getElementById("display-username");
    const savedFullName = localStorage.getItem("user_fullname");

    if (displayUsername) {
        displayUsername.textContent = savedFullName || "Người dùng";
    }

    let isSending = false;

    if (chatContainer && chatInput && sendButton) {

        function addUserMessage(message) {
            const msgHTML = `
                <div class="flex gap-5 items-start justify-end mb-10">
                    <div class="bg-secondary-container p-6 rounded-[2rem] rounded-tr-none max-w-[85%] ambient-shadow">
                        <p class="text-[15px] leading-relaxed font-bold text-primary">${message}</p>
                    </div>
                    <div class="w-9 h-9 rounded-full bg-secondary flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
                        <span class="material-symbols-outlined text-white text-sm">person</span>
                    </div>
                </div>
            `;
            chatContainer.insertAdjacentHTML('beforeend', msgHTML);
            scrollToBottom();
        }

        function addAIMessage(answer, citations) {
            let citationsHTML = "";
            if (citations && citations.length > 0) {
                const tags = citations.map(c => {
                    let cleanCitation = c.replace(/(Điều\s*)+/gi, "Điều ");
                    return `<span class="bg-primary/10 text-primary px-2 py-1 rounded text-xs font-bold mr-2 mb-2 inline-block">${cleanCitation}</span>`;
                }).join("");

                citationsHTML = `
                    <div class="mt-4 pt-4 border-t border-on-surface-variant/10">
                        <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-2">Căn cứ pháp lý áp dụng:</p>
                        <div class="flex flex-wrap">${tags}</div>
                    </div>
                `;
            }
            const formattedAnswer = answer.replace(/\n/g, '<br>');
            const msgHTML = `
                <div class="flex gap-5 items-start mb-10">
                    <div class="w-9 h-9 rounded-full bg-primary flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
                        <span class="material-symbols-outlined text-white text-sm" style="font-variation-settings: 'FILL' 1;">shield_person</span>
                    </div>
                    <div class="bg-white p-8 rounded-[2rem] rounded-tl-none ambient-shadow border border-on-surface-variant/5 max-w-[85%]">
                        <div class="text-[15px] text-slate-700 leading-relaxed font-medium">
                            ${formattedAnswer}
                        </div>
                        ${citationsHTML}
                    </div>
                </div>
            `;
            chatContainer.insertAdjacentHTML('beforeend', msgHTML);
            scrollToBottom();
        }

        function showTypingIndicator() {
            const typingHTML = `
                <div id="typing-indicator" class="flex gap-5 items-start mb-10 transition-all">
                    <div class="w-9 h-9 rounded-full bg-primary flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
                        <span class="material-symbols-outlined text-white text-sm" style="font-variation-settings: 'FILL' 1;">shield_person</span>
                    </div>
                    <div class="bg-white px-6 py-4 rounded-[2rem] rounded-tl-none ambient-shadow border border-on-surface-variant/5">
                        <div class="flex space-x-2 justify-center items-center h-5">
                            <div class="w-2 h-2 bg-primary/40 rounded-full animate-bounce" style="animation-delay: 0s"></div>
                            <div class="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                            <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                        </div>
                    </div>
                </div>
            `;
            chatContainer.insertAdjacentHTML('beforeend', typingHTML);
            scrollToBottom();
        }

        function removeTypingIndicator() {
            const indicator = document.getElementById("typing-indicator");
            if (indicator) indicator.remove();
        }

        function scrollToBottom() {
            chatContainer.scrollTo({
                top: chatContainer.scrollHeight + 100,
                behavior: 'smooth'
            });
        }

        async function sendMessage() {
            const question = chatInput.value.trim();
            if (!question || isSending) return;

            try {
                isSending = true;
                sendButton.disabled = true;
                chatInput.disabled = true;

                addUserMessage(question);
                chatInput.value = "";
                showTypingIndicator();

                const token = localStorage.getItem("access_token") || localStorage.getItem("token");

                const response = await fetch(`${API_BASE}/api/chat`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": token ? `Bearer ${token}` : ""
                    },
                    body: JSON.stringify({ question: question })
                });

                if (response.status === 401) {
                    alert("Phiên đăng nhập đã hết hạn hoặc bạn chưa có quyền. Vui lòng đăng nhập lại!");
                    window.location.href = "login.html";
                    return;
                }

                if (!response.ok) throw new Error("Lỗi kết nối tới máy chủ AI");

                const data = await response.json();
                removeTypingIndicator();
                addAIMessage(data.answer, data.citations);

                if (typeof fetchChatHistory === "function") {
                    fetchChatHistory();
                }

            } catch (error) {
                console.error("Lỗi:", error);
                removeTypingIndicator();
                addAIMessage("Xin lỗi, hệ thống đang bận hoặc mất kết nối. Vui lòng thử lại sau.", []);
            } finally {
                isSending = false;
                sendButton.disabled = false;
                chatInput.disabled = false;
                chatInput.focus();
            }
        }

        // BỘ BA KHÓA CHỐNG TẢI LẠI TRANG
        sendButton.addEventListener("click", function(event) {
            event.preventDefault();
            sendMessage();
        });

        const chatForm = sendButton.closest("form");
        if (chatForm) {
            chatForm.addEventListener("submit", function(event) {
                event.preventDefault();
                sendMessage();
            });
        }

        chatInput.addEventListener("keydown", function(event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        });
    }

    // ========================================================
    // PHẦN 3: LOGIC TRANG ĐĂNG KÝ (dangky.html)
    // ========================================================
    const registerForm = document.getElementById("registerForm");

    if (registerForm) {
        registerForm.addEventListener("submit", async function(event) {
            event.preventDefault();

            const hoten = document.getElementById("hoten").value.trim();
            const email = document.getElementById("email").value.trim();
            const phone = document.getElementById("sodienthoai").value.trim();
            const password = document.getElementById("matkhau").value;
            const confirmPassword = document.getElementById("xacnhanmatkhau").value;
            const errorMessage = document.getElementById("register-error-message");

            errorMessage.style.display = "none";

            if (password !== confirmPassword) {
                errorMessage.textContent = "Mật khẩu xác nhận không khớp!";
                errorMessage.style.display = "block";
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/api/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        HoTen: hoten,
                        Email: email,
                        SoDienThoai: phone,
                        MatKhau: password
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    alert("Đăng ký thành công! Vui lòng đăng nhập để tiếp tục.");
                    window.location.href = "login.html";
                } else {
                    errorMessage.textContent = data.detail || "Đăng ký thất bại!";
                    errorMessage.style.display = "block";
                }
            } catch (error) {
                console.error("Lỗi:", error);
                errorMessage.textContent = "Không thể kết nối đến máy chủ Backend!";
                errorMessage.style.display = "block";
            }
        });
    }

    // ========================================================
    // PHẦN 4: LOGIC TRANG QUÊN MẬT KHẨU (quenmatkhau.html)
    // ========================================================
    const forgotPasswordForm = document.getElementById("forgotPasswordForm");

    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener("submit", async function(event) {
            event.preventDefault();

            const email = document.getElementById("email").value.trim();
            const messageBox = document.getElementById("forgot-message");

            messageBox.style.display = "none";
            messageBox.className = "text-sm font-medium text-center p-4 rounded-lg border";

            try {
                const response = await fetch(`${API_BASE}/api/forgot-password`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ Email: email })
                });

                const data = await response.json();

                if (response.ok) {
                    messageBox.innerHTML = `<strong>${data.message}</strong><br>Hệ thống sẽ chuyển về trang đăng nhập sau 3 giây...`;
                    messageBox.classList.add("bg-green-50", "text-green-700", "border-green-200");
                    messageBox.style.display = "block";

                    setTimeout(() => {
                        window.location.href = "login.html";
                    }, 3000);
                } else {
                    messageBox.textContent = data.detail || "Có lỗi xảy ra!";
                    messageBox.classList.add("bg-red-50", "text-red-600", "border-red-200");
                    messageBox.style.display = "block";
                }
            } catch (error) {
                console.error("Lỗi:", error);
                messageBox.textContent = "Không thể kết nối đến máy chủ Backend!";
                messageBox.classList.add("bg-red-50", "text-red-600", "border-red-200");
                messageBox.style.display = "block";
            }
        });
    }

    // ========================================================
    // PHẦN 5: LOGIC MENU NGƯỜI DÙNG & HỒ SƠ
    // ========================================================
    const userMenuTrigger = document.getElementById("user-menu-trigger");
    const userDropdown = document.getElementById("user-dropdown");
    const btnLogout = document.getElementById("btn-logout");
    const btnOpenProfile = document.getElementById("btn-open-profile");
    const profileModal = document.getElementById("profile-modal");
    const btnCloseProfile = document.getElementById("btn-close-profile");
    const profileForm = document.getElementById("profileForm");
    const avatarUpload = document.getElementById("avatar-upload");
    const previewAvatar = document.getElementById("preview-avatar");
    const sidebarAvatar = document.getElementById("sidebar-avatar");

    let currentBase64Avatar = null;
    let currentUsername = localStorage.getItem("username");

    if (userMenuTrigger && userDropdown) {
        userMenuTrigger.addEventListener("click", function(e) {
            if (!userDropdown.contains(e.target)) {
                userDropdown.classList.toggle("hidden");
            }
        });

        document.addEventListener("click", function(e) {
            if (!userMenuTrigger.contains(e.target)) {
                userDropdown.classList.add("hidden");
            }
        });
    }

    if (btnLogout) {
        btnLogout.addEventListener("click", function() {
            localStorage.clear();
            window.location.href = "login.html";
        });
    }

    if (btnOpenProfile) {
        btnOpenProfile.addEventListener("click", async function() {
            currentUsername = localStorage.getItem("username");

            if (!currentUsername) {
                alert("Phiên đăng nhập không hợp lệ, vui lòng đăng nhập lại!");
                window.location.href = "login.html";
                return;
            }

            userDropdown.classList.add("hidden");
            profileModal.classList.remove("hidden");
            profileModal.classList.add("flex");

            try {
                const res = await fetch(`${API_BASE}/api/profile/get`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ TenDangNhap: currentUsername })
                });
                const data = await res.json();
                if (res.ok) {
                    const inputHoTen = document.getElementById("profile-hoten");
                    const inputUserName = document.getElementById("profile-username");

                    if (inputHoTen) inputHoTen.value = data.ho_ten;
                    if (inputUserName) inputUserName.value = data.ten_dang_nhap;

                    if (data.avatar) {
                        previewAvatar.src = data.avatar;
                        currentBase64Avatar = data.avatar;
                    } else {
                        previewAvatar.src = `https://ui-avatars.com/api/?name=${data.ho_ten}&background=random`;
                    }
                } else {
                    alert("Không thể tải thông tin hồ sơ: " + (data.detail || ""));
                }
            } catch (error) {
                console.error("Lỗi lấy hồ sơ:", error);
                alert("Không thể tải thông tin hồ sơ!");
            }
        });
    }

    if (btnCloseProfile) {
        btnCloseProfile.addEventListener("click", () => profileModal.classList.add("hidden"));
    }

    if (avatarUpload) {
        avatarUpload.addEventListener("change", function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    previewAvatar.src = event.target.result;
                    currentBase64Avatar = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (profileForm) {
        profileForm.addEventListener("submit", async function(e) {
            e.preventDefault();
            const msgBox = document.getElementById("profile-msg");
            const newHoten = document.getElementById("profile-hoten").value;
            const newUsername = document.getElementById("profile-username").value;

            msgBox.style.display = "none";

            try {
                const res = await fetch(`${API_BASE}/api/profile/update`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        TenDangNhapCu: currentUsername,
                        HoTen: newHoten,
                        TenDangNhapMoi: newUsername,
                        Avatar: currentBase64Avatar
                    })
                });
                const data = await res.json();

                if (res.ok) {
                    msgBox.innerHTML = "Lưu thành công!";
                    msgBox.className = "text-xs text-center font-bold text-green-600 block py-2";

                    localStorage.setItem("user_fullname", newHoten);
                    localStorage.setItem("username", newUsername);

                    if (data.access_token) {
                        localStorage.setItem("access_token", data.access_token);
                    }

                    currentUsername = newUsername;

                    if (document.getElementById("display-username")) {
                        document.getElementById("display-username").textContent = newHoten;
                    }
                    if (currentBase64Avatar && sidebarAvatar) {
                        sidebarAvatar.src = currentBase64Avatar;
                    }

                    setTimeout(() => profileModal.classList.add("hidden"), 1500);
                } else {
                    msgBox.innerHTML = data.detail || "Lỗi cập nhật!";
                    msgBox.className = "text-xs text-center font-bold text-red-600 block py-2";
                }
            } catch (error) {
                msgBox.innerHTML = "Lỗi kết nối máy chủ!";
                msgBox.className = "text-xs text-center font-bold text-red-600 block py-2";
            }
        });
    }

    // ========================================================
    // PHẦN 6: TỰ ĐỘNG TẢI AVATAR KHI KHỞI CHẠY TRANG CHAT
    // ========================================================
    if (currentUsername && sidebarAvatar) {
        fetch(`${API_BASE}/api/profile/get`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ TenDangNhap: currentUsername })
        }).then(res => res.json()).then(data => {
            if (data.avatar) sidebarAvatar.src = data.avatar;
            else sidebarAvatar.src = `https://ui-avatars.com/api/?name=${data.ho_ten}&background=random`;
        }).catch(err => console.log("Lỗi tải avatar ban đầu", err));
    }

    // ========================================================
    // PHẦN 7: LOGIC TẢI VÀ HIỂN THỊ LỊCH SỬ TƯ VẤN
    // ========================================================
    const historyListContainer = document.getElementById("history-list") || document.querySelector(".history-list");
    let cachedHistoryItems = [];

    if (historyListContainer && chatContainer) {

        async function fetchChatHistory() {
            const token = localStorage.getItem("access_token") || localStorage.getItem("token");
            const username = localStorage.getItem("username");
            if (!username) return;

            try {
                const response = await fetch(`${API_BASE}/api/chat/history`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": token ? `Bearer ${token}` : ""
                    },
                    body: JSON.stringify({
                        TenDangNhap: username,
                        username: username,
                        user_id: username
                    })
                });

                if (response.ok) {
                    const historyData = await response.json();
                    const items = Array.isArray(historyData) ? historyData :
                                  (historyData.history || historyData.data || historyData.conversations || historyData.sessions || historyData.results || []);

                    cachedHistoryItems = items;
                    renderHistoryList(items);
                }
            } catch (error) {
                console.error("Lỗi hệ thống khi lấy lịch sử hội thoại:", error);
            }
        }

        function renderHistoryList(items) {
            historyListContainer.innerHTML = "";

            if (!items || items.length === 0) {
                historyListContainer.innerHTML = `
                    <div class="text-center py-6 text-slate-400 text-xs font-medium">
                        <p>Chưa có lịch sử tư vấn</p>
                    </div>`;
                return;
            }

            items.forEach((session, index) => {
                const title = session.tieu_de || session.TieuDe
                           || session.title || session.chat_title
                           || session.summary || session.question || session.CauHoi
                           || `Phiên tư vấn số #${index + 1}`;
                const timeStr = session.thoi_gian || session.ThoiGian || session.created_at || session.timestamp;
                const displayTime = timeStr ? new Date(timeStr).toLocaleDateString('vi-VN') : "Gần đây";
                const id = session.id || session.session_id || session.ma_phien || session.MaPhien || session._id || index;

                const itemHTML = `
                    <div class="history-item flex items-center gap-3 p-3.5 rounded-xl hover:bg-slate-100 cursor-pointer transition-all mb-2 border border-transparent hover:border-slate-200" data-id="${id}" data-index="${index}">
                        <span class="material-symbols-outlined text-slate-400 text-lg flex-shrink-0">chat_bubble</span>
                        <div class="flex-1 overflow-hidden">
                            <p class="text-sm font-semibold text-slate-700 truncate">${title}</p>
                            <p class="text-[11px] text-slate-400 mt-0.5">${displayTime}</p>
                        </div>
                    </div>
                `;
                historyListContainer.insertAdjacentHTML("beforeend", itemHTML);
            });

            const historyElements = historyListContainer.querySelectorAll(".history-item");
            historyElements.forEach(el => {
                el.addEventListener("click", function() {
                    const idx = this.getAttribute("data-index");
                    loadSelectedHistoryDetail(items[idx]);
                });
            });
        }

        function loadSelectedHistoryDetail(chatSession) {
            if (!chatSession) return;
            chatContainer.innerHTML = "";

            const messages = chatSession.messages || chatSession.history || chatSession.detail || (Array.isArray(chatSession) ? chatSession : [chatSession]);

            if (Array.isArray(messages)) {
                messages.forEach(msg => {
                    if (msg.question || msg.role === "user" || msg.is_user === true) {
                        const userText = msg.question || msg.content || msg.message || msg.text;
                        if (userText) {
                            const userHTML = `
                                <div class="flex gap-5 items-start justify-end mb-10">
                                    <div class="bg-secondary-container p-6 rounded-[2rem] rounded-tr-none max-w-[85%] ambient-shadow">
                                        <p class="text-[15px] leading-relaxed font-bold text-primary">${userText}</p>
                                    </div>
                                    <div class="w-9 h-9 rounded-full bg-secondary flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
                                        <span class="material-symbols-outlined text-white text-sm">person</span>
                                    </div>
                                </div>
                            `;
                            chatContainer.insertAdjacentHTML('beforeend', userHTML);
                        }
                    }

                    if (msg.answer || msg.role === "assistant" || msg.role === "ai" || msg.role === "model") {
                        const aiText = msg.answer || msg.content || msg.reply || msg.text;
                        if (aiText) {
                            const citations = msg.citations || msg.sources || [];

                            let citationsHTML = "";
                            if (citations && citations.length > 0) {
                                const tags = citations.map(c => {
                                    let cleanCitation = c.replace(/(Điều\s*)+/gi, "Điều ");
                                    return `<span class="bg-primary/10 text-primary px-2 py-1 rounded text-xs font-bold mr-2 mb-2 inline-block">${cleanCitation}</span>`;
                                }).join("");

                                citationsHTML = `
                                    <div class="mt-4 pt-4 border-t border-on-surface-variant/10">
                                        <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-2">Căn cứ pháp lý áp dụng:</p>
                                        <div class="flex flex-wrap">${tags}</div>
                                    </div>
                                `;
                            }

                            const formattedAnswer = aiText.replace(/\n/g, '<br>');
                            const aiHTML = `
                                <div class="flex gap-5 items-start mb-10">
                                    <div class="w-9 h-9 rounded-full bg-primary flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
                                        <span class="material-symbols-outlined text-white text-sm" style="font-variation-settings: 'FILL' 1;">shield_person</span>
                                    </div>
                                    <div class="bg-white p-8 rounded-[2rem] rounded-tl-none ambient-shadow border border-on-surface-variant/5 max-w-[85%]">
                                        <div class="text-[15px] text-slate-700 leading-relaxed font-medium">
                                            ${formattedAnswer}
                                        </div>
                                        ${citationsHTML}
                                    </div>
                                </div>
                            `;
                            chatContainer.insertAdjacentHTML('beforeend', aiHTML);
                        }
                    }
                });
            }

            chatContainer.scrollTo({
                top: chatContainer.scrollHeight + 100,
                behavior: 'smooth'
            });
        }

        window.fetchChatHistory = fetchChatHistory;

        window.loadChatSession = function(sessionId) {
            const found = cachedHistoryItems.find(item => {
                const id = item.id || item.session_id || item._id;
                return String(id) === String(sessionId);
            });
            if (found) {
                loadSelectedHistoryDetail(found);
            } else {
                console.log("Không tìm thấy dữ liệu trùng khớp với Session ID:", sessionId);
            }
        };

        fetchChatHistory();
    }
});