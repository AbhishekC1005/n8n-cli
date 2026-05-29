import React from 'react';
import { Star, ArrowRight } from 'lucide-react';

export const Reviews: React.FC = () => {
  return (
    <section id="reviews" className="testimonials-site reveal-on-scroll" style={{ borderTop: '1px solid rgba(255,255,255,0.02)' }}>
      <div className="container">
        <div className="section-badge-center">
          <div className="badge-pill">
            <div className="badge-dot"></div>
            <span>Developer Reviews</span>
          </div>
          <h2 className="title-section">What our <span className="font-serif text-neon">Users</span> Say</h2>
          <p className="desc-section">
            Feedback from engineers and DevOps leads who are automating their workflows using the n8n CLI Agent.
          </p>
        </div>

        <div className="testimonials-grid-layout">
          {/* Review 1 */}
          <div className="testimonial-card-green card-green">
            <div className="testimonial-quote-large">“</div>
            <div className="testimonial-reviewer-info">
              <div className="reviewer-avatar-green">SK</div>
              <div>
                <div className="reviewer-details-name">Satoshi Koto</div>
                <div className="reviewer-details-title">DevOps Tech Lead</div>
              </div>
            </div>
            <div className="reviewer-stars-green">
              {[...Array(5)].map((_, i) => <Star key={i} size={13} fill="#eab308" stroke="none" />)}
            </div>
            <p className="testimonial-text-green">
              "Spawning the n8n Developer Subagent from my terminal is incredibly fast. Constructing Slack reminders and synchronizing database queries from natural language descriptions saves us hours of manual layout configurations in the GUI."
            </p>
            <div className="testimonial-quote-large-bottom">”</div>
          </div>

          {/* Review 2 */}
          <div className="testimonial-card-green card-green">
            <div className="testimonial-quote-large">“</div>
            <div className="testimonial-reviewer-info">
              <div className="reviewer-avatar-green">EB</div>
              <div>
                <div className="reviewer-details-name">Evelyn Blake</div>
                <div className="reviewer-details-title">Automation Architect</div>
              </div>
            </div>
            <div className="reviewer-stars-green">
              {[...Array(5)].map((_, i) => <Star key={i} size={13} fill="#eab308" stroke="none" />)}
            </div>
            <p className="testimonial-text-green">
              "The credential auto-discovery feature is absolute gold. It queries our active integrations (Sheets, Postgres OAuth) and maps their IDs securely into the JSON tree. No password leaks in git history!"
            </p>
            <div className="testimonial-quote-large-bottom">”</div>
          </div>

          {/* Review 3 */}
          <div className="testimonial-card-green card-green">
            <div className="testimonial-quote-large">“</div>
            <div className="testimonial-reviewer-info">
              <div className="reviewer-avatar-green">JM</div>
              <div>
                <div className="reviewer-details-name">Jared Martinez</div>
                <div className="reviewer-details-title">Backend Tech Lead</div>
              </div>
            </div>
            <div className="reviewer-stars-green">
              {[...Array(5)].map((_, i) => <Star key={i} size={13} fill="#eab308" stroke="none" />)}
            </div>
            <p className="testimonial-text-green">
              "The stateful terminal simulator shell is magnificent. Running `/list` to check workflow statuses, and having the self-healing linter repair broken connection names automatically, gives us pure speed."
            </p>
            <div className="testimonial-quote-large-bottom">”</div>
          </div>
        </div>

        <div style={{ textAlign: 'center' }}>
          <a href="https://github.com/AbhishekC1005/n8n-cli" target="_blank" rel="noreferrer" className="btn-outline btn-outline-green">
            <span>View GitHub Discussions</span>
            <ArrowRight size={14} style={{ color: 'var(--accent-color)' }} />
          </a>
        </div>
      </div>
    </section>
  );
};
