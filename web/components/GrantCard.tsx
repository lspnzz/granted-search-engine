import { Grant } from '../lib/api';
import styles from './GrantCard.module.css';

export default function GrantCard({ grant }: { grant: Grant }) {
  const matchPercentage = grant.match_score ? Math.round(grant.match_score * 100) : 0;

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div className={styles.metaRow}>
          <span className={styles.statusBadge}>{grant.status || 'Open'}</span>
          {matchPercentage > 0 && (
            <span className={styles.matchScore}>{matchPercentage}% Match</span>
          )}
        </div>
        <h3 className={styles.title}>{grant.title}</h3>
      </div>

      <div className={styles.body}>
        <p className={styles.description}>
          {grant.description}
        </p>

        <div className={styles.gridMeta}>
          <div className={styles.metaItem}>
            <span className={styles.metaLabel}>Amount</span>
            <span className={styles.metaValue}>{grant.amount || 'N/A'}</span>
          </div>
          <div className={styles.metaItem}>
            <span className={styles.metaLabel}>Deadline</span>
            <span className={styles.metaValue}>{grant.deadline || 'Ongoing'}</span>
          </div>
        </div>
      </div>

      <div className={styles.footer}>
        <a href={grant.url || '#'} target="_blank" rel="noopener noreferrer" className={styles.link}>
          Read more
        </a>
      </div>
    </div>
  );
}
