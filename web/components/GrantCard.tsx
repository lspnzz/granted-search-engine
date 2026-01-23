import { Grant } from '../lib/api';
import styles from './GrantCard.module.css';
import { CSSProperties } from 'react';


export default function GrantCard({ grant, style }: { grant: Grant; style?: CSSProperties }) {
  const matchPercentage = grant.match_score ? Math.round(grant.match_score * 100) : 0;

  return (
    <div className={styles.card} style={style}>
      {/* VISUAL CARD: White bg, border, shadow */}
      <div className={styles.mainContent}>
        <div className={styles.headerGroup}>
          <h3 className={styles.title}>{grant.title}</h3>
          <p className={styles.description}>
            {grant.description}
          </p>
        </div>

        <div className={styles.footer}>
          <a href={grant.url || '#'} className={styles.sourceLink} target="_blank" rel="noopener noreferrer">
            {/* Link Icon */}
            <span className={styles.icon}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
              </svg>
            </span>
            Source: EU Funding & Tenders Portal
          </a>

          {matchPercentage > 0 && (
            <div className={styles.matchScore}>
              {/* Heart Icon Gauge equivalent */}
              <span className={styles.icon}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                </svg>
              </span>
              {matchPercentage}% Match
            </div>
          )}
        </div>
      </div>

      {/* META ROWS: Plain text below card */}
      <div className={styles.metaList}>
        <div className={styles.metaRow}>
          <div className={styles.metaLabelGroup}>
            <span className={styles.icon}>
              {/* Gauge Icon for Funding */}
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                <path d="M12 8v4"></path>
                <path d="M12 16h.01"></path>
              </svg>
            </span>
            Total available funding
          </div>
          <span className={styles.metaValue}>{grant.amount || 'N/A'}</span>
        </div>

        <div className={styles.metaRow}>
          <div className={styles.metaLabelGroup}>
            <span className={styles.icon}>
              {/* Calendar Icon */}
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
            </span>
            Opening date
          </div>
          <span className={styles.metaValue}>{grant.opening_date || 'N/A'}</span>
        </div>

        <div className={styles.metaRow}>
          <div className={styles.metaLabelGroup}>
            <span className={styles.icon}>
              {/* Calendar Icon with Alert/Clock - using same calendar for consistency unless specified */}
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
                <circle cx="17" cy="17" r="3" fill="var(--white)" stroke="none" />
                <path d="M17 15v2h1" stroke="currentColor" strokeWidth="1.5" />
                <circle cx="17" cy="17" r="3" stroke="currentColor" strokeWidth="1.5" />
              </svg>
            </span>
            Deadline date
          </div>
          <span className={styles.metaValue}>{grant.deadline || 'Ongoing'}</span>
        </div>

        <div className={styles.metaRow}>
          <div className={styles.metaLabelGroup}>
            <span className={styles.icon}>
              {/* Inbox/Tray Icon for Status */}
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline>
                <path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path>
              </svg>
            </span>
            Status
          </div>
          <span className={styles.metaValue}>{grant.status || 'Open for submissions'}</span>
        </div>
      </div>
    </div>
  );
}
