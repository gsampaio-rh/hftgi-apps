const source = new EventSource("/stream");

let currentAudio = null;
let currentProgressId = '';

// Call this function whenever a new message is received
function onNewMessageReceived(message) {
    displayChatBallon(message.id, message.sentiment_analysis, message.conversation);
    displayMessageDetails(message);
    updateTopDepartments(message.department); // Update the departments list
}

// Example usage: This should be inside your EventSource message event listener
source.onmessage = event => {
    const request = JSON.parse(event.data);
    console.log(request.conversation)
    onNewMessageReceived(request);
};

function displayChatBallon(chatID, sentiment, conversation) {
    const sentimentClass = sentiment.includes("Negative") ? 'negative' : 'positive';
    const balloon = $(`<div class="speech-balloon ${sentimentClass}"><p>💬 ${chatID}</p></div>`);
    // balloon.data('conversation', conversation); // Store the conversation in the data attribute

    balloon.on('click', function () {
        // When a balloon is clicked, parse the conversation and display it in a modal
        const conversationHtml = formatConversationAsChat(conversation);
        $('#conversationModalContent').html(conversationHtml);
        $('#conversationModal').modal('show');
    });

    $('#messageStream').prepend(balloon);
}

function formatConversationAsChat(conversationText) {
    const lines = conversationText.trim().split('\n');
    let conversationHtml = '<div class="chat-container">';
    let bubbleColor = true;  // Start with the first color, e.g., green

    lines.forEach(line => {
        if (line) {
            const bubbleClass = bubbleColor ? 'sender' : 'receiver';
            conversationHtml += `<div class="chat-bubble ${bubbleClass}">${line}</div>`;
            bubbleColor = !bubbleColor;  // Toggle color for next bubble
        }
    });

    conversationHtml += '</div>';
    return conversationHtml;
}

function playAudio(audioUrl) {
    const audio = new Audio(audioUrl);
    audio.play().catch(e => console.error('Error playing audio:', e));
}

function displayMessageDetails(message) {

    // Construct the HTML for the message details

    audio_file_url = 'https://samplelib.com/lib/preview/mp3/sample-3s.mp3'
    // audio_file_url = '${ message.audio_file_url }'

    // const speakerIconHtml = `
    //     <i class="fa fa-volume-up" aria-hidden="true" onclick="toggleAudio('${audio_file_url}', 'progress-${message.id}')">🔊</i>
    //     <progress id="progress-${message.id}" value="0" max="100" class="audio-progress"></progress>
    // `;

    const speakerIconHtml = `
        <i class="fa fa-volume-up" aria-hidden="true" onclick="toggleAudio('${audio_file_url}', 'progress-${message.id}')">🔊</i>
    `;

    const detailsHtml = `
    <div class="message-detail-item"><div class="detail-title"><h4>${message.id}</h4>${speakerIconHtml}</div>
    <div class="message-detail-item"><strong>🧑‍💼 Name:</strong> ${message.name}</div>
    <div class="message-detail-item"><strong>📧 Email:</strong> ${message.email}</div>
    <div class="message-detail-item"><strong>📞 Phone Number:</strong> ${message.phone_number}</div>
    <div class="message-detail-item"><strong>🏢 Department:</strong> ${message.department}</div>
    <div class="message-detail-item"><strong>📄 Issue:</strong> ${message.issue}</div>
    <div class="message-detail-item"><strong>🛠 Service:</strong> ${message.service}</div>
    <div class="message-detail-item"><strong>ℹ️ Additional Information:</strong> ${message.additional_information}</div>
    <div class="message-detail-item"><strong>🗒 Detailed Description:</strong> ${message.detailed_description}</div>
    `;

    // Update the message details as before
    $('#messageDetails').html(detailsHtml)
        .addClass(message.sentiment_analysis.includes("Negative") ? 'flash-negative' : 'flash-positive')
        .on('animationend', function () {
            $(this).removeClass('flash-negative flash-positive');
        });

    // Format the JSON string to display it pretty-printed
    const jsonPretty = JSON.stringify(message, null, 4); // Indent with 4 spaces

    // Set the JSON to the code block, wrapped in <pre> and <code> for formatting
    $('#jsonCodeBlock').html(`<pre><code>${jsonPretty}</code></pre>`);
}

// Object to hold department counts
const departmentCounts = {};

function updateTopDepartments(department) {
    // Increase the count for the department or add it if it doesn't exist
    if (departmentCounts[department]) {
        departmentCounts[department]++;
    } else {
        departmentCounts[department] = 1;
    }

    // Sort departments by count
    const sortedDepartments = Object.entries(departmentCounts).sort((a, b) => b[1] - a[1]);

    // Update the list in the DOM
    const departmentListHtml = sortedDepartments.map(([dept, count]) =>
        `<li>${dept}: ${count}</li>`
    ).join('');

    $('#departmentList').html(departmentListHtml);
}

function toggleAudio(audioUrl, progressId) {
    // If an audio is currently playing, pause it and reset the progress bar
    if (currentAudio && currentProgressId !== progressId) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        document.getElementById(currentProgressId).value = 0;
    }

    // Either create a new audio element or use the existing one
    if (!currentAudio || currentProgressId !== progressId) {
        currentAudio = new Audio(audioUrl);
        currentProgressId = progressId;
    }

    // Play or pause the audio
    if (currentAudio.paused) {
        currentAudio.play();
        currentAudio.addEventListener('timeupdate', updateProgress);
    } else {
        currentAudio.pause();
    }

    function updateProgress() {
        const progress = document.getElementById(progressId);
        const value = (currentAudio.currentTime / currentAudio.duration) * 100;
        progress.value = value;
    }
}

// Add listener for when the audio ends to reset the progress bar
currentAudio.addEventListener('ended', function () {
    document.getElementById(currentProgressId).value = 0;
});