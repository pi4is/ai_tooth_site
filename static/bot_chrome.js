const chatBox = document.querySelector(".chat-box");
const chatBox = document.querySelector(".chrome-box");
const messageInput = document.querySelector("#message-input");
const sendBtn = document.querySelector("#button-addon2");

console.log(sendBtn);
console.log(chatBox);
console.log(messageInput);


function addMessage(message, isUserMessage) {
      const messageDiv = document.createElement("div");
      messageDiv.classList.add("card", "mx-auto", "my-2");
      messageDiv.style.cssText = "width: 550px;";
      if (isUserMessage) {
        messageDiv.classList.add("user-message");

      } else {
        messageDiv.classList.add("bot-message");
      }

      if (isUserMessage) {
      messageDiv.innerHTML = `<div class="card-header">
                                <h5 class="card-title">Ваше сообщение</h5>
                              </div>
                              <div class="card-body">
                                <p class="card-text">${message}</p>
                              </div>`;

      } else {
        messageDiv.innerHTML = `<div class="card-header">
                                    <h5 class="card-title">WhoAm</h5>
                                </div>
                                <div class="card-body text-center">
                                  <div class="spinner-grow spinner-grow-sm" role="status">
                                    <span class="visually-hidden">Загрузка...</span>
                                  </div>

                                  <div class="spinner-border spinner-border-sm" role="status">
                                    <span class="visually-hidden">Загрузка...</span>
                                  </div>

                                  <div class="spinner-grow spinner-grow-sm" role="status">
                                    <span class="visually-hidden">Загрузка...</span>
                                  </div>
                                </div>

        `;
      }

      chatBox.appendChild(messageDiv);
      chatBox.scrollTop = chatBox.scrollHeight;
    }

function sendMessage() {
  const message = messageInput.value.trim();

  if (message !== "") {
    messageInput.value = "";

    addMessage("Wait", false);

    fetch("/api", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message })
    })
      .then(response => response.json())
      .then(data => {
                  messageInput.value = "";
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("card", "mx-auto", "my-2");
        messageDiv.style.cssText = "width: 550px;";

        chatBox.lastElementChild.remove();

        const content = data.content;

        // Check if the content has code block
        const hasCodeBlock = content.includes("```");
        if (hasCodeBlock) {
          // If the content has code block, wrap it in a <pre><code> element
          const codeContent = content.replace(/```([\s\S]+?)```/g, '</p><pre><code>$1</code></pre><p>');


          messageDiv.innerHTML = `<img src="{{ url_for('static', filename='images/gpt.jpg') }}" class="bot-icon"><p>${codeContent}</p>`

        }
        else{
          messageDiv.setAttribute("id","just-line-break");
          messageDiv.innerHTML = `
                              <div class="card-header">
                                <h5 class="card-title">WhoAm</h5>
                              </div>
                              <div class="card-body">
                                <p class="card-text">${content}</p>
                              </div>`
        }
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

      })
      .catch(error => console.error(error));
  }
}

sendBtn.addEventListener("click", sendMessage);
messageInput.addEventListener("keydown", event => {
      if (event.keyCode === 13 && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
});