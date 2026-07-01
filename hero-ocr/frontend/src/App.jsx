import { useState, useRef, useEffect } from 'react';
import { Send, Bot, Database, Square, ThumbsUp, ThumbsDown } from 'lucide-react';
import KnowledgeView from './KnowledgeView';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('chat'); // 'chat' or 'knowledge'
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am HeRO, your DTI Region 11 Human Resource Officer. I am here to help you with questions about DTI policies, HR guidelines, and internal memorandums. How can I help you today?' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);
  const [feedbackState, setFeedbackState] = useState({});

  const handleFeedback = (index, type) => {
    if (!feedbackState[index]) {
      setFeedbackState(prev => ({ ...prev, [index]: type }));
    }
  };

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

    // Create an AbortController so we can cancel the fetch
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      console.log("VITE_API_URL resolves to:", import.meta.env.VITE_API_URL);
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userMessage.content }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error('Failed to fetch response');
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { role: 'ai', content: data.answer }]);
    } catch (error) {
      if (error.name === 'AbortError') {
        // User cancelled — the backend will return a partial/cancelled response
        // We just show a simple cancellation message on the frontend
        setMessages((prev) => [...prev, { role: 'ai', content: '⚠️ Generation was cancelled.' }]);
      } else {
        console.error(error);
        setMessages((prev) => [...prev, { role: 'ai', content: 'Sorry, I encountered an error. Please make sure the backend server is running.' }]);
      }
    } finally {
      abortControllerRef.current = null;
      setIsLoading(false);
    }
  };

  const handleCancel = async () => {
    // 1. Abort the frontend fetch
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    // 2. Tell the backend to stop Ollama generation
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      await fetch(`${apiUrl}/api/chat/cancel`, { method: 'POST' });
    } catch {
      // Best-effort — if this fails the abort signal already stopped the frontend
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
            <h1>Project HeRO</h1>
            <p>DTI Region 11 HR Policy Assistant</p>
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
                {msg.role === 'ai' && (
                  <div className="feedback-container">
                    <button 
                      className={`feedback-btn thumbs-up ${feedbackState[index] === 'up' ? 'active-up' : ''}`}
                      onClick={() => handleFeedback(index, 'up')}
                      disabled={!!feedbackState[index]}
                      title="Helpful"
                    >
                      <ThumbsUp size={14} />
                    </button>
                    <button 
                      className={`feedback-btn thumbs-down ${feedbackState[index] === 'down' ? 'active-down' : ''}`}
                      onClick={() => handleFeedback(index, 'down')}
                      disabled={!!feedbackState[index]}
                      title="Not helpful"
                    >
                      <ThumbsDown size={14} />
                    </button>
                    {feedbackState[index] && (
                      <span className="feedback-text">Thank you for your feedback!</span>
                    )}
                  </div>
                )}
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

          <footer className="input-container">
            <form onSubmit={handleSend} className="input-box">
              <input
                type="text"
                className="chat-input"
                placeholder={isLoading ? 'AI is generating...' : 'Ask a question...'}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                disabled={isLoading}
              />
              {isLoading ? (
                <button type="button" className="cancel-button" onClick={handleCancel} title="Cancel generation">
                  <Square size={18} />
                </button>
              ) : (
                <button type="submit" className="send-button" disabled={!inputValue.trim()}>
                  <Send size={20} />
                </button>
              )}
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
