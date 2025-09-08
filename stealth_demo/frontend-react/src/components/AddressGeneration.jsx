import React, { useState, useCallback } from 'react';
import { Section, Button, Select, DataList, Output } from './common'; // Adjusted path
import { apiService } from '../services/apiService';
import { useAppData } from '../hooks/useAppData';
import { useSchemeContext } from '../hooks/useSchemeContext'; // Import scheme context
import { getAddressDisplayDetails, getLatestAddressSummary } from '../utils/addressDisplay'; // Import new helpers
import { truncateHex } from '../utils/helpers';

function AddressGeneration() {
  const { currentScheme: scheme } = useSchemeContext(); // Get current scheme

  
  const { 
    keys, 
    addresses, 
    addAddress, 
    loadKeys, 
    loading: globalLoading, 
    error: globalError, 
    clearError 
  } = useAppData();
  
  const [selectedKeyIndex, setSelectedKeyIndex] = useState('');
  const [selectedAddrIndex, setSelectedAddrIndex] = useState(-1);
  const [localLoading, setLocalLoading] = useState({});
  const [localError, setLocalError] = useState('');

  const handleRefreshKeys = useCallback(async () => {
    setLocalError('');
    clearError();
    await loadKeys();
  }, [loadKeys, clearError]);

  const handleGenerateAddress = useCallback(async () => {
    if (selectedKeyIndex === '') {
      setLocalError('Please select a key!');
      return;
    }

    try {
      setLocalLoading(prev => ({ ...prev, addrgen: true }));
      setLocalError('');
      clearError();
      
      const newAddress = await apiService.generateAddress(parseInt(selectedKeyIndex));
      addAddress(newAddress);
      
    } catch (err) {
      setLocalError(`${scheme.toUpperCase()} address generation failed: ${err.message}`);
    } finally {
      setLocalLoading(prev => ({ ...prev, addrgen: false }));
    }
  }, [selectedKeyIndex, addAddress, clearError, scheme]);

  const handleAddressClick = useCallback((index) => {
    setSelectedAddrIndex(index);
  }, []);

  const getOutputContent = () => {
    const error = localError || globalError;
    if (error) {
      return `Error: ${error}`;
    }
    
    if (selectedAddrIndex >= 0 && addresses[selectedAddrIndex]) {
      return getAddressDisplayDetails(scheme, addresses[selectedAddrIndex]);
    }
    
    if (addresses.length > 0) {
      const latestAddr = addresses[addresses.length - 1];
      // Ensure the latest address matches the current scheme before showing summary
      if (latestAddr.scheme === scheme) {
        return getLatestAddressSummary(scheme, latestAddr);
      }
    }
    
    return `Select a key and click 'Generate Address' to create a new ${scheme.toUpperCase()} address.`;
  };

  const addressItems = addresses
    .filter(addr => addr.scheme === scheme) // Filter addresses by scheme
    .map((addr, index) => ({
      id: addr.id,
      header: `${addr.id} (Owner: ${addr.key_id})`,
      details: [
        `${truncateHex(addr.addr_hex, 20)}`,
        `Scheme: ${addr.scheme}`
      ],
      selected: addresses.indexOf(addr) === selectedAddrIndex,
      onClick: () => handleAddressClick(addresses.indexOf(addr))
  }));

  return (
    <Section title={`📧 Address Generation (${scheme.toUpperCase()})`}>
      <div className="controls">
        <label>Select Key for Address Generation:</label>
        <Select
          value={selectedKeyIndex}
          onChange={(e) => setSelectedKeyIndex(e.target.value)}
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
            onClick={handleGenerateAddress}
            loading={localLoading.addrgen}
            disabled={selectedKeyIndex === '' || localLoading.addrgen}
          >
            Generate Address
          </Button>
          
          <Button
            onClick={handleRefreshKeys}
            variant="secondary"
          >
            Refresh Keys
          </Button>
        </div>
      </div>
      
      <DataList items={addressItems} />
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  );
}

export default AddressGeneration;
