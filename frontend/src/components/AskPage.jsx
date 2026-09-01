import React, { useState } from 'react';

export default function AskPage({ status, onAsk, isLoading, answerData }) {
  const [query, setQuery] = useState('');

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onAsk(query);
    }
  };

  const handleSampleClick = (sampleQuery) => {
    setQuery(sampleQuery);
    onAsk(sampleQuery);
  };

  return (
    <div style={styles.container}>
      {/* Hero Header */}
      <div style={styles.greeting}>{getGreeting()}</div>
      <h1 style={styles.heroTitle}>
        What would you like<br />
        to know?
      </h1>
      <div style={styles.heroSubtitle}>Ask anything about your connected knowledge.</div>

      {/* Primary Question Composer Box */}
      <form onSubmit={handleSubmit} style={styles.composerCard}>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question across your connected notes..."
          rows={3}
          style={styles.textarea}
        />
        <div style={styles.composerFooter}>
          <div style={styles.composerMetadata}>
            <span>✧</span> Powered by RAG &nbsp;·&nbsp; Grounded in your knowledge &nbsp;·&nbsp; Private & local
          </div>
          <button type="submit" disabled={isLoading || !query.trim()} style={styles.askButton}>
            {isLoading ? 'Retrieving...' : 'Ask Question'}
            <svg style={{ width: 16, height: 16, fill: '#FFFFFF' }} viewBox="0 0 24 24">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
            </svg>
          </button>
        </div>
      </form>

      {/* Answer Component if available */}
      {answerData && (
        <div style={styles.answerCard}>
          <div style={styles.answerHeader}>Answer</div>
          <div style={styles.answerBody}>{answerData.answer}</div>

          {answerData.primary_chunks && answerData.primary_chunks.length > 0 && (
            <div style={{ marginTop: '24px' }}>
              <div style={styles.evidenceTitle}>Grounded Source Evidence</div>
              {answerData.primary_chunks.map((chunk, idx) => (
                <div key={chunk.chunk_id || idx} style={styles.evidenceItem}>
                  <div style={styles.evidenceTopRow}>
                    <div>
                      <b style={{ color: '#FFFFFF', fontFamily: "'Roboto', sans-serif" }}>{chunk.file_name}</b>
                      &nbsp;<span style={styles.monoMeta}>[{chunk.heading}]</span>
                    </div>
                    <span style={styles.monoMeta}>Hybrid Score: {chunk.hybrid_score}</span>
                  </div>
                  <div style={styles.chunkText}>{chunk.text}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Try Asking Something Like Section */}
      <div style={{ marginTop: '32px' }}>
        <div style={styles.sampleSectionTitle}>Try asking something like</div>
        <div style={styles.sampleGrid}>
          <div
            onClick={() => handleSampleClick('What are the main validation checks?')}
            style={styles.sampleCard}
          >
            <div style={styles.sampleCardTop}>
              <div style={styles.sampleCardText}>
                What are the main<br />
                validation checks?
              </div>
              <svg style={styles.arrowIcon} viewBox="0 0 24 24">
                <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" />
              </svg>
            </div>
            <div style={styles.sampleCardSource}>IDEX_Project.md</div>
          </div>

          <div
            onClick={() => handleSampleClick('How are cable routing paths calculated?')}
            style={styles.sampleCard}
          >
            <div style={styles.sampleCardTop}>
              <div style={styles.sampleCardText}>
                How are cable routing<br />
                paths calculated?
              </div>
              <svg style={styles.arrowIcon} viewBox="0 0 24 24">
                <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" />
              </svg>
            </div>
            <div style={styles.sampleCardSource}>architecture.md</div>
          </div>

          <div
            onClick={() => handleSampleClick('Explain the retrieval architecture.')}
            style={styles.sampleCard}
          >
            <div style={styles.sampleCardTop}>
              <div style={styles.sampleCardText}>
                Explain the retrieval<br />
                architecture.
              </div>
              <svg style={styles.arrowIcon} viewBox="0 0 24 24">
                <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" />
              </svg>
            </div>
            <div style={styles.sampleCardSource}>retrieval.md</div>
          </div>
        </div>
      </div>

      {/* Bottom Feature Highlights Bar */}
      <div style={styles.featuresBar}>
        <div>
          <div style={styles.featureTitle}>Your knowledge</div>
          <div style={styles.featureDesc}>
            {status.active_files || 1} document<br />
            {status.active_chunks || 16} chunks
          </div>
        </div>
        <div>
          <div style={styles.featureTitle}>Private & secure</div>
          <div style={styles.featureDesc}>All data stays on your device</div>
        </div>
        <div>
          <div style={styles.featureTitle}>Fast retrieval</div>
          <div style={styles.featureDesc}>Hybrid search with semantic + BM25</div>
        </div>
        <div>
          <div style={styles.featureTitle}>Grounded answers</div>
          <div style={styles.featureDesc}>Every answer is backed by your sources</div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '960px',
    margin: '0 auto',
  },
  greeting: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.95rem',
    color: '#00A896',
    fontWeight: 500,
    marginBottom: '8px',
  },
  heroTitle: {
    fontFamily: "'Newsreader', Georgia, serif",
    fontSize: '3.6rem',
    fontWeight: 500,
    color: '#FFFFFF',
    letterSpacing: '-0.02em',
    lineHeight: 1.1,
    marginBottom: '12px',
  },
  heroSubtitle: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '1.05rem',
    color: '#8C9BAE',
    marginBottom: '28px',
  },
  composerCard: {
    backgroundColor: '#121722',
    border: '1px solid #1E2638',
    borderRadius: '14px',
    padding: '20px',
    marginBottom: '28px',
    boxShadow: '0 10px 30px rgba(0, 0, 0, 0.25)',
  },
  textarea: {
    width: '100%',
    backgroundColor: 'transparent',
    border: 'none',
    outline: 'none',
    color: '#FFFFFF',
    fontFamily: "'Roboto', sans-serif",
    fontSize: '1.05rem',
    lineHeight: 1.5,
    resize: 'none',
  },
  composerFooter: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: '14px',
    paddingTop: '14px',
    borderTop: '1px solid #1E2638',
  },
  composerMetadata: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.82rem',
    color: '#64748B',
  },
  askButton: {
    backgroundColor: '#00A896',
    border: 'none',
    borderRadius: '8px',
    color: '#FFFFFF',
    fontFamily: "'Roboto', sans-serif",
    padding: '10px 20px',
    fontSize: '0.92rem',
    fontWeight: 700,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    transition: 'background-color 0.2s ease',
  },
  answerCard: {
    backgroundColor: '#121722',
    border: '1px solid #1E2638',
    borderRadius: '14px',
    padding: '28px',
    marginBottom: '28px',
  },
  answerHeader: {
    fontFamily: "'Newsreader', Georgia, serif",
    fontSize: '1.8rem',
    fontWeight: 500,
    color: '#FFFFFF',
    marginBottom: '12px',
  },
  answerBody: {
    fontFamily: "'Roboto', sans-serif",
    lineHeight: 1.65,
    color: '#F0F4F8',
    fontSize: '1.0rem',
  },
  evidenceTitle: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.95rem',
    fontWeight: 700,
    color: '#FFFFFF',
    marginBottom: '12px',
  },
  evidenceItem: {
    backgroundColor: '#182030',
    border: '1px solid #243048',
    borderLeft: '4px solid #00A896',
    borderRadius: '8px',
    padding: '16px',
    marginBottom: '12px',
  },
  evidenceTopRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
    fontSize: '0.9rem',
  },
  monoMeta: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.82rem',
    color: '#00A896',
  },
  chunkText: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.84rem',
    color: '#8C9BAE',
    backgroundColor: '#121722',
    padding: '12px',
    borderRadius: '6px',
    border: '1px solid #1E2638',
    whiteSpace: 'pre-wrap',
  },
  sampleSectionTitle: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.95rem',
    fontWeight: 500,
    color: '#F0F4F8',
    marginBottom: '14px',
  },
  sampleGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '16px',
  },
  sampleCard: {
    backgroundColor: '#121722',
    border: '1px solid #1E2638',
    borderRadius: '12px',
    padding: '20px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  sampleCardTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '12px',
  },
  sampleCardText: {
    fontFamily: "'Roboto', sans-serif",
    fontWeight: 500,
    fontSize: '0.96rem',
    color: '#F0F4F8',
    lineHeight: 1.4,
  },
  arrowIcon: {
    width: '18px',
    height: '18px',
    fill: '#00A896',
    minWidth: '18px',
  },
  sampleCardSource: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.78rem',
    color: '#64748B',
  },
  featuresBar: {
    backgroundColor: '#121722',
    border: '1px solid #1E2638',
    borderRadius: '14px',
    padding: '22px',
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '20px',
    marginTop: '36px',
  },
  featureTitle: {
    fontFamily: "'Roboto', sans-serif",
    fontWeight: 700,
    fontSize: '0.95rem',
    color: '#FFFFFF',
    marginBottom: '4px',
  },
  featureDesc: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.82rem',
    color: '#8C9BAE',
    lineHeight: 1.4,
  },
};
