import type { Metadata } from 'next';
import './globals.css';
import PageWrapper from '../components/PageWrapper';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import SmoothScrolling from '../components/SmoothScrolling';

export const metadata: Metadata = {
  title: 'Granted.',
  description: 'Find EU grants for your project.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <SmoothScrolling>
          <PageWrapper>
            <Navbar />
            <main className="main-wrapper">
              {children}
            </main>
            <Footer />
          </PageWrapper>
        </SmoothScrolling>
      </body>
    </html>
  );
}
