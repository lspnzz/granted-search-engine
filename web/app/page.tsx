'use client';

import { useState, Suspense, useEffect, useRef } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import SearchBar from '../components/SearchBar';
import GrantCard from '../components/GrantCard';
import { Grant, searchGrants } from '../lib/api';
import styles from './page.module.css';
import gsap from 'gsap';

function SearchResults() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const query = searchParams.get('q');

  const [grants, setGrants] = useState<Grant[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState('');

  // Animation Refs
  const titleRef = useRef<HTMLHeadingElement>(null);
  const dividerRef = useRef<HTMLDivElement>(null);
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Page Load Animation
  useEffect(() => {
    // Only run on initial mount (roughly equivalent to page load logic)
    const tl = gsap.timeline({ defaults: { duration: 1.5, ease: "power4.in" } });

    // Split text logic simulated via blur/opacity since we don't have SplitText plugin
    // To match reference exactly we'd need SplitText, but we can do a decent approximation

    tl.fromTo(titleRef.current,
      { opacity: 0, filter: "blur(10px)", y: 20 },
      { opacity: 1, filter: "blur(0px)", y: 0, duration: 1.5 }
    )
      .fromTo(dividerRef.current,
        { width: "0%" },
        { width: "50%", duration: 1.5 }, // Matching the 50% width rule for ATF divider
        "<"
      )
      .fromTo(searchContainerRef.current,
        { opacity: 0, y: 50, filter: "blur(5px)" },
        { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.5, ease: "power4.inOut" },
        "<"
      );

  }, []);

  // Effect to handle URL query changes
  useState(() => {
    if (query) {
      handleSearch(query);
    }
  });

  async function handleSearch(pitch: string) {
    if (!pitch.trim()) return;

    if (pitch !== query) {
      router.push(`/?q=${encodeURIComponent(pitch)}`, { scroll: false });
    }

    setLoading(true);
    setError('');
    setSearched(true);

    try {
      const data = await searchGrants(pitch);
      setGrants(data.grants);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch grants. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <section className={`${styles.section} ${styles.atf}`} ref={containerRef}>
        <div className={styles.container}>
          <h1 className={styles.pageTitle} ref={titleRef}>
            we design and develop beautiful software
          </h1>
        </div>

        <div className={styles.ctaActionsWrapper}>
          <div className={styles.atfMainButtonWrapper}>
            <div className={styles.dividerLine} ref={dividerRef}></div>
            <div className={styles.searchContainer} ref={searchContainerRef}>
              <SearchBar
                initialValue={query || ''}
                onSearch={handleSearch}
                isLoading={loading}
              />
            </div>
          </div>
        </div>

        <div className={styles.resultsSection}>
          {error && <div className={styles.errorBox}>{error}</div>}

          <div className={styles.card}>
            {searched ? (
              <div className={styles.resultsGrid}>
                {grants.map((grant, i) => (
                  <GrantCard key={i} grant={grant} />
                ))}
                {grants.length === 0 && !loading && (
                  <div className={styles.emptyState}>
                    No results found. Try a different query.
                  </div>
                )}
              </div>
            ) : (
              <div className={styles.emptyState}>
                <h3>Ready to search?</h3>
              </div>
            )}
          </div>
        </div>
      </section>

      <div className={`${styles.ultraWideText} ${styles.isLeft}`}>
        <p><strong>Wow this is a very wide screen...</strong></p>
      </div>
      <div className={`${styles.ultraWideText} ${styles.isRight}`}>
        <p><strong>Sometimes I really wonder why...</strong></p>
      </div>
    </>
  );
}

export default function Home() {
  return (
    <main>
      <Suspense fallback={<div>Loading...</div>}>
        <SearchResults />
      </Suspense>
    </main>
  );
}
