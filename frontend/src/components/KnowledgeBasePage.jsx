import React, { useState, useEffect } from 'react';

export default function KnowledgeBasePage({ status, vaults, vaultScope, selectedVaults, onSelectVault, onRescan, onSync }) {
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);

  const fetchDocuments = async () => {
    setLoadingDocs(true);
    try {
      const url = `http://127.0.0.1:5000/api/documents?vault_scope=${encodeURIComponent(vaultScope)}&selected_vaults=${encodeURIComponent(selectedVaults.join(','))}`;
      const res = await fetch(url);
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch (e) {
      console.error('Error fetching documents:', e);
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [status.active_vault_path, vaultScope, selectedVaults]);

  const handleDelete = async (fileName) => {
    try {
      await fetch(`http://127.0.0.1:5000/api/documents/${encodeURIComponent(fileName)}`, {
        method: 'DELETE',
      });
      fetchDocuments();
    } catch (e) {
      console.error('Error deleting document:', e);
    }
  };

  let scopeSummaryText = `Current Vault (${status.active_vault_name || 'IDEX'})`;
  if (vaultScope === 'Selected Vaults') {
    scopeSummaryText = `${selectedVaults.length} Vaults Selected (${selectedVaults.join(' · ')})`;
  } else if (vaultScope === 'All Vaults') {
    scopeSummaryText = 'All Discovered Vaults';
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Knowledge Base</h1>
      <div style={styles.subtitle}>
        Manage connected Obsidian vaults and document synchronization.
      </div>

      <div style={styles.actionBar}>
        <button onClick={onRescan} style={styles.secondaryButton}>
          Rescan Vaults
        </button>
        <button onClick={onSync} style={styles.primaryButton}>
          Sync Current Vault
        </button>
      </div>

      {/* Global Search Scope Banner */}
      <div style={styles.scopeBanner}>
        <div>
          <span style={styles.scopeLabel}>CURRENT SEARCH SCOPE</span>
          <div style={styles.scopeVal}>{scopeSummaryText}</div>
        </div>
        <div style={styles.monoMeta}>
          {documents.length} {documents.length === 1 ? 'file' : 'files'} in scope
        </div>
      </div>

      <div style={styles.grid}>
        {/* Discovered Vaults Column */}
        <div>
          <div style={styles.sectionHeader}>DISCOVERED VAULTS</div>
          {vaults.map((v) => (
            <div
              key={v.path}
              style={{
                ...styles.vaultCard,
                ...(v.is_active ? styles.activeVaultCard : {}),
              }}
            >
              <div style={styles.vaultCardTop}>
                <b style={{ color: '#FFFFFF', fontSize: '1.05rem' }}>{v.name}</b>
                {v.is_active ? (
                  <span style={styles.activeBadge}>ACTIVE</span>
                ) : (
                  <button
                    onClick={() => onSelectVault(v.path)}
                    style={styles.connectButton}
                  >
                    Connect
                  </button>
                )}
              </div>
              <div style={styles.monoMeta}>
                {v.md_count} files &nbsp;·&nbsp; {v.chunk_count} chunks
              </div>
            </div>
          ))}
        </div>

        {/* Workspace Active Vault & Scope Column */}
        <div>
          <div style={styles.sectionHeader}>MANAGED ACTIVE VAULT</div>
          <div style={styles.workspaceCard}>
            <div style={styles.vaultCardTop}>
              <div>
                <h3 style={styles.workspaceName}>{status.active_vault_name}</h3>
                <div style={styles.monoMeta}>Path: {status.active_vault_path}</div>
              </div>
              <span style={styles.detectedBadge}>OBSIDIAN DETECTED</span>
            </div>
          </div>

          <div style={{ marginTop: '24px' }}>
            <div style={styles.sectionHeader}>DOCUMENTS IN SEARCH SCOPE</div>
            {loadingDocs ? (
              <div style={{ color: '#8C9BAE' }}>Loading documents...</div>
            ) : documents.length === 0 ? (
              <div style={{ color: '#8C9BAE' }}>No documents in current search scope.</div>
            ) : (
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Filename</th>
                    {vaultScope !== 'Current Vault' && <th style={styles.th}>Vault</th>}
                    <th style={styles.th}>Chunks</th>
                    <th style={styles.th}>Status</th>
                    <th style={styles.th}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc, idx) => (
                    <tr key={idx} style={styles.tr}>
                      <td style={styles.td}>
                        <b style={{ color: '#FFFFFF' }}>{doc.file_name}</b>
                      </td>
                      {vaultScope !== 'Current Vault' && (
                        <td style={styles.td}>
                          <span style={styles.monoMeta}>{doc.vault_name || status.active_vault_name}</span>
                        </td>
                      )}
                      <td style={styles.td}>
                        <span style={styles.monoMeta}>{doc.chunk_count} chunks</span>
                      </td>
                      <td style={styles.td}>
                        <span style={styles.indexedBadge}>INDEXED</span>
                      </td>
                      <td style={styles.td}>
                        <button
                          onClick={() => handleDelete(doc.file_name)}
                          style={styles.deleteButton}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
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
  actionBar: {
    display: 'flex',
    gap: '12px',
    marginBottom: '20px',
  },
  scopeBanner: {
    backgroundColor: '#121722',
    border: '1px solid #00A896',
    borderRadius: '10px',
    padding: '16px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '28px',
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
  primaryButton: {
    backgroundColor: '#00A896',
    border: 'none',
    borderRadius: '8px',
    color: '#FFFFFF',
    fontFamily: "'Roboto', sans-serif",
    padding: '10px 18px',
    fontSize: '0.9rem',
    fontWeight: 700,
    cursor: 'pointer',
  },
  secondaryButton: {
    backgroundColor: '#182030',
    border: '1px solid #243048',
    borderRadius: '8px',
    color: '#F0F4F8',
    fontFamily: "'Roboto', sans-serif",
    padding: '10px 18px',
    fontSize: '0.9rem',
    fontWeight: 500,
    cursor: 'pointer',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 2fr',
    gap: '24px',
  },
  sectionHeader: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.75rem',
    fontWeight: 700,
    color: '#64748B',
    letterSpacing: '0.08em',
    marginBottom: '12px',
  },
  vaultCard: {
    backgroundColor: '#121722',
    border: '1px solid #1E2638',
    borderRadius: '10px',
    padding: '16px',
    marginBottom: '12px',
  },
  activeVaultCard: {
    borderColor: '#00A896',
    borderLeft: '4px solid #00A896',
  },
  vaultCardTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
  },
  activeBadge: {
    backgroundColor: 'rgba(0, 168, 150, 0.12)',
    color: '#00A896',
    border: '1px solid #00A896',
    borderRadius: '4px',
    padding: '2px 8px',
    fontSize: '0.7rem',
    fontWeight: 700,
    fontFamily: "'Roboto', sans-serif",
  },
  connectButton: {
    backgroundColor: 'transparent',
    border: '1px solid #243048',
    borderRadius: '6px',
    color: '#8C9BAE',
    fontFamily: "'Roboto', sans-serif",
    padding: '4px 10px',
    fontSize: '0.78rem',
    fontWeight: 500,
    cursor: 'pointer',
  },
  workspaceCard: {
    backgroundColor: '#121722',
    border: '1px solid #1E2638',
    borderRadius: '10px',
    padding: '20px',
  },
  workspaceName: {
    fontFamily: "'Newsreader', Georgia, serif",
    fontSize: '1.8rem',
    fontWeight: 500,
    color: '#FFFFFF',
    margin: 0,
  },
  detectedBadge: {
    backgroundColor: 'rgba(0, 168, 150, 0.12)',
    color: '#00A896',
    border: '1px solid #00A896',
    borderRadius: '4px',
    padding: '4px 10px',
    fontSize: '0.75rem',
    fontWeight: 700,
    fontFamily: "'Roboto', sans-serif",
  },
  monoMeta: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.8rem',
    color: '#00A896',
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
  indexedBadge: {
    backgroundColor: 'rgba(0, 168, 150, 0.12)',
    color: '#00A896',
    borderRadius: '4px',
    padding: '2px 8px',
    fontSize: '0.72rem',
    fontWeight: 700,
    fontFamily: "'Roboto', sans-serif",
  },
  deleteButton: {
    backgroundColor: 'transparent',
    border: '1px solid #243048',
    borderRadius: '6px',
    color: '#FF6B6B',
    fontFamily: "'Roboto', sans-serif",
    padding: '4px 10px',
    fontSize: '0.78rem',
    cursor: 'pointer',
  },
};
