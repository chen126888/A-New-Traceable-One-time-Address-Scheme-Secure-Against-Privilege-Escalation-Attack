import React, { useState, useEffect, useCallback } from 'react';
import { Section, Button, Select, Output } from './common/index.jsx';
import { apiService } from '../services/apiService';
import { useAppData } from '../hooks/useAppData';
import { useSchemeContext } from '../hooks/useSchemeContext';
import { getSystemSetupDetails } from '../utils/systemDisplay';

function SystemSetup() {
  const { loadAllData, resetData } = useAppData();
  const { currentScheme: scheme } = useSchemeContext();

  const [paramFiles, setParamFiles] = useState([]);
  const [selectedParam, setSelectedParam] = useState('');
  const [loading, setLoading] = useState({});
  const [error, setError] = useState('');
  const [setupComplete, setSetupComplete] = useState(false);
  const [traceKey, setTraceKey] = useState(null);

  const loadParamFiles = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, paramFiles: true }));
      const data = await apiService.getParamFiles();
      setParamFiles(data.param_files);
      if (data.current) {
        setSelectedParam(data.current);
      }
    } catch (err) {
      setError('Failed to load parameter files: ' + err.message);
    } finally {
      setLoading(prev => ({ ...prev, paramFiles: false }));
    }
  }, []);

  useEffect(() => {
    // When the scheme changes, reset the setup status and reload param files.
    setSetupComplete(false);
    setTraceKey(null);
    setError('');
    loadParamFiles();
  }, [scheme, loadParamFiles]);

  const handleSetup = useCallback(async () => {
    if (!selectedParam) {
      setError('Please select a parameter file');
      return;
    }
    try {
      setLoading(prev => ({ ...prev, setup: true }));
      setError('');
      const data = await apiService.setup(selectedParam);
      setTraceKey(data);
      setSetupComplete(true);
      await loadAllData();
    } catch (err) {
      setError('Setup failed: ' + err.message);
    } finally {
      setLoading(prev => ({ ...prev, setup: false }));
    }
  }, [selectedParam, loadAllData]);

  const handleReset = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, reset: true }));
      setError('');
      await resetData();
      setSetupComplete(false);
      setTraceKey(null);
    } catch (err) {
      setError('Reset failed: ' + err.message);
    } finally {
      setLoading(prev => ({ ...prev, reset: false }));
    }
  }, [resetData]);

  const getOutputContent = () => {
    if (error) {
      return `Error: ${error}`;
    }
    if (setupComplete && traceKey) {
      return getSystemSetupDetails(scheme, traceKey, selectedParam);
    }
    return `Select a parameter file to initialize the ${scheme.toUpperCase()} system.`;
  };

  return (
    <Section 
      title={`🔧 System Setup (${scheme.toUpperCase()})`} 
      statusActive={setupComplete}
    >
      <div className="controls">
        <label>Select Parameter File:</label>
        <Select
          value={selectedParam}
          onChange={(e) => setSelectedParam(e.target.value)}
          disabled={loading.paramFiles}
        >
          <option value="">
            {loading.paramFiles ? 'Loading...' : 'Select Parameter File...'}
          </option>
          {paramFiles.map((file) => (
            <option key={file.name} value={file.name}>
              {file.name} ({file.size} bytes)
            </option>
          ))}
        </Select>
        
        <div className="inline-controls">
          <Button
            onClick={handleSetup}
            loading={loading.setup}
            disabled={!selectedParam || loading.setup}
          >
            Initialize System
          </Button>
          
          {scheme === 'sitaiba' && (
            <Button
              onClick={handleReset}
              variant="secondary"
              loading={loading.reset}
              disabled={loading.reset}
            >
              Reset System
            </Button>
          )}
        </div>
      </div>
      
      <Output 
        content={getOutputContent()}
        isError={!!error}
      />
    </Section>
  );
}

export default SystemSetup;
