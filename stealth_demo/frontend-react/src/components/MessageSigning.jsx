import React, { useState, useCallback, useEffect } from 'react';
import { Section, Button, Select, Input, DataList, Output } from './common';
import { apiService } from '../services/apiService';
import { useAppData } from '../hooks/useAppData'; // Import useAppData
import { useSchemeContext } from '../hooks/useSchemeContext';
import { truncateHex } from '../utils/helpers';

// A simple placeholder for non-signing schemes
function SchemeNotSupported() {
  return (
    <Section title="✍️ Message Signing" className="disabled">
      <div style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>
        <span style={{ fontSize: '2rem', marginBottom: '1rem' }}>🚫</span>
        <p>The current scheme does not support message signing.</p>
        <p>Please switch to the <strong>Stealth</strong> scheme to use this feature.</p>
      </div>
    </Section>
  );
}

function MessageSigning() {
  const { currentScheme: scheme, supportsSigning } = useSchemeContext(); // Get supportsSigning
  const { 
    addresses, 
    dsks, // Use dsks from useAppData
    txMessages, // Use txMessages from useAppData
    loading: globalLoading, 
    error: globalError,
    clearError,
    loadAllData, // Use loadAllData for refresh
    addTxMessage // Use addTxMessage for new signatures
  } = useAppData();
  
  const [message, setMessage] = useState('Hello, this is a test message!');
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('');
  const [selectedDSKIndex, setSelectedDSKIndex] = useState('');
  const [selectedSigIndex, setSelectedSigIndex] = useState(-1); // Still local for display selection
  const [localLoading, setLocalLoading] = useState({});
  const [localError, setLocalError] = useState('');

  // Initial data load when component mounts or scheme changes
  useEffect(() => {
    if (supportsSigning) { // Only load if signing is supported by the scheme
      loadAllData(); // Load all data including keys, addresses, DSKs, and txMessages
    }
  }, [scheme, supportsSigning, loadAllData]); // Depend on scheme and loadAllData

  const handleRefreshData = useCallback(async () => {
    console.log('MessageSigning: Refresh Data button clicked, calling loadAllData...'); // Debug log
    setLocalError('');
    clearError();
    await loadAllData(); // Load all data from backend
  }, [loadAllData, clearError]);

  const handleSignMessage = useCallback(async () => {
    if (!message.trim() || selectedAddrIndex === '' || selectedDSKIndex === '') {
      setLocalError('Please enter a message and select an address and DSK!');
      return;
    }

    try {
      setLocalLoading(prev => ({ ...prev, signing: true }));
      setLocalError('');
      clearError();
      
      const signature = await apiService.post('/sign_with_address_dsk', {
        message: message,
        address_index: parseInt(selectedAddrIndex),
        dsk_index: parseInt(selectedDSKIndex)
      });
      
      // Add the new signature to the global txMessages state
      addTxMessage(signature); 
      
      // Optionally, you might want to select the newly added signature for immediate display
      // setSelectedSigIndex(txMessages.length); // This might be tricky due to async state update
      
    } catch (err) {
      setLocalError('Message signing failed: ' + err.message);
    } finally {
      setLocalLoading(prev => ({ ...prev, signing: false }));
    }
  }, [message, selectedDSKIndex, selectedAddrIndex, clearError, addTxMessage]); // Add addTxMessage to dependencies

  const handleSignatureClick = useCallback((index) => {
    setSelectedSigIndex(index);
  }, []);

  const getOutputContent = () => {
    const error = localError || globalError;
    if (error) return `Error: ${error}`;

    if (selectedSigIndex >= 0 && txMessages[selectedSigIndex]) { // Use txMessages
      const sig = txMessages[selectedSigIndex];
      return `🔍 Signature Details - Index ${selectedSigIndex}\n📝 Message: "${sig.message}"\n🛠️ Signing Method: ${sig.method}\n📧 Address: ${sig.address_id || 'N/A'}\n🔑 Key: ${sig.key_id || 'N/A'}\n🔐 DSK: ${sig.dsk_id || 'N/A'}\n📊 Status: ${sig.status}\n\n✍️ Signature Components:\nQ_sigma (G1):\n${sig.q_sigma_hex}\n\nH (Zr):\n${sig.h_hex}`;
    }
    
    if (txMessages.length > 0) { // Use txMessages
      const latestSig = txMessages[txMessages.length - 1];
      return `✅ Message Signed Successfully!\n📝 Message: "${latestSig.message}"\n✍️ Q_sigma: ${truncateHex(latestSig.q_sigma_hex)}\n🔢 H: ${truncateHex(latestSig.h_hex)}`;
    }
    
    return 'Enter a message and select the corresponding address and DSK to create a signature.';
  };

  const filteredAddresses = addresses.filter(addr => addr.scheme === scheme);
  const filteredDsks = dsks.filter(dsk => dsk.scheme === scheme); // Filter dsks from useAppData

  if (!supportsSigning) { // Use supportsSigning from context
    return <SchemeNotSupported />;
  }

  return (
    <Section title="✍️ Message Signing (Stealth)">
      <div className="controls">
        <label>Message to Sign:</label>
        <Input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Enter your message here..." />
        
        <label>Select Address to Sign With:</label>
        <Select value={selectedAddrIndex} onChange={(e) => setSelectedAddrIndex(e.target.value)}>
          <option value="">Select an address...</option>
          {filteredAddresses.map((addr, index) => (
            <option key={addr.id} value={addresses.indexOf(addr)}>
              {addr.id} - {truncateHex(addr.addr_hex, 12)}
            </option>
          ))}
        </Select>
        
        <label>Select DSK to Use:</label>
        <Select value={selectedDSKIndex} onChange={(e) => setSelectedDSKIndex(e.target.value)}>
          <option value="">{filteredDsks.length === 0 ? 'No DSKs available' : 'Select a DSK...'}</option>
          {filteredDsks.map((dsk, index) => (
            <option key={dsk.id} value={dsks.indexOf(dsk)}>
              {dsk.id} - For: {dsk.address_id}
            </option>
          ))}
        </Select>
        
        <div className="inline-controls">
          <Button onClick={handleSignMessage} loading={localLoading.signing} disabled={localLoading.signing || !message.trim() || !selectedAddrIndex || !selectedDSKIndex}>
            Sign Message
          </Button>
          <Button onClick={handleRefreshData} variant="secondary">
            Refresh Data
          </Button>
        </div>
      </div>
      
      <DataList items={txMessages.map((sig, index) => ({
        id: `sig_${index}`,
        header: `Signature ${index}`,
        details: [`Message: "${sig.message.substring(0, 20)}..."`, `Q_sigma: ${truncateHex(sig.q_sigma_hex, 12)}`],
        selected: index === selectedSigIndex,
        onClick: () => handleSignatureClick(index)
      }))} />
      
      <Output content={getOutputContent()} isError={!!(localError || globalError)} />
    </Section>
  );
}

export default MessageSigning;
