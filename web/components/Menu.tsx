'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import styles from './Menu.module.css';
import { useMenu } from '../context/MenuContext';

export default function Menu() {
  const { menuOpen } = useMenu();
  const menuWrapperRef = useRef<HTMLDivElement>(null);
  const tlMenuReveal = useRef<gsap.core.Timeline | null>(null);

  useEffect(() => {
    // Animation Config
    const clickDuration = 1.5;
    const clickEase = "expo.inOut";

    tlMenuReveal.current = gsap.timeline({ paused: true, defaults: { duration: clickDuration, ease: clickEase } })
      .fromTo(menuWrapperRef.current, { height: 0 }, { height: "auto" }); // "auto" isn't fully supported in all fromTo cases cleanly without some hacks, but GSAP handles it reasonably well usually. 
    // Actually, for "auto" height simple .to from 0 usually works best if we start at 0 css.
    // Reference used: tlMenuReveal.fromTo(menuWrapperRef, { height: 0 }, { height: "auto" });

    return () => {
      tlMenuReveal.current?.kill();
    };
  }, []);

  useEffect(() => {
    if (menuOpen) {
      // Invalidate to ensure "auto" height is recalculated (refreshed) 
      // in case of layout changes (e.g. fonts loading, resizing)
      tlMenuReveal.current?.invalidate().play();
    } else {
      tlMenuReveal.current?.reverse();
    }
  }, [menuOpen]);

  return (
    <div className={styles.menuWrapper} ref={menuWrapperRef}>
      <div className={styles.menu}>
        <div className={styles.container}>
          <div className={styles.menuColumn}>
            <div className={styles.menuContentWrapper}>
              <h3>Did you really think this was a menu? 😏</h3>
              <p>
                <b style={{ color: 'tomato' }}>While we have your attention:</b> Granted is currently in open beta.
                If you care about what it does and would like to support it's development, please reach out to{' '}
                <a href="mailto:takemymoney@grantedsearch.eu?subject=I'd like to pay for a proper product">
                  takemymoney@grantedsearch.eu
                </a>
                . We have big plans for this and we'll need your support. No pressure, but it all depends on <s>your wallet</s> you.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div >
  );
}
