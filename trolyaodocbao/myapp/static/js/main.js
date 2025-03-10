$(document).ready(function() {
    const micButton = $('#micButton');
    const statusDiv = $('#status');
    const chatMessages = $('#chat-messages');
    let isListening = false;

    micButton.click(function() {
        if (!isListening) {
            startListening();
        } else {
            stopListening();
        }
    });

    function startListening() {
        isListening = true;
        micButton.css('background', 'red');
        statusDiv.text('Đang lắng nghe...');
        
        $.ajax({
            url: '/start_listening/',
            method: 'POST',
            success: function(response) {
                if (response.text) {
                    addMessage(response.text, 'user');
                    processUserInput(response.text);
                }
                stopListening();
            },
            error: function() {
                statusDiv.text('Có lỗi xảy ra');
                stopListening();
            }
        });
    }

    function stopListening() {
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
                if (response.response) {
                    addMessage(response.response, 'bot');
                }
            }
        });
    }

    function addMessage(text, sender) {
        const messageDiv = $('<div>')
            .addClass('message')
            .addClass(sender + '-message')
            .text(text);
        chatMessages.append(messageDiv);
        chatMessages.scrollTop(chatMessages[0].scrollHeight);
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