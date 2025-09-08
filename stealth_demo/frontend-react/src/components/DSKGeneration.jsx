import React, { useState, useCallback, useEffect } from 'react';
import { Section, Button, Select, DataList, Output } from './common';
import { apiService } from '../services/apiService';
import { useAppData } from '../hooks/useAppData';
import { useSchemeContext } from '../hooks/useSchemeContext';
import { getDSKDetails, getLatestDSKSummary } from '../utils/dskDisplay';
import { truncateHex } from '../utils/helpers';

function DSKGeneration() {
  const { currentScheme: scheme } = useSchemeContext();
  const { 
    keys, 
    addresses,
    dsks,
    loading: globalLoading, 
    error: globalError, 
    clearError,
    loadKeys,
    loadAddresses,
    loadDSKs,
    addDsk
  } = useAppData();
  
  const [selectedKeyIndex, setSelectedKeyIndex] = useState('');
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('');
  const [selectedDSKIndex, setSelectedDSKIndex] = useState(-1);
  const [localLoading, setLocalLoading] = useState({});
  const [localError, setLocalError] = useState('');

  const handleRefreshData = useCallback(async () => {
    setLocalError('');
    clearError();
    await Promise.all([loadKeys(), loadAddresses(), loadDSKs()]);
  }, [loadKeys, loadAddresses, loadDSKs, clearError]);

  useEffect(() => {
    loadDSKs();
  }, [loadDSKs]);

  const notifyDSKUpdate = useCallback((newDSK) => {
    window.dispatchEvent(new CustomEvent('dskUpdated', { 
      detail: { newDSK, allDSKs: [...dsks, newDSK] }
    }));
  }, [dsks]);

  const handleGenerateDSK = useCallback(async () => {
    if (selectedAddrIndex === '' || selectedKeyIndex === '') {
      setLocalError('Please select both an address and a key!');
      return;
    }

    try {
      setLocalLoading(prev => ({ ...prev, generating: true }));
      setLocalError('');
      clearError();
      
      const newDSK = await apiService.generateDSK(
        parseInt(selectedAddrIndex), 
        parseInt(selectedKeyIndex)
      );
      
      addDsk(newDSK);
      notifyDSKUpdate(newDSK);
      
    } catch (err) {
      setLocalError(`${scheme.toUpperCase()} DSK generation failed: ${err.message}`);
    } finally {
      setLocalLoading(prev => ({ ...prev, generating: false }));
    }
  }, [selectedAddrIndex, selectedKeyIndex, clearError, notifyDSKUpdate, scheme]);

  const handleDSKClick = useCallback((index) => {
    setSelectedDSKIndex(index);
  }, []);

  const getOutputContent = () => {
    const error = localError || globalError;
    if (error) {
      return `Error: ${error}`;
    }
    
    const filteredDsks = dsks.filter(dsk => dsk.scheme === scheme);

    if (selectedDSKIndex >= 0 && dsks[selectedDSKIndex]) {
        const selectedDsk = dsks[selectedDSKIndex];
        if (selectedDsk.scheme === scheme) {
            return getDSKDetails(scheme, selectedDsk, selectedDSKIndex);
        }
    }
    
    if (filteredDsks.length > 0) {
      const latestDSK = filteredDsks[filteredDsks.length - 1];
      return getLatestDSKSummary(scheme, latestDSK);
    }
    
    return `Select an address and key to generate a new ${scheme.toUpperCase()} DSK.`;
  };

  const dskItems = dsks
    .filter(dsk => dsk.scheme === scheme)
    .map((dsk, index) => ({
      id: dsk.id,
      header: `${dsk.id} (Address: ${dsk.address_id})`,
      details: [
        `DSK: ${truncateHex(dsk.dsk_hex, 12)}`,
        `Key: ${dsk.key_id}`,
        `Scheme: ${dsk.scheme}`
      ],
      selected: dsks.indexOf(dsk) === selectedDSKIndex,
      onClick: () => handleDSKClick(dsks.indexOf(dsk))
  }));

  const filteredAddresses = addresses.filter(addr => addr.scheme === scheme);

  return (
    <Section title={`🔐 DSK Generation (${scheme.toUpperCase()})`}>
      <div className="controls">
        <label>Select Address:</label>
        <Select
          value={selectedAddrIndex}
          onChange={(e) => setSelectedAddrIndex(e.target.value)}
          disabled={globalLoading.all}
        >
          <option value="">Select address...</option>
          {filteredAddresses.map((addr, index) => (
            <option key={addr.id} value={addresses.indexOf(addr)}>
              {addr.id} - {truncateHex(addr.addr_hex, 12)}
            </option>
          ))}
        </Select>
        
        <label>Select Key:</label>
        <Select
          value={selectedKeyIndex}
          onChange={(e) => setSelectedKeyIndex(e.target.value)}
          disabled={globalLoading.all}
        >
          <option value="">Select key...</option>
          {keys.map((key, index) => (
            <option key={key.id} value={index}>
              {key.id} - A: {truncateHex(key.A_hex, 8)}
            </option>
          ))}
        </Select>
        
        <div className="inline-controls">
          <Button
            onClick={handleGenerateDSK}
            loading={localLoading.generating}
            disabled={selectedAddrIndex === '' || selectedKeyIndex === '' || localLoading.generating}
          >
            Generate DSK
          </Button>
          
          <Button
            onClick={handleRefreshData}
            variant="secondary"
            disabled={globalLoading.all}
          >
            Refresh Data
          </Button>
        </div>
      </div>
      
      <DataList items={dskItems} />
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  );
}

export default DSKGeneration;
