import type { Metadata } from 'next';
import styles from './terms.module.css';

export const metadata: Metadata = {
  title: 'Terms of Service | Granted',
  description: "Our Terms of Service.",
};

export default function TermsOfService() {
  return (
    <div className={styles.mainContainer}>
      <section className={`${styles.section} ${styles.atfSection}`}>
        <h1 className={styles.pageTitle}>
          Terms of Service
        </h1>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeadingWrapper}>
          <h2 className={styles.sectionTitle}>Introduction</h2>
        </div>
        <div className={styles.divider}></div>

        <p className={styles.subtitle}>The boring stuff.</p>

        <h3 className={styles.subsectionTitle}>Welcome</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>
            Welcome to Granted. By using our website, you agree to these terms. If you don&apos;t agree, well, that&apos;s awkward.
          </p>
        </div>

        <h3 className={styles.subsectionTitle}>Acceptance of Terms</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>
            By accessing this website, we assume you accept these terms and conditions. Do not continue to use Granted if you do not agree to take all of the terms and conditions stated on this page.
          </p>
        </div>

        <h3 className={styles.subsectionTitle}>License</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>
            Unless otherwise stated, Granted and/or its licensors own the intellectual property rights for all material on Granted. All intellectual property rights are reserved. You may access this from Granted for your own personal use subjected to restrictions set in these terms and conditions.
          </p>
          <p>You must not:</p>
          <ul className={styles.list}>
            <li className={styles.listItem}>Republish material from Granted;</li>
            <li className={styles.listItem}>Sell, rent or sub-license material from Granted;</li>
            <li className={styles.listItem}>Reproduce, duplicate or copy material from Granted;</li>
            <li className={styles.listItem}>Redistribute content from Granted;</li>
          </ul>
        </div>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeadingWrapper}>
          <h2 className={styles.sectionTitle}>Liability</h2>
        </div>
        <div className={styles.divider}></div>

        <p className={styles.subtitle}>It&apos;s not our fault. Usually.</p>

        <div className={styles.content}>
          <p>
            We are not responsible for any content that appears on your Website. You agree to protect and defend us against all claims that is rising on your Website. No link(s) should appear on any Website that may be interpreted as libelous, obscene or criminal, or which infringes, otherwise violates, or advocates the infringement or other violation of, any third party rights.
          </p>
        </div>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeadingWrapper}>
          <h2 className={styles.sectionTitle}>Disclaimer</h2>
        </div>
        <div className={styles.divider}></div>

        <p className={styles.subtitle}>Don&apos;t blame us.</p>

        <div className={styles.content}>
          <p>
            To the maximum extent permitted by applicable law, we exclude all representations, warranties and conditions relating to our website and the use of this website.
          </p>
        </div>
        <h3 className={styles.subsectionTitle}>Modifications</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>
            Granted may revise these terms of service for its website at any time without notice. By using this website you are agreeing to be bound by the then current version of these terms of service.
          </p>
        </div>
      </section>

    </div>
  );
}
