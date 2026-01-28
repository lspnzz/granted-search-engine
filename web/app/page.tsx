'use client';

import { useState, Suspense, useEffect, useRef, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import posthog from 'posthog-js';
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
  const [showDividerAnimation, setShowDividerAnimation] = useState(false);

  // Animation Refs
  const titleRef = useRef<HTMLHeadingElement>(null);
  const dividerRef = useRef<HTMLDivElement>(null);
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Expanded Card State
  const [expandedCardId, setExpandedCardId] = useState<number | null>(null);

  // Click Outside Handler
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      // If we have an expanded card, check if the click target is within a card
      if (expandedCardId !== null) {
        const target = event.target as HTMLElement;
        // If click is NOT inside a .card, collapse all
        // We assume the Card component will have a class containing 'card' or similar, 
        // but checking closest is safer if we know the selector. 
        // Alternatively, we can rely on bubble propagation: 
        // If the card itself handles its click, it can stopPropagation if needed, 
        // OR we just check if the click path includes the expanded card.
        // A simple "click anywhere on document resets state" unless stopped is good,
        // but 'GrantCard' click will bubble here. 
        // So we might need to handle this carefully.

        // Simpler approach: 
        // The GrantCard onClick sets the state. 
        // This global listener resets it IF the click didn't originate from an expanded card interactable.
        // Actually, if I click another card, that card's handler fires.
        // If I click empty space, this fires.
        // We can just check `!target.closest('.grant-card-interactive')` if we add that class.

        if (!target.closest('[data-card-id]')) {
          setExpandedCardId(null);
        }
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [expandedCardId]);


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
  useEffect(() => {
    if (query) {
      handleSearch(query);
    }
  }, [query]); // Added query to dependency array to re-run if query changes

  async function handleSearch(pitch: string) {
    if (!pitch.trim()) {
      setGrants([]);
      setSearched(false);
      setExpandedCardId(null); // Reset on clear
      router.push('/', { scroll: false });
      return;
    }

    if (pitch !== query) {
      router.push(`/?q=${encodeURIComponent(pitch)}`, { scroll: false });
    }


    setLoading(true);
    setShowDividerAnimation(false); // Reset divider animation
    setError('');
    setSearched(true);
    setGrants([]);
    setExpandedCardId(null); // Reset on new search

    try {
      const [data] = await Promise.all([
        searchGrants(pitch),
        new Promise((resolve) => setTimeout(resolve, 500)) // Min 0.5s animation duration
      ]);
      setGrants(data.grants);

      // Track successful grant search
      posthog.capture('grant_searched', {
        query: pitch,
        results_count: data.grants.length,
      });
    } catch (err) {
      console.error(err);
      setError('Failed to fetch grants. Please try again.');

      // Track search error
      posthog.capture('search_error', {
        query: pitch,
        error_message: err instanceof Error ? err.message : 'Unknown error',
      });
      posthog.captureException(err);
    } finally {
      setLoading(false);
    }
  }

  const handleLoadingComplete = useCallback(() => {
    // Search loading finished and loop animation finished.
    // Now show the divider animation.
    setShowDividerAnimation(true);
  }, []);

  return (
    <>
      <section className={`${styles.section} ${styles.atf}`} ref={containerRef}>
        <div className={styles.container}>
          <h1 className={styles.pageTitle} ref={titleRef}>
            Write down your project's pitch and find relevant EU grants
          </h1>
        </div>

        <div className={styles.ctaActionsWrapper}>
          <div className={styles.atfMainButtonWrapper}>
            <div className={`${styles.dividerLine} ${showDividerAnimation ? styles.loadingDivider : ''}`} ref={dividerRef}>
              <div className={styles.dividerProgress}></div>
            </div>
            <div className={styles.searchContainer} ref={searchContainerRef}>
              <SearchBar
                initialValue={query || ''}
                onSearch={handleSearch}
                isLoading={loading}
                hasResults={grants.length > 0}
                onLoadingComplete={handleLoadingComplete}
              />
            </div>
          </div>
        </div>

        <div className={styles.resultsSection}>
          {error && <div className={styles.errorBox}>{error}</div>}

          <div className={`${styles.card} ${(grants.length === 0 && !loading) ? styles.hiddenCard : ''}`}>
            {grants.length > 0 && (
              <div className={`${styles.resultsGrid} ${expandedCardId !== null ? styles.hasExpanded : ''}`}>
                {grants.map((grant, i) => (
                  <GrantCard
                    key={i}
                    grant={grant}
                    style={{ animationDelay: `${i * 0.1}s` }}
                    isExpanded={expandedCardId === i}
                    isDimmed={expandedCardId !== null && expandedCardId !== i}
                    onClick={(e) => {
                      // Stop propagation so the document listener doesn't immediately close it
                      // if we are clicking TO open.
                      // Actually, React events propagate to document listeners.
                      // We can use e.stopPropagation() here to prevent the document listener from firing
                      // for THIS click.
                      e.stopPropagation();
                      const isExpanding = expandedCardId !== i;
                      setExpandedCardId(isExpanding ? i : null);

                      // Track grant card expansion
                      if (isExpanding) {
                        posthog.capture('grant_card_expanded', {
                          grant_title: grant.title,
                          grant_id: grant.id,
                          match_score: grant.match_score,
                          position_in_results: i,
                        });
                      }
                    }}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </section>


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
