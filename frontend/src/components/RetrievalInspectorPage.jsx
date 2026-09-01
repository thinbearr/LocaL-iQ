import React from 'react';

export default function RetrievalInspectorPage({ answerData }) {
  if (!answerData) {
    return (
      <div style={styles.container}>
        <h1 style={styles.title}>Retrieval Inspector</h1>
        <div style={styles.subtitle}>
          Inspect query resolution, candidate scoring, BM25 reranking, and evidence selection.
        </div>
        <div style={styles.infoCard}>
          Ask a question in the Ask tab first to inspect its retrieval trajectory and scores!
        </div>
      </div>
    );
  }

  const scopeSummary = answerData.scope_info ? answerData.scope_info.summary_text : 'Current Vault';

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Retrieval Inspector</h1>
      <div style={styles.subtitle}>
        Inspect query resolution, candidate scoring, BM25 reranking, and evidence selection.
      </div>

      {/* Scope Banner */}
      <div style={styles.scopeBanner}>
        <div>
          <span style={styles.scopeLabel}>EVALUATED SEARCH SCOPE</span>
          <div style={styles.scopeVal}>{scopeSummary}</div>
        </div>
        <div style={styles.monoMeta}>
          {answerData.all_candidates ? answerData.all_candidates.length : 0} candidates evaluated
        </div>
      </div>

      {/* Step-by-Step Trajectory Diagram */}
      <div style={styles.pipelineGrid}>
        {[
          { step: 'STEP 1', name: 'Vector Search', active: true },
          { step: 'STEP 2', name: 'Candidate Pool' },
          { step: 'STEP 3', name: 'BM25 Rerank' },
          { step: 'STEP 4', name: 'Hybrid Fusion' },
          { step: 'STEP 5', name: 'Sibling Window' },
          { step: 'STEP 6', name: 'Evidence Gate' },
          { step: 'STEP 7', name: 'Answer Generation', active: true, green: true },
        ].map((item, idx) => (
          <React.Fragment key={idx}>
            <div
              style={{
                ...styles.pipelineNode,
                ...(item.active ? styles.activeNode : {}),
                ...(item.green ? styles.greenNode : {}),
              }}
            >
              <div
                style={{
                  ...styles.stepBadge,
                  color: item.green ? '#3FB950' : item.active ? '#00A896' : '#64748B',
                }}
              >
                {item.step}
              </div>
              <div style={styles.nodeName}>{item.name}</div>
            </div>
            {idx < 6 && <div style={styles.arrow}>➔</div>}
          </React.Fragment>
        ))}
      </div>

      {/* Metrics Row */}
      <div style={styles.metricsGrid}>
        <div style={styles.metricCard}>
          <div style={styles.metricLabel}>Candidates Evaluated</div>
          <div style={styles.metricVal}>{answerData.all_candidates ? answerData.all_candidates.length : 0}</div>
        </div>
        <div style={styles.metricCard}>
          <div style={styles.metricLabel}>Selected Evidence</div>
          <div style={styles.metricVal}>{answerData.primary_chunks ? answerData.primary_chunks.length : 0}</div>
        </div>
        <div style={styles.metricCard}>
          <div style={styles.metricLabel}>Top Semantic Score</div>
          <div style={styles.metricVal}>{answerData.max_raw_semantic ? answerData.max_raw_semantic.toFixed(4) : '0.0000'}</div>
        </div>
        <div style={styles.metricCard}>
          <div style={styles.metricLabel}>Top Hybrid Score</div>
          <div style={styles.metricVal}>{answerData.max_hybrid_score ? answerData.max_hybrid_score.toFixed(4) : '0.0000'}</div>
        </div>
        <div style={styles.metricCard}>
          <div style={styles.metricLabel}>Latency</div>
          <div style={styles.metricVal}>{answerData.latency_ms ? answerData.latency_ms.toFixed(1) : '0.0'} ms</div>
        </div>
      </div>

      {/* Candidate Pool Scoring Matrix */}
      <div style={{ marginTop: '32px' }}>
        <div style={styles.sectionHeader}>CANDIDATE POOL SCORING MATRIX</div>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Rank</th>
              <th style={styles.th}>Selected</th>
              <th style={styles.th}>Vault</th>
              <th style={styles.th}>Source File</th>
              <th style={styles.th}>Section</th>
              <th style={styles.th}>Raw Cosine</th>
              <th style={styles.th}>BM25 Score</th>
              <th style={styles.th}>Hybrid Score</th>
            </tr>
          </thead>
          <tbody>
            {(answerData.all_candidates || []).map((c, idx) => (
              <tr key={idx} style={styles.tr}>
                <td style={styles.td}>{c.rank}</td>
                <td style={styles.td}>
                  {c.selected ? (
                    <span style={{ color: '#00A896', fontWeight: 700 }}>Yes</span>
                  ) : (
                    <span style={{ color: '#64748B' }}>No</span>
                  )}
                </td>
                <td style={styles.td}>
                  <span style={styles.monoMeta}>{c.vault_name || 'Default'}</span>
                </td>
                <td style={styles.td}>
                  <b style={{ color: '#FFFFFF' }}>{c.file_name}</b>
                </td>
                <td style={styles.td}>{c.heading}</td>
                <td style={styles.tdMono}>{c.raw_semantic_score}</td>
                <td style={styles.tdMono}>{c.lexical_bm25_score}</td>
                <td style={styles.tdMonoHighlight}>{c.hybrid_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '1000px',
  },
  title: {
    fontFamily: "'Newsreader', Georgia, serif",
    fontSize: '2.8rem',
    fontWeight: 500,
    color: '#FFFFFF',
    marginBottom: '4px',
  },
  subtitle: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.95rem',
    color: '#8C9BAE',
    marginBottom: '24px',
  },
  infoCard: {
    backgroundColor: '#121722',
    border: '1px solid #1E2638',
    borderRadius: '10px',
    padding: '20px',
    color: '#8C9BAE',
    fontFamily: "'Roboto', sans-serif",
  },
  scopeBanner: {
    backgroundColor: '#121722',
    border: '1px solid #00A896',
    borderRadius: '10px',
    padding: '16px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },
  scopeLabel: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.72rem',
    fontWeight: 700,
    color: '#00A896',
    letterSpacing: '0.08em',
  },
  scopeVal: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '1.05rem',
    fontWeight: 600,
    color: '#FFFFFF',
    marginTop: '2px',
  },
  pipelineGrid: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#121722',
    border: '1px solid #1E2638',
    borderRadius: '12px',
    padding: '20px',
    marginBottom: '28px',
    overflowX: 'auto',
  },
  pipelineNode: {
    backgroundColor: '#182030',
    border: '1px solid #243048',
    borderRadius: '8px',
    padding: '12px 14px',
    minWidth: '110px',
    textAlign: 'center',
  },
  activeNode: {
    borderColor: '#00A896',
  },
  greenNode: {
    borderColor: '#3FB950',
  },
  stepBadge: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.72rem',
    fontWeight: 700,
  },
  nodeName: {
    fontFamily: "'Roboto', sans-serif",
    fontWeight: 700,
    fontSize: '0.84rem',
    color: '#FFFFFF',
    marginTop: '4px',
  },
  arrow: {
    color: '#64748B',
    fontSize: '1.1rem',
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(5, 1fr)',
    gap: '16px',
  },
  metricCard: {
    backgroundColor: '#121722',
    border: '1px solid #1E2638',
    borderRadius: '10px',
    padding: '16px',
  },
  metricLabel: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.78rem',
    color: '#8C9BAE',
    marginBottom: '6px',
  },
  metricVal: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '1.25rem',
    fontWeight: 700,
    color: '#FFFFFF',
  },
  sectionHeader: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.75rem',
    fontWeight: 700,
    color: '#64748B',
    letterSpacing: '0.08em',
    marginBottom: '12px',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    backgroundColor: '#121722',
    border: '1px solid #1E2638',
    borderRadius: '8px',
    overflow: 'hidden',
  },
  th: {
    textAlign: 'left',
    padding: '12px 16px',
    backgroundColor: '#182030',
    color: '#8C9BAE',
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.8rem',
    fontWeight: 700,
    borderBottom: '1px solid #1E2638',
  },
  tr: {
    borderBottom: '1px solid #1E2638',
  },
  td: {
    padding: '12px 16px',
    fontSize: '0.88rem',
    fontFamily: "'Roboto', sans-serif",
  },
  tdMono: {
    padding: '12px 16px',
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.84rem',
    color: '#8C9BAE',
  },
  tdMonoHighlight: {
    padding: '12px 16px',
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.84rem',
    color: '#00A896',
    fontWeight: 700,
  },
  monoMeta: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.82rem',
    color: '#00A896',
  },
};
