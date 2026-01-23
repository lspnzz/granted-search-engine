'use client';

import styles from './Footer.module.css';

export default function Footer() {
  return (
    <div className={styles.footerWrapper}>
      <footer className={styles.footer}>
        <section className={styles.sectionHeadingSupportingText}>
          <div className="container is-text is-menu-and-footer">
            <div className={styles.footerContentWrapper}>
              <p className={styles.lastParagraph}>© 2026, Studio Quinto.</p>
            </div>
          </div>
        </section>
      </footer>
    </div>
  );
}
