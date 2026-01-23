import type { Metadata } from 'next';
import './globals.css';
import PageWrapper from '../components/PageWrapper';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export const metadata: Metadata = {
  title: 'Studio Quinto | Search',
  description: 'We design and develop Beautiful Software.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <PageWrapper>
          <Navbar />
          <main className="main-wrapper">
            {children}
          </main>
          <Footer />
        </PageWrapper>
      </body>
    </html>
  );
}
