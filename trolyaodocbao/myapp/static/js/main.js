$(document).ready(function() {
    const micButton = $('#micButton');
    const statusDiv = $('#status');
    const chatMessages = $('#chat-messages');
    let isListening = false;
    let recognition;

    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.lang = 'vi-VN'; // Set language to Vietnamese
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = function() {
            isListening = true;
            micButton.css('background', 'red');
            statusDiv.text('Đang lắng nghe...');
        };

        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            processUserInput(text);
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            statusDiv.text('Có lỗi xảy ra, vui lòng thử lại.');
            stopListening();
        };

        recognition.onend = function() {
            stopListening();
        };
    } else {
        console.warn('Speech recognition not supported in this browser.');
        statusDiv.text('Trình duyệt không hỗ trợ nhận diện giọng nói.');
    }

    micButton.click(function() {
        if (!isListening) {
            startListening();
        } else {
            stopListening();
        }
    });

    function startListening() {
        if (recognition) {
            recognition.start();
        }
    }

    function stopListening() {
        if (recognition) {
            recognition.stop();
        }
        isListening = false;
        micButton.css('background', '#007bff');
        statusDiv.text('');
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
                    addMessage(response.response.join('<br>'), 'bot');
                    if (window.speechSynthesis) {
                        const utterance = new SpeechSynthesisUtterance(response.response.join(' '));
                        utterance.lang = 'vi-VN';
                        window.speechSynthesis.speak(utterance);
                    }
                } else {
                    addMessage("Có lỗi xảy ra, vui lòng thử lại.", 'bot');
                }
            },
            error: function(xhr, status, error) {
                addMessage("Lỗi kết nối, vui lòng thử lại.", 'bot');
            }
        });
    }

    function addMessage(text, sender) {
        const messageDiv = $('<div>')
            .addClass('message')
            .addClass(`${sender}-message`);
        
        if (typeof text === 'string') {
            const p = $('<p>').html(text);
            messageDiv.append(p);
        }
        
        $('#chat-messages').append(messageDiv);
        $('.chat-box').scrollTop($('.chat-box')[0].scrollHeight);
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