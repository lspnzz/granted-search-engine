'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import Link from 'next/link';
import posthog from 'posthog-js';
import styles from './Navbar.module.css';

import { useMenu } from '../context/MenuContext';
import AuthButton from './AuthButton';

export default function Navbar() {
  const buttonRef = useRef<HTMLDivElement>(null);
  const topBarRef = useRef<HTMLDivElement>(null);
  const centerBarRef = useRef<HTMLDivElement>(null);
  const bottomBarRef = useRef<HTMLDivElement>(null);

  const { menuOpen, toggleMenu } = useMenu();

  // Timelines
  const tlClosedHover = useRef<gsap.core.Timeline | null>(null);
  const tlOpenHover = useRef<gsap.core.Timeline | null>(null);
  const tlButtonClick = useRef<gsap.core.Timeline | null>(null);

  useEffect(() => {
    // Animation Config
    const hoverDuration = 0.5;
    const clickDuration = 0.8;
    const hoverEase = "power1.out"; // "ease" equivalent
    const clickEase = "power3.inOut";

    // Build Timelines
    tlClosedHover.current = gsap.timeline({ paused: true, defaults: { duration: hoverDuration, ease: hoverEase } })
      .to(topBarRef.current, { y: 5 }, 0)
      .to(bottomBarRef.current, { y: -5 }, 0)
      .to(centerBarRef.current, { rotation: 90 }, 0);

    tlOpenHover.current = gsap.timeline({ paused: true, defaults: { duration: hoverDuration, ease: hoverEase } })
      .to([topBarRef.current, bottomBarRef.current], { rotation: -45 }, 0)
      .to(centerBarRef.current, { rotation: 135 }, 0);

    tlButtonClick.current = gsap.timeline({ paused: true, defaults: { duration: clickDuration, ease: clickEase } })
      .to(buttonRef.current, { rotation: 45 });

    return () => {
      tlClosedHover.current?.kill();
      tlOpenHover.current?.kill();
      tlButtonClick.current?.kill();
    };
  }, []);

  const handleMouseEnter = () => {
    if (!menuOpen) {
      tlClosedHover.current?.play();
    } else {
      tlOpenHover.current?.play();
    }
  };

  const handleMouseLeave = () => {
    if (!menuOpen) {
      tlClosedHover.current?.reverse();
    } else {
      tlOpenHover.current?.reverse();
    }
  };

  useEffect(() => {
    if (menuOpen) {
      tlButtonClick.current?.play(0);
    } else {
      tlButtonClick.current?.reverse();
      tlOpenHover.current?.reverse();
    }
  }, [menuOpen]);

  const handleClick = () => {
    const newState = !menuOpen;
    toggleMenu();

    // Track menu toggle
    posthog.capture('menu_toggled', {
      menu_state: newState ? 'opened' : 'closed',
    });
  };

  return (
    <div id="top-of-the-page" className={styles.navbar}>
      <div className={`w-layout-blockcontainer container w-container ${styles.navbarContainer}`}>
        <div className={styles.navbarContent}>
          <div className={styles.navbarLeftSide}>
            <AuthButton />
          </div>

          {/* Logo */}
          <Link href="/" className={styles.navbarTitle}>GRANTED</Link>

          <div className={styles.navbarRightSide}>
            <div className={styles.navbarDividerWrapper}>
              <div id="navbar-divider" className={`${styles.dividerLine} ${styles.isNavbar}`}></div>
            </div>

            <div
              id="button-menu"
              className={styles.buttonMenu}
              ref={buttonRef}
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
              onClick={handleClick}
            >
              <div ref={topBarRef} className={`${styles.buttonMenuBar} ${styles.isTopBar}`}></div>
              <div ref={centerBarRef} className={`${styles.buttonMenuBar} ${styles.isCenterBar}`}></div>
              <div ref={bottomBarRef} className={`${styles.buttonMenuBar} ${styles.isBottomBar}`}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
