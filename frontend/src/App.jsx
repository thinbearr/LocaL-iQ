import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import TopHeader from './components/TopHeader';
import AskPage from './components/AskPage';
import KnowledgeBasePage from './components/KnowledgeBasePage';
import RetrievalInspectorPage from './components/RetrievalInspectorPage';
import SettingsPage from './components/SettingsPage';
import { API_BASE_URL } from './config';

export default function App() {
  const [activeTab, setActiveTab] = useState('ask');
  const [vaultScope, setVaultScope] = useState('Current Vault');
  const [selectedVaults, setSelectedVaults] = useState([]);
  const [status, setStatus] = useState({});
  const [vaults, setVaults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [answerData, setAnswerData] = useState(null);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/status`);
      const data = await res.json();
      setStatus(data);
      if (data.active_vault_name && selectedVaults.length === 0) {
        setSelectedVaults([data.active_vault_name]);
      }
    } catch (e) {
      console.error('Error fetching status:', e);
    }
  };

  const fetchVaults = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/vaults`);
      const data = await res.json();
      setVaults(data.vaults || []);
      if (data.vaults && data.vaults.length > 0 && selectedVaults.length === 0) {
        setSelectedVaults(data.vaults.map((v) => v.name));
      }
    } catch (e) {
      console.error('Error fetching vaults:', e);
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchVaults();
  }, []);

  const handleSelectVault = async (vaultPath) => {
    try {
      await fetch(`${API_BASE_URL}/api/vaults/select`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vault_path: vaultPath }),
      });
      fetchStatus();
      fetchVaults();
    } catch (e) {
      console.error('Error selecting vault:', e);
    }
  };

  const handleRescan = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/vaults/rescan`, { method: 'POST' });
      const data = await res.json();
      setVaults(data.vaults || []);
      fetchStatus();
    } catch (e) {
      console.error('Error rescanning vaults:', e);
    }
  };

  const handleSync = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/vaults/sync`, { method: 'POST' });
      fetchStatus();
    } catch (e) {
      console.error('Error syncing vault:', e);
    }
  };

  const handleAsk = async (queryText) => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryText,
          vault_scope: vaultScope,
          selected_vaults: selectedVaults,
        }),
      });
      const data = await res.json();
      setAnswerData(data);
    } catch (e) {
      console.error('Error asking question:', e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.appContainer}>
      <Sidebar
        status={status}
        vaults={vaults}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        vaultScope={vaultScope}
        setVaultScope={setVaultScope}
        selectedVaults={selectedVaults}
        setSelectedVaults={setSelectedVaults}
        onSelectVault={handleSelectVault}
        onRescan={handleRescan}
      />

      <main style={styles.mainContent}>
        <TopHeader
          status={status}
          vaultScope={vaultScope}
          selectedVaults={selectedVaults}
        />

        <div style={styles.contentArea}>
          {activeTab === 'ask' && (
            <AskPage
              status={status}
              onAsk={handleAsk}
              isLoading={isLoading}
              answerData={answerData}
            />
          )}

          {activeTab === 'kb' && (
            <KnowledgeBasePage
              status={status}
              vaults={vaults}
              vaultScope={vaultScope}
              selectedVaults={selectedVaults}
              onSelectVault={handleSelectVault}
              onRescan={handleRescan}
              onSync={handleSync}
            />
          )}

          {activeTab === 'inspector' && (
            <RetrievalInspectorPage answerData={answerData} />
          )}

          {activeTab === 'settings' && <SettingsPage />}
        </div>
      </main>
    </div>
  );
}

const styles = {
  appContainer: {
    display: 'flex',
    minHeight: '100vh',
    backgroundColor: '#0B0E14',
  },
  mainContent: {
    flexGrow: 1,
    padding: '24px 36px',
    overflowY: 'auto',
    maxHeight: '100vh',
  },
  contentArea: {
    maxWidth: '1100px',
    margin: '0 auto',
  },
};
