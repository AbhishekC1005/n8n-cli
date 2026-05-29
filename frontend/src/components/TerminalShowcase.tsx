import React from 'react';
import { TerminalSimulator } from './TerminalSimulator';

export const TerminalShowcase: React.FC = () => {
  return (
    <section id="terminal-showcase" className="reveal-on-scroll" style={{ padding: '140px 0', borderTop: '1px solid rgba(255,255,255,0.02)', position: 'relative', overflow: 'hidden' }}>
      {/* Glow Shadow Dot Backdrop Effect */}
      <div className="terminal-glow-dot"></div>

      <div className="container">
        <div className="section-badge-center" style={{ marginBottom: '60px' }}>
          <div className="badge-pill">
            <div className="badge-dot"></div>
            <span>Stateful CLI Console</span>
          </div>
          <h2 className="title-section">Interactive <span className="text-neon">CLI Agent Simulator</span></h2>
          <p className="desc-section">
            Directly query workflow states, trigger diagnostic audits, and let the agent orchestrate multi-node templates using real conversational terminal controls.
          </p>
        </div>
        <div style={{ maxWidth: '900px', margin: '0 auto', position: 'relative', zIndex: 1 }}>
          <TerminalSimulator />
        </div>
      </div>
    </section>
  );
};
