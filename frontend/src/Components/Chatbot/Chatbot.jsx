import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import { IoChatbubble } from "react-icons/io5";
import { BiSolidSend } from "react-icons/bi";
import "./Chatbot.css";

const Chatbot = ({ sidebarOpen, setSidebarOpen }) => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]); // [{ type: 'user' | 'bot', text: '' }]
  const [typing, setTyping] = useState(false);
  const messageEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message to chat
    const newMessages = [
      ...messages,
      { type: "user", text: input },
    ];
    setMessages(newMessages);
    setInput("");
    setTyping(true);

    try {
      const res = await axios.post(
        "http://localhost:8000/chat",
        {
          message: input,
        }
      );

      const botReply = res.data.response;
      setMessages((prev) => [
        ...prev,
        { type: "bot", text: botReply },
      ]);
    } catch (err) {
      console.error("Error sending message:", err);
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: "Oops! Something went wrong.",
        },
      ]);
    } finally {
      setTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div
      className={`chatbot-container ${
        sidebarOpen ? "shifted" : ""
      }`}
    >
      <div className="chat-with-document">
        <h2>
          <span className="chat-bubble">
            <IoChatbubble />
          </span>{" "}
          Document{" "}
          <span className="custom-your">Insights</span> with
          a Simple Chat
        </h2>
      </div>

      <div
        className={`chat-messages ${
          messages.length === 0 ? "empty" : ""
        }`}
        ref={chatContainerRef}
      >
        {messages.length === 0 ? (
          <div className="empty-state">
            Looking for help with something?
          </div>
        ) : (
          <>
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`message ${
                  msg.type === "user"
                    ? "user-msg"
                    : "bot-msg"
                }`}
              >
                {msg.text}
              </div>
            ))}
            {typing && (
              <div className="message bot-msg typing-indicator">
                Bot is typing...
              </div>
            )}
            <div ref={messageEndRef} />
          </>
        )}
      </div>

      <div className="input-field">
        <input
          type="text"
          placeholder="Ask a question about your document"
          className="custom-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <div className="send-btn" onClick={handleSend}>
          <BiSolidSend />
        </div>
      </div>
      {sidebarOpen && window.innerWidth <= 500 && (
        <div
          className="overlay"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}
    </div>
  );
};

export default Chatbot;
