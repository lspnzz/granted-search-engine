'use client';

import { ReactNode } from 'react';
import { MenuProvider } from '../context/MenuContext';
import Menu from './Menu';

export default function PageWrapper({ children }: { children: ReactNode }) {
  return (
    <MenuProvider>
      <div className="page-wrapper">
        <div className='shadow'></div>
        <Menu />
        {children}
      </div>
    </MenuProvider>
  );
}
