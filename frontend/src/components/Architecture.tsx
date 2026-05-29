import React from 'react';
import { ArrowRight, Sparkles } from 'lucide-react';

export const Architecture: React.FC = () => {
  return (
    <section id="architecture" className="about-site reveal-on-scroll">
      <div className="container about-layout">
        <div>
          <div className="badge-pill">
            <div className="badge-dot"></div>
            <span>The Architecture</span>
          </div>
          
          <h2 className="about-headline">
            Driven by <span className="text-neon">Google ADK</span>, <br />
            Optimized by NVIDIA NIM.
          </h2>
          
          <h3 className="about-desc-heading">Autonomous Dual-Agent Engine</h3>
          <p className="about-desc-text">
            The project splits conversational tasks from write/modify workflow processes. The main agent handles lookup commands directly, while delegating heavy schema writing to the developer subagent.
          </p>
          
          <a href="#features" className="btn-outline btn-outline-green">
            <span>View Agent Features</span>
            <ArrowRight size={14} />
          </a>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          <div className="chips-grid-about">
            <div className="chip-card-about">Google ADK</div>
            <div className="chip-card-about" style={{ borderColor: 'var(--accent-color)', boxShadow: '0 0 10px rgba(220, 38, 38, 0.08)' }}>NVIDIA NIM</div>
            <div className="chip-card-about">LiteLLM</div>
            <div className="chip-card-about">n8n API</div>
            <div className="chip-card-about" style={{ borderColor: 'var(--accent-color)', boxShadow: '0 0 10px rgba(220, 38, 38, 0.08)' }}>Self-Healing</div>
          </div>

          <div className="card-green" style={{ padding: '32px', display: 'flex', gap: '20px', alignItems: 'center' }}>
            <div className="service-icon-green" style={{ marginBottom: 0 }}>
              <Sparkles size={20} />
            </div>
            <div>
              <h4 style={{ color: '#fff', fontSize: '16px', marginBottom: '4px' }}>AUTONOMOUS NODE WIRING</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px', lineHeight: 1.5 }}>
                The subagent parses parameters, links connection cords horizontally, and automatically fetches local database or messaging credentials from n8n.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
