import styles from './ChatMessage.module.css';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  isTyping?: boolean;
}

export default function ChatMessage({ role, content, isTyping }: ChatMessageProps) {
  const isUser = role === 'user';

  if (isTyping) {
    return (
      <div className={`${styles.message} ${styles.agentMessage}`}>
        <span className={styles.role}>Granted Agent</span>
        <div className={`${styles.bubble} ${styles.typing}`}>
          <span className={styles.typingDot}></span>
          <span className={styles.typingDot}></span>
          <span className={styles.typingDot}></span>
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.message} ${isUser ? styles.userMessage : styles.agentMessage}`}>
      <span className={styles.role}>{isUser ? 'You' : 'Granted Agent'}</span>
      <div className={styles.bubble}>{content}</div>
    </div>
  );
}
