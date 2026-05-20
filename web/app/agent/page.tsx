'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ChatMessage from '../../components/ChatMessage';
import GrantCard from '../../components/GrantCard';
import { AgentMessage, AgentResponse, sendAgentMessage } from '../../lib/agent-api';
import { Grant } from '../../lib/api';
import styles from './page.module.css';

const PHASE_LABELS: Record<string, string> = {
  gathering: '📝 Gathering Info',
  composing: '✍️ Composing Pitch',
  reviewing: '👀 Review Pitch',
  searching: '🔍 Searching Grants',
  complete: '✅ Complete',
};

const PHASE_STYLES: Record<string, string> = {
  gathering: styles.phaseGathering,
  composing: styles.phaseComposing,
  reviewing: styles.phaseReviewing,
  searching: styles.phaseSearching,
  complete: styles.phaseComplete,
};

export default function AgentPage() {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [phase, setPhase] = useState<string>('gathering');
  const [threadId] = useState(() => uuidv4());
  const [searchResults, setSearchResults] = useState<Grant[]>([]);
  const [error, setError] = useState('');
  const [expandedCardId, setExpandedCardId] = useState<number | null>(null);
  const [initialised, setInitialised] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Scroll to bottom when messages change
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, scrollToBottom]);

  const handleAgentResponse = useCallback((response: AgentResponse, isInit = false) => {
    // Extract only the assistant messages from the response
    const agentMessages = response.messages.filter(m => m.role === 'assistant');

    if (isInit) {
      // On init, show only the last assistant message as the greeting
      const lastAgent = agentMessages[agentMessages.length - 1];
      if (lastAgent) {
        setMessages([lastAgent]);
      }
    } else {
      // Append new assistant messages
      const lastAgent = agentMessages[agentMessages.length - 1];
      if (lastAgent) {
        setMessages(prev => [...prev, lastAgent]);
      }
    }

    setPhase(response.phase);

    if (response.search_results && response.search_results.length > 0) {
      setSearchResults(response.search_results as Grant[]);
    }
  }, []);

  // Initialise conversation — send empty to get the greeting
  useEffect(() => {
    if (initialised) return;

    async function initialiseConversation() {
      setInitialised(true);
      setLoading(true);
      setError('');
      try {
        const response = await sendAgentMessage(
          [{ role: 'user', content: 'Hello' }],
          threadId,
        );
        handleAgentResponse(response, true);
      } catch (err) {
        console.error('Failed to start conversation:', err);
        setError('Failed to connect to the agent. Please try again.');
      } finally {
        setLoading(false);
      }
    }

    initialiseConversation();
  }, [handleAgentResponse, initialised, threadId]);

  async function handleSend() {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMsg: AgentMessage = { role: 'user', content: trimmed };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setError('');
    setLoading(true);

    // Resize input back
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
    }

    try {
      const response = await sendAgentMessage(
        [userMsg],
        threadId,
      );
      handleAgentResponse(response);
    } catch (err) {
      console.error('Agent error:', err);
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleInputChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setInput(e.target.value);
    // Auto-resize
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`;
    }
  }

  return (
    <section className={styles.agentPage}>
      {/* Header */}
      <div className={styles.header}>
        <h1 className={styles.title}>Pitch Assistant</h1>
        <p className={styles.subtitle}>
          I&apos;ll help you craft the perfect pitch for your EU grant search
        </p>
      </div>

      {/* Phase Badge */}
      <div className={`${styles.phaseBadge} ${PHASE_STYLES[phase] || ''}`}>
        {PHASE_LABELS[phase] || phase}
      </div>

      {/* Chat */}
      <div className={styles.chatContainer}>
        <div className={styles.messagesArea}>
          {messages.map((msg, i) => (
            <ChatMessage key={i} role={msg.role} content={msg.content} />
          ))}
          {loading && <ChatMessage role="assistant" content="" isTyping />}
          {error && <div className={styles.errorMessage}>{error}</div>}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        {phase !== 'complete' && (
          <div className={styles.inputArea}>
            <textarea
              ref={inputRef}
              className={styles.chatInput}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Type your response..."
              rows={1}
              disabled={loading}
            />
            <button
              className={styles.sendButton}
              onClick={handleSend}
              disabled={loading || !input.trim()}
              aria-label="Send message"
            >
              <svg className={styles.sendIcon} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
              </svg>
            </button>
          </div>
        )}
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className={styles.resultsSection}>
          <h2 className={styles.resultsTitle}>Matching EU Grants</h2>
          {searchResults.map((grant, i) => (
            <GrantCard
              key={i}
              grant={grant}
              style={{ animationDelay: `${i * 0.1}s` }}
              isExpanded={expandedCardId === i}
              isDimmed={expandedCardId !== null && expandedCardId !== i}
              onClick={(e) => {
                e.stopPropagation();
                setExpandedCardId(expandedCardId !== i ? i : null);
              }}
            />
          ))}
        </div>
      )}
    </section>
  );
}
