import React, { useState } from 'react';
import { Send, ArrowUpRight } from 'lucide-react';
import { GithubIcon, DiscordIcon, TwitterIcon } from './Icons';
import logo from '../assets/logo.png';

export const Footer: React.FC = () => {
  const [newsletterEmail, setNewsletterEmail] = useState('');
  const [newsletterSubscribed, setNewsletterSubscribed] = useState(false);

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newsletterEmail.trim()) return;
    setNewsletterSubscribed(true);
    setNewsletterEmail('');
    setTimeout(() => setNewsletterSubscribed(false), 3000);
  };

  return (
    <>
      {/* ── Newsletter Strip Section (Stay Updated with Patches) ── */}
      <section className="newsletter-strip-green">
        <div className="container newsletter-strip-container">
          <div>
            <h3 className="newsletter-text-title">Stay Updated with n8n CLI Patches</h3>
            <p className="newsletter-text-desc">Subscribe to stay updated with model additions, diagnostic updates, and self-healing linters.</p>
          </div>
          <form onSubmit={handleSubscribe} className="newsletter-form-green">
            <input
              type="email"
              className="newsletter-input-green"
              value={newsletterEmail}
              onChange={(e) => setNewsletterEmail(e.target.value)}
              placeholder="Your email address"
              required
            />
            <button type="submit" className="newsletter-submit-btn-green" style={{ background: 'var(--accent-color)', color: '#fff' }}>
              {newsletterSubscribed ? '✔' : <Send size={14} fill="#fff" stroke="none" />}
            </button>
          </form>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="footer-site-green">
        <div className="container footer-layout-green">
          <div className="footer-brand-logo" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <img src={logo} alt="ZeroPoint Logo" className="logo-img-footer" />
            </div>
            <p className="footer-brand-desc">
              Autonomous AI architects for n8n workflows, built on cutting-edge Google ADK and NVIDIA NIM models.
            </p>
            <div className="footer-social-icons">
              <a href="https://github.com/AbhishekC1005/n8n-cli" target="_blank" rel="noreferrer" className="footer-social-icon-btn"><GithubIcon size={16} /></a>
              <a href="#" className="footer-social-icon-btn"><DiscordIcon size={16} /></a>
              <a href="#" className="footer-social-icon-btn"><TwitterIcon size={16} /></a>
            </div>
          </div>

          <div>
            <h4 className="footer-column-title">Quick Links</h4>
            <ul className="footer-links-list">
              <li><a href="#home" className="footer-link-green">Home</a></li>
              <li><a href="#architecture" className="footer-link-green">What You Get</a></li>
              <li><a href="#features" className="footer-link-green">Capabilities</a></li>
              <li><a href="#compiler" className="footer-link-green">Spec Compiler</a></li>
            </ul>
          </div>

          <div>
            <h4 className="footer-column-title">Resources</h4>
            <ul className="footer-links-list">
              <li><a href="https://github.com/AbhishekC1005/n8n-cli" target="_blank" rel="noreferrer" className="footer-link-green">GitHub Codebase</a></li>
              <li><a href="https://n8n.io" target="_blank" rel="noreferrer" className="footer-link-green">n8n Platform</a></li>
              <li><a href="https://build.nvidia.com" target="_blank" rel="noreferrer" className="footer-link-green">NVIDIA NIM Hub</a></li>
            </ul>
          </div>

          <div>
            <h4 className="footer-column-title">Location / Endpoints</h4>
            <ul className="footer-links-list">
              <li style={{ color: 'var(--text-secondary)', fontSize: '13.5px' }}>Local instance: http://localhost:5678</li>
              <li style={{ color: 'var(--text-secondary)', fontSize: '13.5px' }}>API Version: v1</li>
              <li><a href="https://github.com/AbhishekC1005/n8n-cli" target="_blank" rel="noreferrer" className="footer-link-green" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>GitHub Repository</span>
                <ArrowUpRight size={12} />
              </a></li>
            </ul>
          </div>
        </div>

        <div className="container footer-bottom-bar">
          <span>&copy; {new Date().getFullYear()} N8N Agent CLI Project. All rights reserved.</span>
          <div className="footer-privacy-links">
            <a href="#" className="footer-link-green">Privacy Policy</a>
            <a href="#" className="footer-link-green">Terms of Service</a>
          </div>
        </div>
      </footer>
    </>
  );
};
