import React, { useState, useEffect } from 'react';
import { GithubIcon } from './Icons';
import logo from '../assets/logo.png';

export const Navbar: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={`navbar-site ${isScrolled ? 'navbar-scrolled' : ''}`}>
      <div className="container navbar-container">
        <a href="#" className="logo-brand">
          <img src={logo} alt="ZeroPoint Logo" className="logo-img" />
        </a>
        
        <nav>
          <ul className="navbar-links">
            <li><a href="#home" className="navbar-link">Home</a></li>
            <li><a href="#architecture" className="navbar-link">What You Get</a></li>
            <li><a href="#features" className="navbar-link">Features</a></li>
            <li><a href="#templates" className="navbar-link">Templates</a></li>
            <li><a href="#reviews" className="navbar-link">Reviews</a></li>
            <li><a href="#compiler" className="navbar-link">Compiler</a></li>
            <li><a href="#setup" className="navbar-link">Setup</a></li>
          </ul>
        </nav>

        <a href="https://github.com/AbhishekC1005/n8n-cli" target="_blank" rel="noreferrer" className="btn-outline btn-outline-green" style={{ padding: '10px 20px', fontSize: '13.5px' }}>
          <GithubIcon size={16} />
          <span>View GitHub</span>
        </a>
      </div>
    </header>
  );
};
