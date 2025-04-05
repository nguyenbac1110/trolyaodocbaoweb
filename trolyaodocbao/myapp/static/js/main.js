$(document).ready(function() {
    const micButton = $('#micButton');
    const statusDiv = $('#status');
    const chatMessages = $('#chat-messages');
    let isListening = false;
    let isSpeaking = false;
    let recognition = null;
    let speechSynthesis = window.speechSynthesis;
    let currentUtterance = null;
    let voices = []; // Lưu trữ danh sách giọng nói

    // Hàm tải danh sách giọng nói
    function loadVoices() {
        voices = speechSynthesis.getVoices();
        console.log("Voices loaded:", voices.length);
        // Log danh sách giọng nói để debug
        if (voices.length > 0) {
            voices.forEach((voice, index) => {
                console.log(`Voice ${index}: ${voice.name} (${voice.lang}) ${voice.default ? '- Default' : ''}`);
            });
        } else {
            console.warn("Không tìm thấy giọng nói nào trong trình duyệt!");
        }
    }

    // Tải giọng nói ngay khi khởi động
    if (speechSynthesis) {
        // Một số trình duyệt đã có sẵn giọng nói
        loadVoices();
        
        // Đăng ký sự kiện cho các trình duyệt cần thời gian để tải giọng nói
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = loadVoices;
        }
    }

    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'vi-VN';

        recognition.onstart = function() {
            isListening = true;
            micButton.removeClass('speaking').addClass('listening');
            micButton.find('i').removeClass('fa-microphone fa-volume-up').addClass('fa-microphone-slash');
            statusDiv.text('Đang lắng nghe...');
        };

        recognition.onend = function() {
            stopListening();
        };

        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            processUserInput(text);
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            statusDiv.text('Có lỗi xảy ra: ' + event.error);
            stopListening();
        };
    } else {
        micButton.prop('disabled', true);
        statusDiv.text('Trình duyệt không hỗ trợ nhận dạng giọng nói');
    }

    micButton.click(function() {
        if (isSpeaking) {
            // Nếu đang nói, dừng nói và chuyển nút về trạng thái bình thường
            stopSpeaking();
            micButton.removeClass('speaking');
            micButton.find('i').removeClass('fa-volume-up').addClass('fa-microphone');
            statusDiv.text('');
            return;
        }
        
        if (!isListening && recognition) {
            // Bắt đầu lắng nghe
            recognition.start();
        } else {
            // Dừng lắng nghe
            stopListening();
        }
    });

    function stopListening() {
        if (recognition) {
            recognition.stop();
        }
        isListening = false;
        micButton.removeClass('listening');
        micButton.find('i').removeClass('fa-microphone-slash').addClass('fa-microphone');
        statusDiv.text('');
    }

    // Hàm đọc văn bản bằng giọng nói
    function speakText(text) {
        // Dừng giọng nói trước đó nếu có
        stopSpeaking();
        
        if (speechSynthesis && text) {
            console.log("Attempting to speak:", text.substring(0, 50) + "...");
            
            // Kiểm tra xem có khả dụng không
            if (!speechSynthesis.speaking && !speechSynthesis.pending) {
                isSpeaking = true;
                micButton.addClass('speaking');
                micButton.find('i').removeClass('fa-microphone fa-microphone-slash').addClass('fa-volume-up');
                statusDiv.text('Đang đọc...');
                
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'vi-VN';
                
                // Tải lại giọng nói để đảm bảo có danh sách mới nhất
                if (voices.length === 0) {
                    loadVoices();
                }
                
                // Tìm giọng tiếng Việt hoặc sử dụng giọng mặc định
                let vietnameseVoice = voices.find(voice => 
                    voice.lang.includes('vi-') || voice.name.toLowerCase().includes('vietnam')
                );
                
                // Nếu không có giọng Việt, sử dụng giọng mặc định
                if (vietnameseVoice) {
                    console.log("Using Vietnamese voice:", vietnameseVoice.name);
                    utterance.voice = vietnameseVoice;
                } else {
                    console.log("No Vietnamese voice found, using default voice");
                }
                
                // Điều chỉnh tốc độ nói nếu cần
                utterance.rate = 1.0; // Tốc độ bình thường
                utterance.pitch = 1.0; // Âm vực bình thường
                utterance.volume = 1.0; // Âm lượng tối đa
                
                utterance.onstart = function() {
                    console.log("Speech started");
                };
                
                utterance.onend = function() {
                    console.log("Speech ended");
                    isSpeaking = false;
                    micButton.removeClass('speaking');
                    micButton.find('i').removeClass('fa-volume-up').addClass('fa-microphone');
                    statusDiv.text('');
                };
                
                utterance.onerror = function(event) {
                    console.error("Speech error:", event.error);
                    isSpeaking = false;
                    micButton.removeClass('speaking');
                    micButton.find('i').removeClass('fa-volume-up').addClass('fa-microphone');
                    statusDiv.text('Lỗi đọc văn bản');
                };
                
                currentUtterance = utterance;
                
                // Workaround cho một số trình duyệt (đặc biệt là Chrome)
                setTimeout(() => {
                    speechSynthesis.speak(utterance);
                }, 100);
            } else {
                console.warn("Speech synthesis is already speaking or pending");
            }
        } else {
            console.error("Speech synthesis not available or text is empty");
        }
    }
    
    // Hàm dừng giọng nói
    function stopSpeaking() {
        if (speechSynthesis) {
            speechSynthesis.cancel();
            currentUtterance = null;
            isSpeaking = false;
            micButton.removeClass('speaking');
            micButton.find('i').removeClass('fa-volume-up').addClass('fa-microphone');
            statusDiv.text('');
        }
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
        $('.chat-box').scrollTop($('.chat-box')[0].scrollHeight);
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