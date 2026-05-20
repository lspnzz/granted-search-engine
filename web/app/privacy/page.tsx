import type { Metadata } from 'next';
import styles from './privacy.module.css';

export const metadata: Metadata = {
  title: 'Privacy & Cookie Policy | Granted',
  description: "It's just a privacy policy.",
};

export default function PrivacyPolicy() {
  return (
    <div className={styles.mainContainer}>
      <section className={`${styles.section} ${styles.atfSection}`}>
        <h1 className={styles.pageTitle}>
          Privacy &amp; Cookie Policy
        </h1>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeadingWrapper}>
          <h2 className={styles.sectionTitle}>Information we collect</h2>
        </div>
        <div className={styles.divider}></div>

        <p className={styles.subtitle}>Very little.</p>

        <h3 className={styles.subsectionTitle}>Personal information</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>None. Unless you give it to us by getting in touch with us.</p>
        </div>

        <h3 className={styles.subsectionTitle}>Non-personal information</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>
            We use <a href="https://plausible.io/" target="_blank" rel="noopener noreferrer">Plausible Analytics</a> to collect anonymised data about your visit to our website. This includes:
          </p>
          <ul className={styles.list}>
            <li className={styles.listItem}>what pages you visit;</li>
            <li className={styles.listItem}>
              the time you <span className={styles.crossedOut}>waste</span> spend on each page;
            </li>
            <li className={styles.listItem}>which website sent you on our site;</li>
            <li className={styles.listItem}>which device and browser you are using to visit the website.</li>
          </ul>
        </div>

        <h3 className={styles.subsectionTitle}>How we use your information</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>
            We use the non-personal information to find ways to make Granted more useful for you.
          </p>
          <p>
            We use your personal information to reply to your emails.
          </p>
        </div>

        <h3 className={styles.subsectionTitle}>Do we share your information with others?</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>No. Unless...</p>
          <ul className={styles.list}>
            <li className={styles.listItem}>
              <span className={styles.crossedOut}>The police knocks on our door and point a gun at us</span> we&apos;re required by law
            </li>
            <li className={styles.listItem}>
              We need to protect our rights or property, whatever that means.
            </li>
          </ul>
        </div>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeadingWrapper}>
          <h2 className={styles.sectionTitle}>Cookies</h2>
        </div>
        <div className={styles.divider}></div>

        <p className={styles.subtitle}>
          Sweet biscuits having a fairly soft, chewy texture and typically containing pieces of chocolate or fruit.
        </p>

        <h3 className={styles.subsectionTitle}>Essential cookies</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>
            Can&apos;t do much about it. These are needed to keep our app and website online.
          </p>
        </div>

        <h3 className={styles.subsectionTitle}>Analytics cookies</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>
            Again, we use <a href="https://plausible.io/" target="_blank" rel="noopener noreferrer">Plausible Analytics</a>, which does not use cookies to track your activity. It gathers anonymised data without storing any personal information.
          </p>
        </div>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeadingWrapper}>
          <h2 className={styles.sectionTitle}>What else?</h2>
        </div>
        <div className={styles.divider}></div>

        <p className={styles.subtitle}>Nespresso.</p>

        <h3 className={styles.subsectionTitle}>Data security</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>
            We do our best to try not to get your data stolen, but we&apos;re not perfect and you know how the internet works, or not, anyway, you get our point. Also, who knows, one day we might try to help that Nigerian prince after all...
          </p>
        </div>

        <h3 className={styles.subsectionTitle}>Your rights</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>
            You can ask us to access the information we have about you, change it, or delete it.
          </p>
        </div>

        <h3 className={styles.subsectionTitle}>Changes to this policy</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>
            We might change this policy from time to time, you are supposed to come back here and look at those changes... 😏
          </p>
        </div>

        <h3 className={styles.subsectionTitle}>Any questions?</h3>
        <div className={styles.divider}></div>
        <div className={styles.content}>
          <p>
            Write us at <a href="mailto:icareaboutmyprivacy@grantedsearch.eu">icareaboutmyprivacy@grantedsearch.eu</a>
          </p>
        </div>
      </section>

    </div>
  );
}
