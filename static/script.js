var d_lowerValue =null;
var d_upperValue=null;
function sendValues() {

    // Send values to Flask backend using fetch
    fetch('/process_values', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ lowerValue: d_lowerValue, upperValue: d_upperValue })
    })
    .then(response => {
      // reload page when python-flask function has been executed
      location.reload()
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }
  document.addEventListener('DOMContentLoaded', function () {
    var slider = document.getElementById('slider');
    var lowerValue = document.getElementById('lowerValue');
    var upperValue = document.getElementById('upperValue');
    
    // Get the lower and upper values passed from Flask
  // Get the lower and upper values passed from Flask
  /* var lowerValueFromFlask = '{{ lower_value|tojson }}';
  var upperValueFromFlask = "{{ upper_value|tojson }}";
   */
  console.log(lowerValueFromFlask, upperValueFromFlask)
    noUiSlider.create(slider, {
      start: [lowerValueFromFlask, upperValueFromFlask], // Initial values from Flask
      connect: true,
      range: {
        'min': parseFloat(lowerValueFromFlask),
        'max': parseFloat(upperValueFromFlask)
      }
    });
  
    slider.noUiSlider.on('update', function (values) {
      lowerValue.innerHTML = 'Lower Value: ' + values[0];
      upperValue.innerHTML = 'Upper Value: ' + values[1];
      d_lowerValue = values[0]
      d_upperValue = values[1]
      //sendValues(values[0],values[1])
    });
  });

  document.addEventListener('DOMContentLoaded', () => {
    // Get chat icon and chat window elements
    const chatIcon = document.getElementById('chat-icon');
    const chatWindow = document.getElementById('chat-window');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const chatLog = document.getElementById('chat-log'); // Moved outside the event listener to be accessible globally

    // Toggle chat window when chat icon is clicked
    chatIcon.addEventListener('click', () => {
        chatWindow.style.display = (chatWindow.style.display === 'none') ? 'block' : 'none';
        
        // Focus on message input when chat window is opened
        if (chatWindow.style.display === 'block') {
            messageInput.focus();
            addMessageToChatLog("I am bartleby the mighty chatbot that will have an answer to every question you ask!", true);
        }
    });
    
    // Function to add message to chat log
    function addMessageToChatLog(message, isBot) {
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('message-container');

        if (isBot) {
            const botIcon = document.createElement('div');
            botIcon.classList.add('chat-bot-icon');
            botIcon.innerHTML = '<img src="http://localhost:5000/robot-icon" alt="Bot Icon">';
            messageContainer.appendChild(botIcon);

            const chatMessage = document.createElement('div');
            chatMessage.classList.add('chat-message', 'blue');
            chatMessage.textContent = message;
            messageContainer.appendChild(chatMessage);
        } else {
            const userMessage = document.createElement('div');
            userMessage.classList.add('user-message');
            userMessage.textContent = message;
            messageContainer.appendChild(userMessage);
        }

        chatLog.appendChild(messageContainer);
    }

    // Function to handle sending messages
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (message !== '') {
            addMessageToChatLog(message, false);
            messageInput.value = ''; // Clear input field after sending message
            
            // Call botchat function and add response to chat log
            const response = await botchat(message);
            if (response !== '') {
                setTimeout(() => {
                    addMessageToChatLog(response, true);
                }, 500); // Delay displaying bot response for a better user experience
            }
        }
    }

    // Send message when send button is clicked
    sendButton.addEventListener('click', sendMessage);

    // Send message when Enter key is pressed
    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
});


async function botchat(message) {
  const OPENROUTER_API_KEY = "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";
  try {
      const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
          method: "POST",
          headers: {
              "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
              "Content-Type": "application/json"
          },
          body: JSON.stringify({
              "model": "mistralai/mistral-7b-instruct:free",
              "messages": [
                  {
                      "role": "system",
                      "content": "You are Bartleby the scrivener from Herman Melville short story 'Bartleby the Scrivener: A Story of Wall Street acting as the refusing assistant. Every prompt you answer with I would prefer not to. Your answer is only one sentence"
                  },
                  {
                      "role": "user",
                      "content": message
                  }
              ]
          })
      });

      if (!response.ok) {
          throw new Error(`Failed to fetch response: ${response.status} ${response.statusText}`);
      }

      const responseData = await response.json();
      console.log("botResponse ", responseData)
      const botResponse = responseData.choices[0].message.content; // Assuming the bot's response is the second message in the array
      console.log("botResponse ", botResponse, responseData)
      return botResponse;
  } catch (error) {
      console.error("Error fetching bot response:", error);
      return "Sorry, I couldn't process your request at the moment. Please try again later.";
  }
}

