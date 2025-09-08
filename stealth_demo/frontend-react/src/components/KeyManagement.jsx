import React, { useState, useCallback } from 'react';
import { Section, Button, DataList, Output } from './common';
import { useAppData } from '../hooks/useAppData';
import { useSchemeContext } from '../hooks/useSchemeContext';
import { apiService } from '../services/apiService';
import { truncateHex } from '../utils/helpers';
import { getKeyDetails, getLatestKeySummary } from '../utils/keyDisplay';

function KeyManagement() {
  const { currentScheme: scheme } = useSchemeContext();
  const { keys, addKey, loadKeys, loading: globalLoading, error: globalError, setError } = useAppData();
  const [selectedKeyIndex, setSelectedKeyIndex] = useState(-1);
  const [localLoading, setLocalLoading] = useState({});
  const [localError, setLocalError] = useState('');

  const handleGenerateKey = useCallback(async () => {
    try {
      setLocalLoading(prev => ({ ...prev, keygen: true }));
      setLocalError('');
      setError('');
      
      const newKey = await apiService.generateKey();
      addKey(newKey);
      
    } catch (err) {
      setLocalError(`${scheme.toUpperCase()} key generation failed: ${err.message}`);
    } finally {
      setLocalLoading(prev => ({ ...prev, keygen: false }));
    }
  }, [scheme, addKey, setError]);

  const handleRefreshKeys = useCallback(async () => {
    setLocalError('');
    setError('');
    await loadKeys();
  }, [loadKeys, setError]);

  const handleKeyClick = (index) => {
    setSelectedKeyIndex(index);
  };

  const getOutputContent = () => {
    const error = localError || globalError;
    if (error) {
      return `Error: ${error}`;
    }
    
    const filteredKeys = keys.filter(key => key.scheme === scheme);

    if (selectedKeyIndex >= 0 && keys[selectedKeyIndex]) {
      const selectedKey = keys[selectedKeyIndex];
      if (selectedKey.scheme === scheme) {
        return getKeyDetails(scheme, selectedKey, selectedKeyIndex);
      }
    }
    
    if (filteredKeys.length > 0) {
      const latestKey = filteredKeys[filteredKeys.length - 1];
      return getLatestKeySummary(scheme, latestKey);
    }
    
    return `Click \"Generate Key\" to create the first key for the ${scheme.toUpperCase()} scheme.`;
  };

  const keyItems = keys
    .filter(key => key.scheme === scheme)
    .map((key, index) => ({
      id: key.id,
      header: `${key.id} (${key.scheme.toUpperCase()})`,
      details: [
        `A: ${truncateHex(key.A_hex, 12)}`,
        `B: ${truncateHex(key.B_hex, 12)}`,
      ],
      selected: keys.indexOf(key) === selectedKeyIndex,
      onClick: () => handleKeyClick(keys.indexOf(key))
  }));

  return (
    <Section title={`🔑 Key Management (${scheme.toUpperCase()})`}>
      <div className="controls">
        <Button
          onClick={handleGenerateKey}
          loading={localLoading.keygen || globalLoading.keys}
          disabled={localLoading.keygen || globalLoading.keys}
        >
          Generate Key
        </Button>
        <Button
          onClick={handleRefreshKeys}
          variant="secondary"
        >
          Refresh Key List
        </Button>
      </div>
      
      <DataList items={keyItems} />
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  );
}

export default KeyManagement;
