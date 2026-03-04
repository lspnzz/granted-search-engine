'use client';

import { ReactNode, useEffect, useRef } from 'react';
import gsap from 'gsap';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { MenuProvider, useMenu } from '../context/MenuContext';
import { useLenis } from 'lenis/react';
import ProfilePanel from './ProfilePanel';
import Menu from './Menu';

function PageContent({ children }: { children: ReactNode }) {
  const { panelOpen } = useAuth();
  const { menuOpen } = useMenu();
  const pageWrapperRef = useRef<HTMLDivElement>(null);
  const tlReveal = useRef<gsap.core.Timeline | null>(null);
  const lenis = useLenis();

  useEffect(() => {
    // Animation Config - matching Menu.tsx
    const clickDuration = 0.8;
    const clickEase = "power3.inOut";

    tlReveal.current = gsap.timeline({ paused: true, defaults: { duration: clickDuration, ease: clickEase } })
      .to(pageWrapperRef.current, { x: "var(--profile-panel-width)" });

    return () => {
      tlReveal.current?.kill();
    };
  }, []);

  useEffect(() => {
    if (panelOpen) {
      tlReveal.current?.play();
    } else {
      tlReveal.current?.reverse();
    }
  }, [panelOpen]);

  useEffect(() => {
    if (panelOpen || menuOpen) {
      lenis?.stop();
      document.body.style.overflow = 'hidden';
    } else {
      lenis?.start();
      document.body.style.overflow = '';
    }

    return () => {
      lenis?.start();
      document.body.style.overflow = '';
    };
  }, [panelOpen, menuOpen, lenis]);

  return (
    <>
      <ProfilePanel />
      <div
        className="page-wrapper"
        ref={pageWrapperRef}
      >
        <div className='shadow'></div>
        <Menu />
        {children}
      </div>
    </>
  );
}

export default function PageWrapper({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <MenuProvider>
        <PageContent>{children}</PageContent>
      </MenuProvider>
    </AuthProvider>
  );
}
