// app.js; // DEBUG: Bắt chính xác dòng code nào gây reload
window.addEventListener('beforeunload', function() {
    console.trace('🔴 TRANG BỊ RELOAD - Stack trace:');
    // Hiển thị trong Console tab của DevTools
});

// Đợi cho đến khi toàn bộ giao diện HTML được tải xong
document.addEventListener("DOMContentLoaded", function() {
    
    // ========================================================
    // PHẦN 1: LOGIC TRANG ĐĂNG NHẬP (login.html) - ĐÃ SỬA LỖI TRỐNG USER_INFO
    // ========================================================
    const loginForm = document.getElementById("loginForm");
    
    if (loginForm) {
        loginForm.addEventListener("submit", async function(event) {
            event.preventDefault(); // Ngăn chặn trình duyệt load lại trang

            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            const errorMessage = document.getElementById("error-message");
            
            errorMessage.style.display = "none";

            try {
                // Gọi API backend
                const response = await fetch("http://127.0.0.1:8000/api/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        TenDangNhap: username,
                        MatKhau: password
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // =====================================================================
                    // 🛠️ TRÚNG ĐÍCH: BỔ SUNG LƯU BIẾN USER_INFO DƯỚI DẠNG CHUỖI ĐỂ TRANG ĐỒ ÁN ADMIN ĐỌC ĐƯỢC
                    // =====================================================================
                    localStorage.setItem("access_token", data.access_token);
                    localStorage.setItem("user_info", JSON.stringify(data.user_info));
                    // =====================================================================
                    
                    // Giữ nguyên các cấu hình lưu dữ liệu cũ của bạn để không ảnh hưởng trang chat.html
                    localStorage.setItem("user_role", data.user_info.ma_vai_tro);
                    localStorage.setItem("user_fullname", data.user_info.ho_ten);
                    localStorage.setItem("username", data.user_info.ten_dang_nhap);
                    
                    alert("Đăng nhập thành công!");
                    
                    // Chuyển hướng trang dựa trên vai trò
                    if (Number(data.user_info.ma_vai_tro) === 1) { 
                        window.location.href = "admin.html"; // Trang Admin
                    } else {
                        window.location.href = "chat.html"; // Trang người dùng
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
    // PHẦN 2: LOGIC TRANG CHAT (chat.html) - KHÓA BA LỚP CHỐNG REFRESH
    // ========================================================
    const chatContainer = document.querySelector("main section.flex-1.overflow-y-auto");
    const chatInput = document.querySelector("textarea");
    const sendButton = document.querySelector("footer button.primary-gradient");

    const displayUsername = document.getElementById("display-username");
    const savedFullName = localStorage.getItem("user_fullname");

    if (displayUsername) {
        if (savedFullName) {
            displayUsername.textContent = savedFullName; 
        } else {
            displayUsername.textContent = "Người dùng"; 
        }
    }

    // Biến cờ kiểm soát trạng thái gửi để tránh Race Condition và gửi trùng lặp dữ liệu
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
                    // TỐI ƯU: Gộp các từ "Điều" bị lặp liên tiếp do lỗi dữ liệu thô thành một từ duy nhất
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

        // Xóa hiệu ứng chờ phản hồi
        function removeTypingIndicator() {
            const indicator = document.getElementById("typing-indicator");
            if (indicator) indicator.remove();
        }

        // Tự động cuộn xuống đáy khung chat
        function scrollToBottom() {
            chatContainer.scrollTo({
                top: chatContainer.scrollHeight + 100,
                behavior: 'smooth'
            });
        }

        // Hàm thực hiện gửi dữ liệu lên Backend RAG
        async function sendMessage() {
            const question = chatInput.value.trim();
            if (!question || isSending) return;

            try {
                // Khóa luồng và vô hiệu hóa UI tạm thời
                isSending = true;
                sendButton.disabled = true;
                chatInput.disabled = true;

                addUserMessage(question);
                chatInput.value = "";
                showTypingIndicator();
                
                const token = localStorage.getItem("access_token") || localStorage.getItem("token");

                const response = await fetch("http://127.0.0.1:8000/api/chat", {
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

                // Kích hoạt làm mới danh sách lịch sử sau khi gửi tin nhắn mới
                if (typeof fetchChatHistory === "function") {
                    fetchChatHistory();
                }

            } catch (error) {
                console.error("Lỗi:", error);
                removeTypingIndicator();
                addAIMessage("Xin lỗi, hệ thống đang bận hoặc mất kết nối. Vui lòng thử lại sau.", []);
            } finally {
                // Mở khóa luồng và kích hoạt lại UI, tự động đưa con trỏ vào ô nhập liệu
                isSending = false;
                sendButton.disabled = false;
                chatInput.disabled = false;
                chatInput.focus();
            }
        }

        // 🔥 ĐẶC TRỊ RAG RACE CONDITION: BỘ BA KHÓA CHỐNG TẢI LẠI TRANG
        
        // Lớp khóa 1: Chặn trực tiếp hành vi click chuột trên Button gửi tin
        sendButton.addEventListener("click", function(event) {
            event.preventDefault();
            sendMessage();
        });

        // Lớp khóa 2: Truy vết ngược lên trên để khóa chặn hành vi submit của thẻ <form> bao quanh (nếu có)
        const chatForm = sendButton.closest("form");
        if (chatForm) {
            chatForm.addEventListener("submit", function(event) {
                event.preventDefault();
                sendMessage();
            });
        }

        // Lớp khóa 3: Chặn sự kiện bấm phím Enter trong Textarea để không kích hoạt submit nhầm của form
        chatInput.addEventListener("keydown", function(event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault(); // Ngăn việc xuống dòng bừa bãi và chặn kích hoạt submit ngầm
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
                const response = await fetch("http://127.0.0.1:8000/api/register", {
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
                const response = await fetch("http://127.0.0.1:8000/api/forgot-password", {
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
    // PHẦN 5: LOGIC MENU NGƯỜI DÙNG & HỒ SƠ (TỐI ƯU HÓA)
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
    let currentUsername = localStorage.getItem("username"); // Lấy username đang login

    // 1. Ẩn/Hiện Dropdown cá nhân
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

    // 2. Xử lý Đăng xuất
    if (btnLogout) {
        btnLogout.addEventListener("click", function() {
            localStorage.clear(); 
            window.location.href = "login.html";
        });
    }

    // 3. Mở form Hồ sơ và load dữ liệu từ API bất đồng bộ
    if (btnOpenProfile) {
        btnOpenProfile.addEventListener("click", async function() {
            currentUsername = localStorage.getItem("username");
            
            if (!currentUsername) {
                alert("Phiên đăng nhập không hợp lệ hoặc thiếu dữ liệu, vui lòng đăng nhập lại!");
                window.location.href = "login.html";
                return;
            }

            userDropdown.classList.add("hidden");
            profileModal.classList.remove("hidden");
            profileModal.classList.add("flex");
            
            try {
                const res = await fetch("http://127.0.0.1:8000/api/profile/get", {
                    method: "POST", 
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ TenDangNhap: currentUsername })
                });
                const data = await res.json();
                if (res.ok) {
                    const inputHoTen = document.getElementById("profile-hoten");
                    const inputUserName = document.getElementById("profile-username");
                    
                    if(inputHoTen) inputHoTen.value = data.ho_ten;
                    if(inputUserName) inputUserName.value = data.ten_dang_nhap;

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

    // 4. Xử lý khi chọn ảnh đại diện mới (Chuyển sang định dạng Base64)
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

    // 5. Submit form cập nhật hồ sơ người dùng
    if (profileForm) {
        profileForm.addEventListener("submit", async function(e) {
            e.preventDefault();
            const msgBox = document.getElementById("profile-msg");
            const newHoten = document.getElementById("profile-hoten").value;
            const newUsername = document.getElementById("profile-username").value;

            msgBox.style.display = "none";

            try {
                const res = await fetch("http://127.0.0.1:8000/api/profile/update", {
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
                    
                    // Cập nhật lại dữ liệu bộ nhớ tạm ở Client
                    localStorage.setItem("user_fullname", newHoten);
                    localStorage.setItem("username", newUsername);
                    
                    // Nâng cấp: Lưu token mới nếu backend sinh lại chuỗi JWT theo Username mới
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
    // PHẦN 6: TỰ ĐỘNG TẢI AVATAR BAN ĐẦU KHI KHỞI CHẠY TRANG CHAT
    // ========================================================
    if (currentUsername && sidebarAvatar) {
        fetch("http://127.0.0.1:8000/api/profile/get", {
            method: "POST", 
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ TenDangNhap: currentUsername })
        }).then(res => res.json()).then(data => {
            if (data.avatar) sidebarAvatar.src = data.avatar;
            else sidebarAvatar.src = `https://ui-avatars.com/api/?name=${data.ho_ten}&background=random`;
        }).catch(err => console.log("Lỗi tải avatar ban đầu", err));
    }

    // ========================================================
    // PHẦN 7: LOGIC TẢI VÀ HIỂN THỊ LỊCH SỬ TƯ VẤN (chat.html) - ĐÃ SỬA LỖI ĐỔ DỮ LIỆU
    // ========================================================
    const historyListContainer = document.getElementById("history-list") || document.querySelector(".history-list");
    let cachedHistoryItems = []; // Bộ nhớ đệm lưu trữ danh sách phiên làm việc
    
    if (historyListContainer && chatContainer) {
        
        // Hàm lấy danh sách lịch sử hội thoại từ API Backend
        async function fetchChatHistory() {
            const token = localStorage.getItem("access_token") || localStorage.getItem("token");
            const username = localStorage.getItem("username");
            if (!username) return;

            try {
                // ĐA DẠNG HÓA PAYLOAD BODY phòng trường hợp backend thay đổi key cấu trúc lọc
                const response = await fetch("http://127.0.0.1:8000/api/chat/history", {
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
                    console.log("=== [app.js] DỮ LIỆU LỊCH SỬ CHAT TỪ BACKEND ===", historyData);
                    
                    // SỬA LỖI: Trích xuất mảng một cách an toàn kể cả khi bị bọc bởi Object từ FastAPI
                    const items = Array.isArray(historyData) ? historyData : 
                                  (historyData.history || historyData.data || historyData.conversations || historyData.sessions || historyData.results || []);
                    
                    cachedHistoryItems = items; // Lưu vào cache client để dùng cho việc tải phiên nhanh
                    renderHistoryList(items);
                }
            } catch (error) {
                console.error("Lỗi hệ thống khi lấy lịch sử hội thoại:", error);
            }
        }

        // Hàm render danh sách các cuộc hội thoại cũ lên khu vực Sidebar lịch sử
        function renderHistoryList(items) {
            historyListContainer.innerHTML = ""; 

            if (!items || items.length === 0) {
                historyListContainer.innerHTML = `
                    <div class="text-center py-6 text-slate-400 text-xs font-medium">
                        <p>Chưa có lịch sử tư vấn</p>
                    </div>`;
                return;
            }

            // Duyệt danh sách các phiên tư vấn trong cơ sở dữ liệu gửi về
            items.forEach((session, index) => {
                // ĐÃ SỬA: Đọc thêm field tieu_de và TieuDe (tên field tiếng Việt từ SQLAlchemy)
                const title = session.tieu_de || session.TieuDe 
                           || session.title || session.chat_title 
                           || session.summary || session.question || session.CauHoi
                           || `Phiên tư vấn số #${index + 1}`;
                // ĐÃ SỬA: Đọc thêm thoi_gian và ThoiGian
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

            // Đăng ký sự kiện Click chọn phiên lịch sử để tải lại lên màn hình Chat chính
            const historyElements = historyListContainer.querySelectorAll(".history-item");
            historyElements.forEach(el => {
                el.addEventListener("click", function() {
                    const idx = this.getAttribute("data-index");
                    loadSelectedHistoryDetail(items[idx]);
                });
            });
        }

        // Hàm Rendering bóc tách tin nhắn cũ render lên khung màn hình chat chính
        function loadSelectedHistoryDetail(chatSession) {
            if (!chatSession) return;
            chatContainer.innerHTML = ""; // Xóa sạch nội dung hiển thị hiện tại
            console.log("=== CHI TIẾT PHIÊN LÀM VIỆC ĐƯỢC TẢI ===", chatSession);

            const messages = chatSession.messages || chatSession.history || chatSession.detail || (Array.isArray(chatSession) ? chatSession : [chatSession]);

            if (Array.isArray(messages)) {
                messages.forEach(msg => {
                    // 1. Kết xuất câu hỏi của Người dùng (User Message)
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

                    // 2. Kết xuất câu trả lời kèm căn cứ pháp lý từ AI (AI Message)
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

            // Tự động kéo thanh cuộn xuống cuối sau khi tái dựng hội thoại lịch sử
            chatContainer.scrollTo({
                top: chatContainer.scrollHeight + 100,
                behavior: 'smooth'
            });
        }

        // Tạo cầu nối các hàm toàn cục nhằm kích hoạt tải/chọn lịch sử đồng bộ từ các file HTML ngoại vi ngoài app.js
        window.fetchChatHistory = fetchChatHistory;
        
        window.loadChatSession = function(sessionId) {
            const found = cachedHistoryItems.find(item => {
                const id = item.id || item.session_id || item._id;
                return String(id) === String(sessionId);
            });
            if (found) {
                loadSelectedHistoryDetail(found);
            } else {
                console.log("Không tìm thấy dữ liệu trùng khớp với Session ID trong bộ nhớ tạm:", sessionId);
            }
        };

        // Kích hoạt chạy tự động lấy danh sách lịch sử khi tải giao diện trang chat xong
        fetchChatHistory();
    }
});