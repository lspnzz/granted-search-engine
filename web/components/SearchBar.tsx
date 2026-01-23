'use client';

import { useState, KeyboardEvent } from 'react';
import styles from './SearchBar.module.css';

interface SearchBarProps {
  initialValue?: string;
  onSearch: (pitch: string) => void;
  isLoading?: boolean;
}

export default function SearchBar({ initialValue = '', onSearch, isLoading }: SearchBarProps) {
  const [value, setValue] = useState(initialValue);

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch(value);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.inputWrapper}>
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe what you're working on"
          className={styles.input}
          disabled={isLoading}
        />
        <button
          onClick={() => onSearch(value)}
          disabled={isLoading}
          className={styles.searchButton}
        >
          {isLoading ? (
            <div className={styles.spinner} />
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
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
          )}
        </button>
      </div>
    </div>
  );
}
