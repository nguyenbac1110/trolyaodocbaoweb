$(document).ready(function() {
    const micButton = $('#micButton');
    const statusDiv = $('#status');
    const chatMessages = $('#chat-messages');
    let isListening = false;
    let isSpeaking = false;
    let recognition = null;

    console.log("Document ready, initializing microphone functionality");

    // Kiểm tra hỗ trợ nhận dạng giọng nói
    function checkSpeechRecognitionSupport() {
        // Kiểm tra các API nhận dạng giọng nói khác nhau
        if ('webkitSpeechRecognition' in window) {
            return 'webkitSpeechRecognition';
        } else if ('SpeechRecognition' in window) {
            return 'SpeechRecognition';
        } else {
            return null;
        }
    }

    // Khởi tạo nhận dạng giọng nói
    function initSpeechRecognition() {
        console.log("Initializing speech recognition...");
        
        const recognitionAPI = checkSpeechRecognitionSupport();
        
        if (recognitionAPI) {
            console.log(`Using ${recognitionAPI} API`);
            
            if (recognitionAPI === 'webkitSpeechRecognition') {
                recognition = new webkitSpeechRecognition();
            } else {
                recognition = new SpeechRecognition();
            }
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'vi-VN';

            recognition.onstart = function() {
                console.log("Speech recognition started");
                isListening = true;
                micButton.removeClass('speaking').addClass('listening');
                micButton.find('i').removeClass('fa-microphone fa-volume-up').addClass('fa-microphone-slash');
                statusDiv.text('Đang lắng nghe...');
            };

            recognition.onend = function() {
                console.log("Speech recognition ended");
                stopListening();
            };

            recognition.onresult = function(event) {
                console.log("Speech recognition result received");
                const text = event.results[0][0].transcript;
                console.log("Recognized text:", text);
                processUserInput(text);
            };

            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                statusDiv.text('Có lỗi xảy ra: ' + event.error);
                stopListening();
                
                // Handle permission errors
                if (event.error === 'not-allowed') {
                    statusDiv.text('Vui lòng cấp quyền truy cập microphone');
                    alert("Vui lòng cấp quyền truy cập microphone cho trang web này để sử dụng tính năng nhận dạng giọng nói.");
                }
            };
            
            return true;
        } else {
            console.error("Speech recognition not supported");
            micButton.prop('disabled', true);
            statusDiv.text('Trình duyệt không hỗ trợ nhận dạng giọng nói');
            return false;
        }
    }
    
    // Khởi tạo nhận dạng giọng nói khi trang tải
    initSpeechRecognition();
    
    // Hiển thị thông báo về trạng thái của nút microphone khi tải trang
    if (recognition) {
        console.log("Microphone button ready");
        statusDiv.text('Nhấn vào nút micro để nói');
        setTimeout(() => statusDiv.text(''), 3000);
    }

    // Xử lý sự kiện click nút microphone
    micButton.on('click', function() {
        console.log("Microphone button clicked, isSpeaking=", isSpeaking, ", isListening=", isListening);
        
        if (isSpeaking) {
            // Nếu đang nói, dừng nói và chuyển nút về trạng thái bình thường
            console.log("Stopping speaking");
            stopSpeaking();
            return;
        }
        
        if (!recognition) {
            console.log("Reinitializing speech recognition");
            if (!initSpeechRecognition()) {
                statusDiv.text('Không thể khởi tạo nhận dạng giọng nói');
                setTimeout(() => statusDiv.text(''), 3000);
                return;
            }
        }
        
        if (!isListening) {
            // Bắt đầu lắng nghe
            console.log("Starting speech recognition");
            try {
                recognition.start();
            } catch (e) {
                console.error("Error starting speech recognition:", e);
                
                // Nếu đã có phiên đang chạy, khởi tạo lại
                if (e.message.includes('already started')) {
                    recognition.stop();
                    setTimeout(() => {
                        recognition.start();
                    }, 100);
                } else {
                    statusDiv.text('Lỗi khởi động: ' + e.message);
                    setTimeout(() => statusDiv.text(''), 3000);
                }
            }
        } else {
            // Dừng lắng nghe
            console.log("Stopping speech recognition");
            stopListening();
        }
    });

    function stopListening() {
        console.log("stopListening called");
        if (recognition) {
            try {
                recognition.stop();
            } catch (e) {
                console.error("Error stopping recognition:", e);
            }
        }
        isListening = false;
        micButton.removeClass('listening');
        micButton.find('i').removeClass('fa-microphone-slash').addClass('fa-microphone');
        statusDiv.text('');
    }

    // Kiểm tra và yêu cầu quyền truy cập microphone
    function requestMicrophonePermission() {
        console.log("Requesting microphone permission");
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(function(stream) {
                    console.log("Microphone permission granted");
                    // Dừng stream ngay khi được cấp quyền
                    stream.getTracks().forEach(track => track.stop());
                    // Cập nhật UI
                    micButton.prop('disabled', false);
                    statusDiv.text('Đã cấp quyền microphone');
                    setTimeout(() => statusDiv.text(''), 2000);
                })
                .catch(function(err) {
                    console.error("Error getting microphone permission:", err);
                    micButton.prop('disabled', true);
                    statusDiv.text('Vui lòng cấp quyền truy cập microphone');
                });
        } else {
            console.error("getUserMedia not supported");
            statusDiv.text('Trình duyệt không hỗ trợ truy cập microphone');
        }
    }
    
    // Yêu cầu quyền truy cập microphone khi trang tải
    requestMicrophonePermission();

    // Hàm đọc văn bản bằng giọng nói sử dụng ResponsiveVoice
    function speakText(text) {
        // Dừng giọng nói trước đó nếu có
        stopSpeaking();
        
        if (text && text.trim() !== '') {
            console.log("Chuẩn bị đọc văn bản:", text.substring(0, 50) + "...");
            
            // Kiểm tra ResponsiveVoice trước khi sử dụng
            if (typeof responsiveVoice === 'undefined') {
                console.error("ResponsiveVoice không khả dụng!");
                return;
            }
            
            // Tiền xử lý văn bản để đọc liên tục
            const processedText = preprocessText(text);
            
            isSpeaking = true;
            micButton.addClass('speaking');
            micButton.find('i').removeClass('fa-microphone fa-microphone-slash').addClass('fa-volume-up');
            statusDiv.text('Đang đọc...');
            
            // Đảm bảo khởi tạo đúng ResponsiveVoice trước khi đọc
            if (typeof responsiveVoice.init === 'function') {
                try {
                    responsiveVoice.init();
                } catch (e) {
                    console.error("Lỗi khởi tạo ResponsiveVoice:", e);
                }
            }
            
            // Đặt priority để đảm bảo đọc liên tục và không bị gián đoạn
            responsiveVoice.speak(processedText, "Vietnamese Female", {
                rate: 1.0,
                pitch: 1.0,
                volume: 1.0,
                priority: 10, // Ưu tiên cao
                linebreak: 1000, // Tạm dừng ngắn giữa các dòng
                onstart: function() {
                    console.log("Bắt đầu đọc văn bản");
                },
                onend: function() {
                    console.log("Kết thúc đọc văn bản");
                    isSpeaking = false;
                    micButton.removeClass('speaking');
                    micButton.find('i').removeClass('fa-volume-up').addClass('fa-microphone');
                    statusDiv.text('');
                },
                onerror: function(error) {
                    console.error("Lỗi đọc văn bản:", error);
                    isSpeaking = false;
                    micButton.removeClass('speaking');
                    micButton.find('i').removeClass('fa-volume-up').addClass('fa-microphone');
                    statusDiv.text('Lỗi đọc văn bản');
                }
            });
        } else {
            console.error("Văn bản trống, không thể đọc");
        }
    }
    
    // Hàm tiền xử lý văn bản để đọc liên tục
    function preprocessText(text) {
        // Thay thế Tiêu đề: bằng dấu chấm để tạo ngắt câu tự nhiên
        let processed = text.replace(/Tiêu đề:/g, '.');

        // Chuẩn hóa khoảng trắng và dấu chấm
        processed = processed.replace(/\s+/g, ' ');
        processed = processed.replace(/\.+/g, '.');
        processed = processed.replace(/\.\s+\./g, '.');
        
        // Loại bỏ ký tự đặc biệt có thể gây ra vấn đề khi đọc
        processed = processed.replace(/[^\p{L}\p{N}\p{P}\s]/gu, '');
        
        // Chèn dấu phẩy giữa các câu dài để tạo nhịp ngắt tự nhiên
        processed = processed.replace(/([^.!?]{40,60})\s/g, '$1, ');
        
        return processed;
    }
    
    // Hàm dừng giọng nói
    function stopSpeaking() {
        if (typeof responsiveVoice !== 'undefined') {
            responsiveVoice.cancel();
            
            // Đảm bảo xóa hàng đợi để tránh lỗi
            if (typeof responsiveVoice.clearQueue === 'function') {
                responsiveVoice.clearQueue();
            }
        }
        
        isSpeaking = false;
        micButton.removeClass('speaking');
        micButton.find('i').removeClass('fa-volume-up').addClass('fa-microphone');
        statusDiv.text('');
    }

    function addMessage(text, sender) {
        const messageDiv = $('<div>')
            .addClass('message')
            .addClass(`${sender}-message`);
        
        if (typeof text === 'string') {
            const p = $('<p>').html(text);
            messageDiv.append(p);
        } else if (Array.isArray(text)) {
            // Nếu là mảng, tạo từng đoạn văn riêng cho mỗi mục
            text.forEach(item => {
                const p = $('<p>').text(item);
                messageDiv.append(p);
            });
        }
        
        $('#chat-messages').append(messageDiv);
        
        // Cuộn xuống tin nhắn mới nhất
        const chatBox = document.getElementById('chatBox');
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function processUserInput(text) {
        $.ajax({
            url: '/process_input/',
            method: 'POST',
            data: {
                'text': text,
                'csrfmiddlewaretoken': getCookie('csrftoken')
            },
            success: function(response) {
                if (response.status === 'success') {
                    addMessage(text, 'user');
                    
                    if (Array.isArray(response.response)) {
                        // Thay đổi: sử dụng hàm addMessage luôn thay vì tự xây dựng message
                        addMessage(response.response, 'bot');
                        
                        // Đọc văn bản nếu có tts_text
                        if (response.tts_text && response.tts_text.trim() !== '') {
                            console.log("TTS text received:", response.tts_text.substring(0, 50) + "...");
                            speakText(response.tts_text);
                        } else {
                            console.warn("No TTS text provided in response");
                        }
                    } else {
                        addMessage(response.response, 'bot');
                        // Đọc văn bản nếu có tts_text
                        if (response.tts_text && response.tts_text.trim() !== '') {
                            console.log("TTS text received:", response.tts_text.substring(0, 50) + "...");
                            speakText(response.tts_text);
                        } else {
                            console.warn("No TTS text provided in response");
                        }
                    }
                } else {
                    addMessage("Có lỗi xảy ra, vui lòng thử lại.", 'bot');
                }
            },
            error: function(xhr, status, error) {
                console.error("Ajax error:", error);
                addMessage("Lỗi kết nối, vui lòng thử lại.", 'bot');
            }
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});