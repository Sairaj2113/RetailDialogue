import React, { useState } from 'react';
import './styles.css';

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChatbot = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div>
      {/* Chatbot Button (Circle) */}
      <div className="chatbot-button" onClick={toggleChatbot}>
        <span>Chat</span>
      </div>

      {/* Chatbot Iframe */}
      {isOpen && (
        <div className="chatbot-container">
          <iframe
            height="430"
            width="350"
            src="https://bot.dialogflow.com/82b182cd-2491-443c-8ec8-6a5818657521"
            title="Chatbot"
            frameBorder="0"
          ></iframe>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
