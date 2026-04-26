import { Metadata } from 'next';
import Hero from '@/components/landing/Hero';
import HowItWorks from '@/components/landing/HowItWorks';
import Features from '@/components/landing/Features';
import Testimonials from '@/components/landing/Testimonials';
import FinalCTA from '@/components/landing/FinalCTA';
import Footer from '@/components/landing/Footer';

export const metadata: Metadata = {
  title: 'SpeakFlow - Aprenda inglês falando com tutor de IA',
  description: 'Pratique sua pronúncia e conversação em inglês com nosso tutor de IA inteligente. Correção em tempo real, flashcards automáticos e progresso gamificado.',
  keywords: ['aprender inglês', 'tutor de IA', 'prática de conversação', 'pronúncia', 'flashcards'],
  openGraph: {
    title: 'SpeakFlow - Aprenda inglês falando com tutor de IA',
    description: 'Pratique sua pronúncia e conversação em inglês com nosso tutor de IA inteligente.',
    type: 'website',
    locale: 'pt_BR',
    url: 'https://speakflow.com',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'SpeakFlow - Aprenda inglês falando',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SpeakFlow - Aprenda inglês falando com tutor de IA',
    description: 'Pratique sua pronúncia e conversação em inglês com nosso tutor de IA inteligente.',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white">
      <Hero />
      <HowItWorks />
      <Features />
      <Testimonials />
      <FinalCTA />
      <Footer />
    </main>
  );
}
