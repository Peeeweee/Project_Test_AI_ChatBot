import { useState, useEffect } from 'react';
import { Search, ChevronDown, ChevronRight, FileText, Database } from 'lucide-react';
import './App.css'; // Reuse existing dark theme CSS

function KnowledgeView() {
  const [data, setData] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedDocs, setExpandedDocs] = useState({});

  useEffect(() => {
    const fetchKnowledge = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/knowledge`);
        if (!response.ok) throw new Error('Failed to fetch knowledge base');
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error("Error fetching knowledge base:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchKnowledge();
  }, []);

  const toggleDoc = (docName) => {
    setExpandedDocs(prev => ({
      ...prev,
      [docName]: !prev[docName]
    }));
  };

  // Filter chunks based on search query
  const getFilteredData = () => {
    if (!searchQuery) return data;
    
    const query = searchQuery.toLowerCase();
    const filtered = {};
    
    Object.keys(data).forEach(docName => {
      // Strictly filter chunks that contain the text
      const matchingChunks = data[docName].filter(chunk => 
        chunk.toLowerCase().includes(query)
      );
      
      // Only show the document if it has chunks that actually contain the searched word
      if (matchingChunks.length > 0) {
        filtered[docName] = matchingChunks;
      }
    });
    
    return filtered;
  };

  // Helper function to highlight search keywords
  const highlightText = (text, highlight) => {
    if (!highlight.trim()) return text;
    
    // Split text on keyword match (case-insensitive)
    const regex = new RegExp(`(${highlight})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, i) => 
      regex.test(part) ? (
        <mark key={i} style={{ backgroundColor: 'var(--ai-bubble-start)', color: 'white', borderRadius: '4px', padding: '0 2px', fontWeight: 'bold' }}>
          {part}
        </mark>
      ) : (
        <span key={i}>{part}</span>
      )
    );
  };

  const filteredData = getFilteredData();
  const totalDocuments = Object.keys(filteredData).length;
  const totalChunks = Object.values(filteredData).reduce((sum, chunks) => sum + chunks.length, 0);

  return (
    <div className="knowledge-container">
      <div className="input-container" style={{ borderBottom: '1px solid var(--panel-border)', borderTop: 'none' }}>
        <div className="input-box">
          <Search size={20} style={{ color: 'var(--text-secondary)' }} />
          <input
            type="text"
            className="chat-input"
            placeholder="Search chunks by keyword..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        
        {!isLoading && (
          <div style={{ marginTop: '16px', color: 'var(--text-secondary)', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={16} />
            <span>Found {totalChunks} chunks across {totalDocuments} documents.</span>
          </div>
        )}
      </div>

      <div className="chat-container" style={{ padding: '24px' }}>
        {isLoading ? (
          <div className="message-wrapper ai" style={{ alignSelf: 'center', marginTop: '40px' }}>
            <div className="message-bubble" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div className="typing-dot" style={{ animationDelay: '0s' }}></div>
              <div className="typing-dot" style={{ animationDelay: '0.2s' }}></div>
              <div className="typing-dot" style={{ animationDelay: '0.4s' }}></div>
              <span style={{ marginLeft: '8px' }}>Loading vector database...</span>
            </div>
          </div>
        ) : totalDocuments === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '40px' }}>
            <p>No chunks found matching your search.</p>
          </div>
        ) : (
          Object.keys(filteredData).sort().map(docName => (
            <div key={docName} className="doc-group">
              <button 
                className="doc-header"
                onClick={() => toggleDoc(docName)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {expandedDocs[docName] ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                  <FileText size={20} style={{ color: 'var(--ai-bubble-start)' }} />
                  <span style={{ fontWeight: '500' }}>{docName}</span>
                </div>
                <span className="chunk-count">{filteredData[docName].length} chunks</span>
              </button>
              
              {expandedDocs[docName] && (
                <div className="doc-chunks">
                  {filteredData[docName].map((chunk, index) => (
                    <div key={index} className="message-wrapper ai" style={{ maxWidth: '100%', marginBottom: '16px' }}>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px', marginLeft: '8px' }}>
                        Chunk {index + 1}
                      </div>
                      <div className="message-bubble chunk-bubble">
                        {highlightText(chunk.trim(), searchQuery)}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default KnowledgeView;
