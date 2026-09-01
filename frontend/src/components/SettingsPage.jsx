import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    top_k_final: 5,
    top_k_pool: 15,
    w_semantic: 0.70,
    w_lexical: 0.30,
    raw_cosine_threshold: 0.28,
    enable_query_expansion: false,
    persist_dir: './chroma_db',
    model_name: 'gemini-3.6-flash',
  });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/settings`)
      .then((res) => res.json())
      .then((data) => setSettings(data))
      .catch((err) => console.error('Error fetching settings:', err));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMsg('');
    try {
      const res = await fetch(`${API_BASE_URL}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
      const data = await res.json();
      setSettings(data);
      setMsg('Settings updated successfully.');
    } catch (err) {
      setMsg('Error saving settings.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Settings</h1>
      <div style={styles.subtitle}>
        Configure LocaL-iQ retrieval engine, parameters, and storage directory.
      </div>

      {msg && <div style={styles.alert}>{msg}</div>}

      <div style={styles.card}>
        <div style={styles.cardHeader}>RETRIEVAL ENGINE PARAMETERS</div>

        <div style={styles.fieldGroup}>
          <label style={styles.label}>
            Final Top-K Evidence Chunks: <b style={{ color: '#FFFFFF' }}>{settings.top_k_final}</b>
          </label>
          <input
            type="range"
            min={1}
            max={10}
            value={settings.top_k_final}
            onChange={(e) => setSettings({ ...settings, top_k_final: parseInt(e.target.value) })}
            style={styles.slider}
          />
        </div>

        <div style={styles.fieldGroup}>
          <label style={styles.label}>
            Initial Candidate Pool Size (Stage 1): <b style={{ color: '#FFFFFF' }}>{settings.top_k_pool}</b>
          </label>
          <input
            type="range"
            min={5}
            max={300}
            value={settings.top_k_pool}
            onChange={(e) => setSettings({ ...settings, top_k_pool: parseInt(e.target.value) })}
            style={styles.slider}
          />
        </div>

        <div style={styles.fieldGroup}>
          <label style={styles.label}>
            Semantic Weight (w_semantic): <b style={{ color: '#FFFFFF' }}>{settings.w_semantic}</b>
            &nbsp; (Lexical Weight: {roundTwo(1 - settings.w_semantic)})
          </label>
          <input
            type="range"
            min={0.0}
            max={1.0}
            step={0.05}
            value={settings.w_semantic}
            onChange={(e) =>
              setSettings({
                ...settings,
                w_semantic: parseFloat(e.target.value),
                w_lexical: roundTwo(1 - parseFloat(e.target.value)),
              })
            }
            style={styles.slider}
          />
        </div>

        <div style={styles.fieldGroup}>
          <label style={styles.label}>
            Absolute Raw Cosine Threshold: <b style={{ color: '#FFFFFF' }}>{settings.raw_cosine_threshold}</b>
          </label>
          <input
            type="range"
            min={0.0}
            max={0.8}
            step={0.02}
            value={settings.raw_cosine_threshold}
            onChange={(e) => setSettings({ ...settings, raw_cosine_threshold: parseFloat(e.target.value) })}
            style={styles.slider}
          />
        </div>

        <div style={styles.fieldGroup}>
          <label style={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={settings.enable_query_expansion}
              onChange={(e) => setSettings({ ...settings, enable_query_expansion: e.target.checked })}
              style={styles.checkbox}
            />
            Enable Experimental Query Expansion
          </label>
        </div>
      </div>

      <div style={styles.card}>
        <div style={styles.cardHeader}>STORAGE & VECTOR DATABASE</div>
        <div style={styles.fieldGroup}>
          <label style={styles.label}>ChromaDB Directory Path</label>
          <input
            type="text"
            value={settings.persist_dir}
            onChange={(e) => setSettings({ ...settings, persist_dir: e.target.value })}
            style={styles.textInput}
          />
        </div>
      </div>

      <button onClick={handleSave} disabled={saving} style={styles.saveButton}>
        {saving ? 'Saving...' : 'Save Settings'}
      </button>
    </div>
  );
}

function roundTwo(num) {
  return Math.round(num * 100) / 100;
}

const styles = {
  container: {
    maxWidth: '800px',
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
  alert: {
    backgroundColor: 'rgba(0, 168, 150, 0.12)',
    color: '#00A896',
    border: '1px solid #00A896',
    borderRadius: '8px',
    padding: '12px 16px',
    marginBottom: '20px',
    fontSize: '0.9rem',
    fontFamily: "'Roboto', sans-serif",
  },
  card: {
    backgroundColor: '#121722',
    border: '1px solid #1E2638',
    borderRadius: '12px',
    padding: '24px',
    marginBottom: '24px',
  },
  cardHeader: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.75rem',
    fontWeight: 700,
    color: '#64748B',
    letterSpacing: '0.08em',
    marginBottom: '20px',
  },
  fieldGroup: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.9rem',
    color: '#8C9BAE',
    marginBottom: '8px',
  },
  slider: {
    width: '100%',
    accentColor: '#00A896',
    cursor: 'pointer',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontFamily: "'Roboto', sans-serif",
    fontSize: '0.92rem',
    color: '#F0F4F8',
    cursor: 'pointer',
  },
  checkbox: {
    accentColor: '#00A896',
    cursor: 'pointer',
  },
  textInput: {
    width: '100%',
    backgroundColor: '#182030',
    border: '1px solid #243048',
    borderRadius: '8px',
    color: '#FFFFFF',
    padding: '10px 14px',
    fontSize: '0.95rem',
    fontFamily: "'JetBrains Mono', monospace",
    outline: 'none',
  },
  saveButton: {
    backgroundColor: '#00A896',
    border: 'none',
    borderRadius: '8px',
    color: '#FFFFFF',
    fontFamily: "'Roboto', sans-serif",
    padding: '12px 24px',
    fontSize: '0.95rem',
    fontWeight: 700,
    cursor: 'pointer',
  },
};
