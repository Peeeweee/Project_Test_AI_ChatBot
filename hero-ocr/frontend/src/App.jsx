import { useState, useRef, useEffect } from 'react';
import { Send, Bot, Database } from 'lucide-react';
import KnowledgeView from './KnowledgeView';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('chat'); // 'chat' or 'knowledge'
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Welcome to Test AI ChatBot! Ask me anything.' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (currentView === 'chat') {
      scrollToBottom();
    }
  }, [messages, isLoading, currentView]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { role: 'user', content: inputValue.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userMessage.content }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch response');
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { role: 'ai', content: data.answer }]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, { role: 'ai', content: 'Sorry, I encountered an error. Please make sure the backend server is running.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div className="header-icon">
            <Bot size={28} />
          </div>
          <div className="header-text">
            <h1>Test AI ChatBot</h1>
            <p>Your Personal AI Assistant</p>
          </div>
        </div>
        
        {/* Navigation Toggle */}
        <div className="nav-toggle">
          <button 
            className={`nav-btn ${currentView === 'chat' ? 'active' : ''}`}
            onClick={() => setCurrentView('chat')}
          >
            Chat
          </button>
          <button 
            className={`nav-btn ${currentView === 'knowledge' ? 'active' : ''}`}
            onClick={() => setCurrentView('knowledge')}
          >
            <Database size={16} /> Knowledge Base
          </button>
        </div>
      </header>

      {currentView === 'chat' ? (
        <>
          {/* Chat Area */}
          <main className="chat-container">
            {messages.map((msg, index) => (
              <div key={index} className={`message-wrapper ${msg.role}`}>
                <div className="message-bubble">
                  {msg.content}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message-wrapper ai">
                <div className="message-bubble">
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </main>

          {/* Input Area */}
          <footer className="input-container">
            <form onSubmit={handleSend} className="input-box">
              <input
                type="text"
                className="chat-input"
                placeholder="Ask a question..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                disabled={isLoading}
              />
              <button type="submit" className="send-button" disabled={!inputValue.trim() || isLoading}>
                <Send size={20} />
              </button>
            </form>
          </footer>
        </>
      ) : (
        <KnowledgeView />
      )}
    </div>
  );
}

export default App;
