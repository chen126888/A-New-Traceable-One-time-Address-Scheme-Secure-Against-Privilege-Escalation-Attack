import React, { useState, useCallback } from 'react';
import { Section, Button, Select, Output } from './common';
import { apiService } from '../services/apiService';
import { useAppData } from '../hooks/useAppData';
import { useSchemeContext } from '../hooks/useSchemeContext';
import { getRecognitionResultDetails } from '../utils/recognitionDisplay';
import { truncateHex } from '../utils/helpers';

function AddressRecognition() {
  const { currentScheme: scheme } = useSchemeContext();
  const { keys, addresses, loadAllData, loading: globalLoading, error: globalError, setError } = useAppData();
  
  const [selectedKeyIndex, setSelectedKeyIndex] = useState('');
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('');
  const [recognitionMethod, setRecognitionMethod] = useState('fast');
  const [localLoading, setLocalLoading] = useState({});
  const [localError, setLocalError] = useState('');
  const [recognitionResult, setRecognitionResult] = useState(null);

  const handleRefreshData = useCallback(async () => {
    setLocalError('');
    setError('');
    setRecognitionResult(null);
    await loadAllData();
  }, [loadAllData, setError]);

  const handleRecognizeAddress = useCallback(async () => {
    if (selectedAddrIndex === '' || selectedKeyIndex === '') {
      setLocalError('Please select both an address and a key!');
      return;
    }

    try {
      setLocalLoading(prev => ({ ...prev, recognizing: true }));
      setLocalError('');
      setError('');
      
      const result = await apiService.recognizeAddress(
        parseInt(selectedAddrIndex),
        parseInt(selectedKeyIndex),
        recognitionMethod === 'fast'
      );
      
      setRecognitionResult(result);
      
    } catch (err) {
      setLocalError(`${scheme.toUpperCase()} address recognition failed: ${err.message}`);
    } finally {
      setLocalLoading(prev => ({ ...prev, recognizing: false }));
    }
  }, [selectedAddrIndex, selectedKeyIndex, recognitionMethod, scheme, setError]);

  const getOutputContent = () => {
    const error = localError || globalError;
    if (error) {
      return `Error: ${error}`;
    }
    
    if (recognitionResult) {
      const selectedAddr = addresses[parseInt(selectedAddrIndex)];
      const selectedKey = keys[parseInt(selectedKeyIndex)];
      return getRecognitionResultDetails(scheme, recognitionResult, selectedAddr, selectedKey);
    }
    
    return 'Select an address, a key, and a method, then click \'Recognize Address\'.';
  };

  const filteredAddresses = addresses.filter(addr => addr.scheme === scheme);

  return (
    <Section title={`🔍 Address Recognition (${scheme.toUpperCase()})`}>
      <div className="controls">
        <label>Select Address to Recognize:</label>
        <Select
          value={selectedAddrIndex}
          onChange={(e) => setSelectedAddrIndex(e.target.value)}
          disabled={globalLoading.all}
        >
          <option value="">
            {globalLoading.all ? 'Loading addresses...' : 'Select address...'}
          </option>
          {filteredAddresses.map((addr, index) => (
            <option key={addr.id} value={addresses.indexOf(addr)}> 
              {addr.id} - {truncateHex(addr.addr_hex, 12)}
            </option>
          ))}
        </Select>
        
        <label>Select Key for Recognition:</label>
        <Select
          value={selectedKeyIndex}
          onChange={(e) => setSelectedKeyIndex(e.target.value)}
          disabled={globalLoading.all}
        >
          <option value="">
            {globalLoading.all ? 'Loading keys...' : 'Select key...'}
          </option>
          {keys.map((key, index) => (
            <option key={key.id} value={index}>
              {key.id} - A: {truncateHex(key.A_hex, 8)}
            </option>
          ))}
        </Select>
        
        <label>Recognition Method:</label>
        <Select
          value={recognitionMethod}
          onChange={(e) => setRecognitionMethod(e.target.value)}
          disabled={globalLoading.all}
        >
          <option value="fast">Fast Recognition</option>
          <option value="full">Full Recognition</option>
        </Select>
        
        <div className="inline-controls">
          <Button
            onClick={handleRecognizeAddress}
            loading={localLoading.recognizing}
            disabled={selectedAddrIndex === '' || selectedKeyIndex === '' || localLoading.recognizing}
          >
            Recognize Address
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
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  );
}

export default AddressRecognition;
