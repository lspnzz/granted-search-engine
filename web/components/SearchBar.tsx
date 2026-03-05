
import { useState, KeyboardEvent, useRef, useEffect, useLayoutEffect } from 'react';
import gsap from 'gsap';
import styles from './SearchBar.module.css';

interface SearchBarProps {
  initialValue?: string;
  onSearch: (pitch: string) => void;
  isLoading?: boolean;
  hasResults?: boolean;
  onLoadingComplete?: () => void;
  disabled?: boolean;
}

export default function SearchBar({ initialValue = '', onSearch, isLoading, hasResults, onLoadingComplete, disabled }: SearchBarProps) {
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

  // Animation Logic
  const rectRef = useRef<SVGRectElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const tlRef = useRef<gsap.core.Timeline | null>(null);

  useLayoutEffect(() => {
    if (!rectRef.current) return;

    // Initialize SVG state
    gsap.set(rectRef.current, {
      opacity: 0,
      strokeDasharray: "0 1000", // Hide stroke initially
      strokeDashoffset: 0
    });

  }, []);

  useEffect(() => {
    if (!rectRef.current) return;

    const rect = rectRef.current;

    // We can approximate perimeter or calculate it. 
    // Since we use vector-effect, correct path length calculation is tricky unless we use getTotalLength().
    // We'll force a specific dash array relative to a simplified perimeter calculation or just trial/error visually.
    // Better: use getTotalLength if possible, but rect element supports pathLength attribute in some browsers.
    // Safest is to get total length via JS.
    const length = rect.getTotalLength ? rect.getTotalLength() : 800; // Fallback

    if (isLoading) {
      // Start Loop
      // If a timeline exists and is running, kill it? or let it continue?
      if (tlRef.current) tlRef.current.kill();

      tlRef.current = gsap.timeline({
        repeat: -1,
        onRepeat: () => {
          // Check if we should stop? No, effects handle that.
        }
      });

      // 1. Fade in / Setup
      gsap.set(rect, { opacity: 1, strokeDasharray: `${length * 0.25} ${length}` });

      // 2. Spin
      // We want it to spin around.
      tlRef.current.fromTo(rect,
        { strokeDashoffset: length * 0.25 },
        { strokeDashoffset: -length * 0.75, duration: 1.5, ease: "none" }
      );

    } else {
      // Stop Loading (Finish Loop)
      // If we were loading (tl exists), we want to finish gracefully.
      if (tlRef.current && tlRef.current.isActive()) {
        const currentTl = tlRef.current;

        // We want to stop the infinite repeat.
        currentTl.repeat(0);

        // After it finishes the current cycle:
        currentTl.eventCallback("onComplete", () => {
          // Animate to specific "exit" state if needed, or just call completion.
          // User wants to "attach" to navbar divider.
          // Logic: Maybe we should make the stroke fill up or move to the left?
          // For now, let's just finish the loop and fire callback.

          // Optional: quick fade out or zip to left?
          // Let's just fire callback immediately after loop end.
          if (onLoadingComplete) onLoadingComplete();

          gsap.to(rect, { opacity: 0, duration: 0.2 });
        });
      } else {
        // Did not animate (maybe initial load), ensure hidden
        gsap.set(rect, { opacity: 0 });
      }
    }

    return () => {
      // Cleanup handled by effect dependency change logic mostly, 
      // but good to kill if unmounting.
      // Don't kill on every render if isLoading didn't change? 
      // Re-running this effect when isLoading changes is correct.
    };
  }, [isLoading, onLoadingComplete]);

  return (
    <div className={styles.container} ref={containerRef}>
      <div className={styles.borderOverlay}>
        <svg className={styles.borderSvg}>
          <rect
            ref={rectRef}
            x="0"
            y="0"
            width="100%"
            height="100%"
            className={styles.borderRect}
          />
        </svg>
      </div>
      <div className={`${styles.inputWrapper} ${hasResults ? styles.hasResults : ''} ${isLoading ? styles.loading : ''}`}>
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
          disabled={isLoading || disabled}
        />
        <button
          onClick={() => onSearch(value)}
          disabled={isLoading || disabled}
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
