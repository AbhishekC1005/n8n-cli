import React from 'react';
import { ArrowRight, ShieldCheck } from 'lucide-react';

export const Outcomes: React.FC = () => {
  return (
    <section id="architecture" className="about-site reveal-on-scroll">
      <div className="container about-layout">
        <div>
          <div className="badge-pill">
            <div className="badge-dot"></div>
            <span>What You Get</span>
          </div>
          
          <h2 className="about-headline">
            Designed for Speed. <br />
            Built for <span className="text-neon">Absolute Security</span>.
          </h2>
          
          <h3 className="about-desc-heading">A Local Co-Pilot That Does the Heavy Lifting</h3>
          <p className="about-desc-text">
            We are giving you a powerful, local terminal assistant that completely replaces manual visual workflow construction. Describe your goals, and get secure, fully wired automation code in seconds.
          </p>
          
          <a href="#features" className="btn-outline btn-outline-green">
            <span>Explore Capabilities</span>
            <ArrowRight size={14} />
          </a>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          <div className="chips-grid-about">
            <div className="chip-card-about" style={{ borderColor: 'var(--accent-color)', boxShadow: '0 0 10px rgba(220, 38, 38, 0.08)' }}>10x Faster Building</div>
            <div className="chip-card-about">Zero Secret Leaks</div>
            <div className="chip-card-about" style={{ borderColor: 'var(--accent-color)', boxShadow: '0 0 10px rgba(220, 38, 38, 0.08)' }}>Self-Healing top</div>
            <div className="chip-card-about">100% Offline Control</div>
            <div className="chip-card-about">Ready-To-Run Specs</div>
          </div>

          <div className="card-green" style={{ padding: '32px', display: 'flex', gap: '20px', alignItems: 'center' }}>
            <div className="service-icon-green" style={{ marginBottom: 0 }}>
              <ShieldCheck size={20} style={{ color: 'var(--accent-color)' }} />
            </div>
            <div>
              <h4 style={{ color: '#fff', fontSize: '16px', marginBottom: '4px' }}>ENTERPRISE SECRETS PROTECTION</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px', lineHeight: 1.5 }}>
                No database credentials or integration keys are ever sent or exposed. The agent queries your local active profiles automatically and references them safely via internal IDs.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
