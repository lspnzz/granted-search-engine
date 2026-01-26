'use client';

import { useState, KeyboardEvent, useRef, useEffect } from 'react';
import styles from './SearchBar.module.css';

interface SearchBarProps {
  initialValue?: string;
  onSearch: (pitch: string) => void;
  isLoading?: boolean;
  hasResults?: boolean;
}

export default function SearchBar({ initialValue = '', onSearch, isLoading, hasResults }: SearchBarProps) {
  const [value, setValue] = useState(initialValue);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  };

  useEffect(() => {
    adjustHeight();
  }, [value]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSearch(value);
    }
  };

  return (
    <div className={styles.container}>
      <div className={`${styles.inputWrapper} ${hasResults ? styles.hasResults : ''}`}>
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          onChange={(e) => {
            const newValue = e.target.value;
            setValue(newValue);
            if (newValue.trim() === '') {
              onSearch('');
            }
          }}
          onKeyDown={handleKeyDown}
          placeholder="Describe what you're working on, in depth"
          className={styles.input}
          disabled={isLoading}
        />
        <button
          onClick={() => onSearch(value)}
          disabled={isLoading}
          className={styles.searchButton}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="1rem"
            height="1rem"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.3-4.3" />
          </svg>
        </button>
      </div>
    </div>
  );
}
