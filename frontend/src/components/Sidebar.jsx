import React from 'react';

export default function Sidebar({
  status,
  vaults,
  activeTab,
  setActiveTab,
  vaultScope,
  setVaultScope,
  selectedVaults,
  setSelectedVaults,
  onSelectVault,
  onRescan
}) {
  const handleCheckboxToggle = (vaultName) => {
    if (selectedVaults.includes(vaultName)) {
      setSelectedVaults(selectedVaults.filter((name) => name !== vaultName));
    } else {
      setSelectedVaults([...selectedVaults, vaultName]);
    }
  };

  return (
    <aside style={styles.sidebar}>
      {/* Brand Header */}
      <div>
        <div style={styles.logo}>LocaL-iQ</div>
        <div style={styles.tagline}>Your knowledge, understood.</div>
      </div>

      <div style={styles.divider} />

      {/* Active Vault Section */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <div style={{ ...styles.sectionHeader, marginBottom: 0 }}>ACTIVE VAULT</div>
        <button
          onClick={onRescan}
          title="Rescan all vaults from disk immediately"
          style={styles.rescanBtn}
        >
          <svg style={{ width: 12, height: 12, fill: 'currentColor' }} viewBox="0 0 24 24">
            <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
          </svg>
          <span>Rescan</span>
        </button>
      </div>
      <div style={styles.vaultCard}>
        <select
          value={status.active_vault_path || ''}
          onChange={(e) => onSelectVault(e.target.value)}
          style={styles.selectInput}
        >
          {vaults.map((v) => (
            <option key={v.path} value={v.path}>
              {v.name}
            </option>
          ))}
        </select>

        <div style={styles.vaultStats}>
          <span style={styles.statItem}>
            <svg style={styles.iconSvg} viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
            <b style={{ color: '#FFFFFF' }}>{status.active_files || 0}</b> document
          </span>
          <span style={styles.statItem}>
            <svg style={styles.iconSvg} viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/></svg>
            <b style={{ color: '#FFFFFF' }}>{status.active_chunks || 0}</b> chunks
          </span>
        </div>

        <div style={styles.syncStatus}>
          <svg style={{ width: 14, height: 14, fill: '#00A896' }} viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
          <span>Synced {status.last_sync_time || 'just now'}</span>
        </div>
      </div>

      <div style={styles.divider} />

      {/* Search Scope Section with Multi-Vault Checkbox Selection */}
      <div style={styles.sectionHeader}>SEARCH SCOPE</div>
      <div style={styles.radioGroup}>
        {['Current Vault', 'Selected Vaults', 'All Vaults'].map((option) => (
          <label key={option} style={styles.radioLabel}>
            <input
              type="radio"
              name="search_scope"
              value={option}
              checked={vaultScope === option}
              onChange={(e) => setVaultScope(e.target.value)}
              style={styles.radioInput}
            />
            <span style={{ color: vaultScope === option ? '#FFFFFF' : '#8C9BAE', fontWeight: 500 }}>{option}</span>
          </label>
        ))}
      </div>

      {/* Multi-Select Vault Picker Box when 'Selected Vaults' is active */}
      {vaultScope === 'Selected Vaults' && (
        <div style={styles.multiSelectBox}>
          <div style={styles.multiSelectList}>
            {vaults.map((v) => {
              const isChecked = selectedVaults.includes(v.name);
              return (
                <label key={v.path} style={styles.checkboxItem}>
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => handleCheckboxToggle(v.name)}
                    style={styles.checkboxInput}
                  />
                  <span style={{ color: isChecked ? '#FFFFFF' : '#8C9BAE' }}>{v.name}</span>
                </label>
              );
            })}
          </div>
          <div style={styles.countBadge}>
            {selectedVaults.length} {selectedVaults.length === 1 ? 'vault' : 'vaults'} selected
          </div>
        </div>
      )}

      <div style={styles.divider} />

      {/* Navigation Section */}
      <div style={styles.sectionHeader}>NAVIGATION</div>
      <div style={styles.navList}>
        {[
          { id: 'ask', label: 'Ask', icon: 'M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z' },
          { id: 'kb', label: 'Knowledge Base', icon: 'M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z' },
          { id: 'inspector', label: 'Retrieval Inspector', icon: 'M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z' },
          { id: 'settings', label: 'Settings', icon: 'M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z' }
        ].map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                ...styles.navItem,
                ...(isActive ? styles.activeNavItem : {})
              }}
            >
              <svg style={{ width: 18, height: 18, fill: isActive ? '#00A896' : '#8C9BAE' }} viewBox="0 0 24 24">
                <path d={item.icon} />
              </svg>
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      <div style={{ flexGrow: 1 }} />

      {/* Footer Connected Card */}
      <div style={styles.footerCard}>
        <div style={styles.footerHeader}>
          <span style={styles.greenDot} />
          <span>Vault connected</span>
        </div>
        <div style={styles.footerDesc}>Everything is up to date</div>
      </div>
    </aside>
  );
}

const styles = {
  sidebar: {
    width: '280px',
    minWidth: '280px',
    backgroundColor: '#121722',
    borderRight: '1px solid #1E2638',
    padding: '24px 20px',
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    position: 'sticky',
    top: 0,
  },
  logo: {
    fontFamily: "'Newsreader', Georgia, serif",
    fontSize: '2.5rem',
    fontWeight: 500,
    color: '#FFFFFF',
    letterSpacing: '-0.01em',
    lineHeight: 1.05,
  },
  tagline: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.85rem',
    color: '#8C9BAE',
    marginTop: '4px',
  },
  divider: {
    height: '1px',
    backgroundColor: '#1E2638',
    margin: '18px 0',
  },
  sectionHeader: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.72rem',
    fontWeight: 700,
    color: '#64748B',
    letterSpacing: '0.08em',
    marginBottom: '10px',
  },
  rescanBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    backgroundColor: 'transparent',
    border: '1px solid #243048',
    borderRadius: '6px',
    color: '#00A896',
    fontSize: '0.72rem',
    fontWeight: 600,
    padding: '3px 8px',
    cursor: 'pointer',
    fontFamily: "'Roboto', sans-serif",
    transition: 'all 0.2s ease',
  },
  vaultCard: {
    backgroundColor: '#182030',
    border: '1px solid #243048',
    borderRadius: '10px',
    padding: '14px',
  },
  selectInput: {
    width: '100%',
    backgroundColor: '#121722',
    border: '1px solid #243048',
    borderRadius: '6px',
    color: '#FFFFFF',
    padding: '8px 12px',
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.95rem',
    fontWeight: 500,
    outline: 'none',
    marginBottom: '10px',
    cursor: 'pointer',
  },
  vaultStats: {
    display: 'flex',
    gap: '14px',
    fontSize: '0.84rem',
    color: '#8C9BAE',
    marginBottom: '8px',
    fontFamily: "'Roboto', sans-serif",
  },
  statItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  iconSvg: {
    width: '14px',
    height: '14px',
    fill: '#00A896',
  },
  syncStatus: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '0.78rem',
    color: '#64748B',
    fontFamily: "'Roboto', sans-serif",
  },
  radioGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  radioLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.9rem',
    cursor: 'pointer',
  },
  radioInput: {
    accentColor: '#00A896',
    cursor: 'pointer',
  },
  multiSelectBox: {
    marginTop: '10px',
    backgroundColor: '#182030',
    border: '1px solid #243048',
    borderRadius: '8px',
    padding: '10px',
  },
  multiSelectList: {
    maxHeight: '130px',
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  checkboxItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '0.86rem',
    fontFamily: "'Roboto', sans-serif",
    fontWeight: 500,
    cursor: 'pointer',
    padding: '4px 6px',
    borderRadius: '4px',
  },
  checkboxInput: {
    accentColor: '#00A896',
    cursor: 'pointer',
    width: '15px',
    height: '15px',
  },
  countBadge: {
    marginTop: '8px',
    paddingTop: '6px',
    borderTop: '1px solid #243048',
    fontSize: '0.76rem',
    color: '#00A896',
    fontWeight: 700,
    textAlign: 'right',
    fontFamily: "'Roboto', sans-serif",
  },
  navList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '10px 14px',
    borderRadius: '8px',
    backgroundColor: 'transparent',
    border: '1px solid transparent',
    color: '#8C9BAE',
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.92rem',
    fontWeight: 500,
    cursor: 'pointer',
    textAlign: 'left',
    transition: 'all 0.2s ease',
  },
  activeNavItem: {
    backgroundColor: '#182030',
    borderColor: '#00A896',
    color: '#FFFFFF',
    fontWeight: 700,
  },
  footerCard: {
    backgroundColor: '#182030',
    border: '1px solid #243048',
    borderRadius: '8px',
    padding: '12px 14px',
    marginTop: '20px',
  },
  footerHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.88rem',
    fontWeight: 700,
    color: '#FFFFFF',
  },
  greenDot: {
    width: '8px',
    height: '8px',
    backgroundColor: '#00A896',
    borderRadius: '50%',
    display: 'inline-block',
  },
  footerDesc: {
    fontSize: '0.78rem',
    color: '#8C9BAE',
    marginTop: '2px',
    fontFamily: "'Roboto', sans-serif",
  },
};
