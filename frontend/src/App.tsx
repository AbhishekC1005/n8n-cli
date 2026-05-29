import { useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { Outcomes } from './components/Outcomes';
import { TerminalShowcase } from './components/TerminalShowcase';
import { Features } from './components/Features';
import { Templates } from './components/Templates';
import { Reviews } from './components/Reviews';
import { CompilerShowcase } from './components/CompilerShowcase';
import { Setup } from './components/Setup';
import { Footer } from './components/Footer';

function App() {
  useEffect(() => {
    // Disable browser native scroll restoration and force page scroll to top on load/reload
    if ('scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual';
    }
    window.scrollTo(0, 0);

    const handleScrollReveal = () => {
      const revealElements = document.querySelectorAll('.reveal-on-scroll');
      const triggerBottom = window.innerHeight * 0.92; // 8% vertical padding offset

      revealElements.forEach(el => {
        const box = el.getBoundingClientRect();
        // If the top of the element rolls into the trigger zone
        if (box.top < triggerBottom) {
          el.classList.add('reveal-visible');
        } else {
          // Revert when scrolled past (scrolling up)
          el.classList.remove('reveal-visible');
        }
      });
    };

    // Stagger slightly on mount to let React painting commit cleanly
    const timer = setTimeout(() => {
      handleScrollReveal();
      window.addEventListener('scroll', handleScrollReveal);
    }, 150);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('scroll', handleScrollReveal);
    };
  }, []);

  return (
    <>
      {/* ── Background Blobs ── */}
      <div className="organic-blob-left"></div>
      <div className="organic-blob-right"></div>

      <Navbar />
      <Hero />
      <Outcomes />
      <TerminalShowcase />
      <Features />
      <Templates />
      <Reviews />
      <CompilerShowcase />
      <Setup />
      <Footer />
    </>
  );
}

export default App;
