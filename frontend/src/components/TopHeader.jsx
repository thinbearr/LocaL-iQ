import React from 'react';

export default function TopHeader({ status, vaultScope, selectedVaults }) {
  const isCurrent = vaultScope === 'Current Vault';
  const isSelected = vaultScope === 'Selected Vaults';

  let scopeText = `Vault: ${status.active_vault_name || 'IDEX'}`;
  let docsCount = status.active_files || 1;
  let chunksCount = status.active_chunks || 16;

  if (isSelected) {
    scopeText = `Search Scope: ${selectedVaults.length} Vaults (${selectedVaults.join(' · ')})`;
    docsCount = status.total_files || docsCount;
    chunksCount = status.total_chunks || chunksCount;
  } else if (vaultScope === 'All Vaults') {
    scopeText = 'Search Scope: All Discovered Vaults';
    docsCount = status.total_files || docsCount;
    chunksCount = status.total_chunks || chunksCount;
  }

  return (
    <div style={styles.headerBar}>
      <div style={styles.pillContainer}>
        <div style={styles.scopeText}>
          {scopeText}
        </div>
        <div style={styles.divider}>|</div>
        <div>
          <span style={{ color: '#00A896', fontWeight: 700 }}>{docsCount}</span> {docsCount === 1 ? 'document' : 'documents'} &nbsp;·&nbsp;{' '}
          <span style={{ color: '#00A896', fontWeight: 700 }}>{chunksCount}</span> chunks
        </div>
        <div style={styles.divider}>|</div>
        <div style={styles.syncBadge}>
          <svg style={{ width: 14, height: 14, fill: '#00A896' }} viewBox="0 0 24 24">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
          </svg>
          <span>SYNCED</span>
        </div>
      </div>
    </div>
  );
}

const styles = {
  headerBar: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginBottom: '20px',
  },
  pillContainer: {
    backgroundColor: '#121722',
    border: '1px solid #1E2638',
    borderRadius: '8px',
    padding: '8px 18px',
    fontSize: '0.86rem',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    color: '#8C9BAE',
    fontFamily: "'Roboto', sans-serif",
  },
  scopeText: {
    color: '#FFFFFF',
    fontWeight: 500,
  },
  divider: {
    color: '#1E2638',
  },
  syncBadge: {
    backgroundColor: 'rgba(0, 168, 150, 0.12)',
    color: '#00A896',
    border: '1px solid #00A896',
    borderRadius: '6px',
    padding: '3px 8px',
    fontSize: '0.75rem',
    fontWeight: 700,
    letterSpacing: '0.04em',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
};
