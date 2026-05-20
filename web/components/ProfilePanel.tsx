'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import styles from './ProfilePanel.module.css';
import type { User } from 'firebase/auth';

function getInitials(user: User): string {
  if (user.displayName) {
    const parts = user.displayName.trim().split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return parts[0].slice(0, 2).toUpperCase();
  }
  return (user.email ?? '').slice(0, 2).toUpperCase();
}

export default function ProfilePanel() {
  const { user, loading, sendEmailLink, signOut, closePanel } = useAuth();
  const [email, setEmail] = useState('');
  const [emailSent, setEmailSent] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        closePanel();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [closePanel]);

  async function handleEmailSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await sendEmailLink(email);
      setEmailSent(true);
    } catch {
      setError('Failed to send sign-in link. Please check your email and try again.');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className={styles.panel}>
      </div>
    );
  }

  if (user) {
    return (
      <div className={styles.panel}>
        <div className={styles.titleWrapper}>
          <div className={styles.avatarSmall}>
            {getInitials(user)}
          </div>
          <div className={styles.titleDivider}></div>
        </div>

        <div className={styles.profileSection}>
          <p className={styles.userEmail}>{user.email}</p>
          <button className={styles.signOutButton} onClick={() => signOut()}>
            Sign Out
          </button>
        </div>
      </div>
    );
  }

  const isEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  return (
    <div className={styles.panel}>
      <div className={styles.titleWrapper}>
        <h2 className={styles.title}>Sign In</h2>
        <div className={styles.titleDivider}></div>
      </div>

      {emailSent ? (
        <p className={styles.successMessage}>Check your email for a sign-in link</p>
      ) : (
        <form onSubmit={handleEmailSubmit} className={styles.form}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={styles.input}
            required
            disabled={submitting}
          />
          <button
            type="submit"
            className={`${styles.submitButton} ${isEmailValid ? styles.active : ''}`}
            disabled={submitting || !isEmailValid}
          >
            {submitting ? '...' : 'Send sign-in link'}
          </button>
        </form>
      )}

      {error && <p className={styles.error}>{error}</p>}
    </div>
  );
}
