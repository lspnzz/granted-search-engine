'use client';

import { ReactLenis } from 'lenis/react';
import { ReactNode } from 'react';
import 'lenis/dist/lenis.css';

function SmoothScrolling({ children }: { children: ReactNode }) {
  const lenisOptions = {
    lerp: 0.05,
    duration: 1.2,
    smoothWheel: true,
    easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    touchMultiplier: 2,
  };

  return (
    <ReactLenis root options={lenisOptions}>
      {children}
    </ReactLenis>
  );
}

export default SmoothScrolling;
