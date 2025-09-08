import React, { useState, useCallback } from 'react';
import { Button } from '../../components/common';
import BaseIdentityTracing from '../../components/BaseIdentityTracing';
import { apiService } from '../../services/apiService';
import { useAppData } from '../../hooks/useAppData';
import { truncateHex } from '../../utils/helpers';

function SitaibaIdentityTracing() {
  const { 
    addresses, 
    loading: globalLoading, 
    error: globalError, 
    clearError,
    loadKeys,
    loadAddresses
  } = useAppData();
  
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('');
  const [selectedTraceIndex, setSelectedTraceIndex] = useState(-1);
  const [traceResults, setTraceResults] = useState([]);
  const [localLoading, setLocalLoading] = useState({});
  const [localError, setLocalError] = useState('');

  const handleRefreshData = useCallback(async () => {
    setLocalError('');
    clearError();
    await Promise.all([loadKeys(), loadAddresses()]);
  }, [loadKeys, loadAddresses, clearError]);

  const handleTraceIdentity = useCallback(async () => {
    if (selectedAddrIndex === '') {
      setLocalError('Please select an address to trace!');
      return;
    }
    try {
      setLocalLoading(prev => ({ ...prev, tracing: true }));
      setLocalError('');
      clearError();
      const result = await apiService.traceIdentity(parseInt(selectedAddrIndex));
      setTraceResults(prev => [...prev, result]);
    } catch (err) {
      setLocalError('SITAIBA identity tracing failed: ' + err.message);
    } finally {
      setLocalLoading(prev => ({ ...prev, tracing: false }));
    }
  }, [selectedAddrIndex, clearError]);

  const handleTraceClick = useCallback((index) => {
    setSelectedTraceIndex(index);
  }, []);

  const getOutputContent = () => {
    const error = localError || globalError;
    if (error) return `Error: ${error}`;

    if (selectedTraceIndex >= 0 && traceResults[selectedTraceIndex]) {
      const trace = traceResults[selectedTraceIndex];
      return `🔍 SITAIBA Identity Tracing Result - Result ${selectedTraceIndex + 1}
📧 Traced Address: ${trace.address_id} (Index: ${trace.address_index})
🎯 Scheme: ${trace.scheme || 'sitaiba'}
📊 Status: ${trace.status}

🔍 Recovered Identity (Public Key B):
${trace.recovered_b_hex}

📋 Original Owner Information:
• Key Index: ${trace.original_owner.key_index}
• Key ID: ${trace.original_owner.key_id}
• Original B Value: ${trace.original_owner.B_hex}

🎯 Match Result:
${trace.perfect_match ? '✅ Perfect match found!' : '❌ No matching key found'}

${trace.matched_key ? `🔑 Matched Key:
• Index: ${trace.matched_key.index}
• ID: ${trace.matched_key.id}
• A: ${truncateHex(trace.matched_key.A_hex)}
• B: ${truncateHex(trace.matched_key.B_hex)}
• Match Type: ${trace.matched_key.match_type}` : ''}

💡 SITAIBA Tracing Features:
• Uses tracking key to recover address owner's public key B
• No C parameter required (unlike Stealth)
• Precisely identifies address creator
• Supports complete identity verification`;
    }

    if (traceResults.length > 0) {
      const latestTrace = traceResults[traceResults.length - 1];
      return `✅ SITAIBA Identity Tracing Completed!
📧 Traced Address: ${latestTrace.address_id}
🎯 Scheme: SITAIBA
🔍 Recovered Public Key: ${truncateHex(latestTrace.recovered_b_hex)}
🎯 Match Status: ${latestTrace.perfect_match ? '✅ Perfect Match' : '❌ No Match'}

${latestTrace.matched_key ? `🔑 Matched Key: ${latestTrace.matched_key.id}` : '❓ No corresponding key found'}`;
    }
    return 'Select an address to trace its identity...';
  };

  const traceItems = traceResults.map((trace, index) => ({
    id: `trace_${index}`,
    header: `Trace ${index + 1}: ${trace.address_id}`,
    details: [
      `Recovered: ${truncateHex(trace.recovered_b_hex, 12)}`,
      `Match: ${trace.perfect_match ? '✅ Yes' : '❌ No'}`,
      `Scheme: ${trace.scheme || 'sitaiba'}`
    ],
    selected: index === selectedTraceIndex,
    onClick: () => handleTraceClick(index)
  }));

  return (
    <BaseIdentityTracing
      title="🔍 Identity Tracing (SITAIBA)"
      selectedAddrIndex={selectedAddrIndex}
      onAddressChange={(e) => setSelectedAddrIndex(e.target.value)}
      addresses={addresses}
      items={traceItems}
      outputContent={getOutputContent()}
      isError={!!(localError || globalError)}
      globalLoading={globalLoading}
    >
      <div className="inline-controls">
        <Button
          onClick={handleTraceIdentity}
          loading={localLoading.tracing}
          disabled={selectedAddrIndex === '' || localLoading.tracing}
        >
          Execute SITAIBA Identity Tracing
        </Button>
        <Button
          onClick={handleRefreshData}
          variant="secondary"
          disabled={globalLoading.all}
        >
          Refresh Data
        </Button>
      </div>
    </BaseIdentityTracing>
  );
}

export default SitaibaIdentityTracing;
