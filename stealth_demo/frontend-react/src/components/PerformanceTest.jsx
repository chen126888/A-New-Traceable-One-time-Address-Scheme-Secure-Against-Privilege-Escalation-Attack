import React, { useState, useCallback } from 'react';
import { Section, Button, Input, Output } from './common';
import { apiService } from '../services/apiService';
import { useAppData } from '../hooks/useAppData';
import { useSchemeContext } from '../hooks/useSchemeContext';
import { getPerformanceTestDetails } from '../utils/performanceDisplay';

function PerformanceTest() {
  const { currentScheme: scheme } = useSchemeContext();
  const { loading: globalLoading, error: globalError, clearError } = useAppData();
  
  const [iterations, setIterations] = useState(100);
  const [testResults, setTestResults] = useState([]);
  const [selectedResultIndex, setSelectedResultIndex] = useState(-1);
  const [localLoading, setLocalLoading] = useState({});
  const [localError, setLocalError] = useState('');

  const handleRunPerformanceTest = useCallback(async (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (iterations < 1 || iterations > 1000) {
      setLocalError('Iteration count must be between 1 and 1000!');
      return;
    }
    try {
      setLocalLoading(prev => ({ ...prev, testing: true }));
      setLocalError('');
      clearError();
      
      const startTime = Date.now();
      const result = await apiService.performanceTest(iterations);
      const endTime = Date.now();
      
      const testWithMetadata = {
        ...result,
        test_index: testResults.length,
        timestamp: new Date().toISOString(),
        total_test_time: endTime - startTime,
        avg_per_iteration: (endTime - startTime) / iterations
      };
      
      setTestResults(prev => [...prev, testWithMetadata]);
      setSelectedResultIndex(testResults.length);
      
    } catch (err) {
      setLocalError(`${scheme.toUpperCase()} performance test failed: ${err.message}`);
    } finally {
      setLocalLoading(prev => ({ ...prev, testing: false }));
    }
  }, [iterations, testResults.length, clearError, scheme]);

  const handleClearResults = useCallback((e) => {
    if (e) e.preventDefault();
    setTestResults([]);
    setSelectedResultIndex(-1);
    setLocalError('');
  }, []);

  const handleSelectResult = useCallback((index) => {
    setSelectedResultIndex(index);
  }, []);

  const handleIterationChange = useCallback((e) => {
    const value = parseInt(e.target.value) || 100;
    setIterations(Math.min(Math.max(value, 1), 1000));
  }, []);

  const handlePresetClick = useCallback((value, e) => {
    if (e) e.preventDefault();
    setIterations(value);
  }, []);

  const getOperationMetrics = (scheme) => {
    if (scheme === 'sitaiba') {
      return [
        { key: 'addr_gen_ms', label: 'Address Generation' },
        { key: 'fast_recognize_ms', label: 'Fast Recognition' },
        { key: 'onetime_sk_ms', label: 'DSK Generation' },
        { key: 'trace_ms', label: 'Identity Tracing' },
        { key: 'total_test_time', label: 'Total Time' },
        { key: 'unsupported', label: 'Signing Features', value: 'Not Supported' },
      ];
    }
    // Default to stealth
    return [
      { key: 'addr_gen_ms', label: 'Address Generation' },
      { key: 'fast_recognize_ms', label: 'Fast Recognition' },
      { key: 'sign_ms', label: 'Signing' },
      { key: 'sig_verify_ms', label: 'Signature Verification' },
      { key: 'trace_ms', label: 'Identity Tracing' },
      { key: 'total_test_time', label: 'Total Time' },
    ];
  };

  const getSchemeOperations = (scheme, result) => {
    if (scheme === 'sitaiba') {
      return {
        'Address Generation': result.addr_gen_ms,
        'Fast Recognition': result.fast_recognize_ms,
        'DSK Generation': result.onetime_sk_ms,
        'Identity Tracing': result.trace_ms
      };
    }
    return {
      'Address Generation': result.addr_gen_ms,
      'Fast Recognition': result.fast_recognize_ms,
      'DSK Generation': result.onetime_sk_ms,
      'Signing': result.sign_ms,
      'Signature Verification': result.sig_verify_ms,
      'Identity Tracing': result.trace_ms
    };
  };

  const getFastestOperation = (result) => {
    const operations = getSchemeOperations(scheme, result);
    return Object.entries(operations).reduce((min, [name, time]) => 
      time < min.time ? { name, time } : min, 
      { name: 'Unknown', time: Infinity }
    ).name;
  };

  const getSlowestOperation = (result) => {
    const operations = getSchemeOperations(scheme, result);
    if (scheme === 'sitaiba') operations['Full Recognition'] = result.addr_recognize_ms;
    return Object.entries(operations).reduce((max, [name, time]) => 
      time > max.time ? { name, time } : max, 
      { name: 'Unknown', time: -1 }
    ).name;
  };

  const getOutputContent = () => {
    const error = localError || globalError;
    if (error) return `Error: ${error}`;

    if (selectedResultIndex >= 0 && testResults[selectedResultIndex]) {
      const result = testResults[selectedResultIndex];
      return getPerformanceTestDetails(scheme, result, getFastestOperation, getSlowestOperation);
    }

    if (testResults.length > 0) {
      const latestResult = testResults[testResults.length - 1];
      const metrics = getSchemeOperations(scheme, latestResult);
      const summary = Object.entries(metrics).map(([key, value]) => `• ${key}: ${value}ms`).join('\n');
      return `✅ ${scheme.toUpperCase()} Performance Test Completed!
🔄 Iterations: ${latestResult.iterations}
⚡ Total Time: ${latestResult.total_test_time}ms
📊 Average/Iteration: ${latestResult.avg_per_iteration.toFixed(2)}ms

Key Metrics:
${summary}`;
    }
    
    return `Configure test parameters and run ${scheme.toUpperCase()} scheme performance analysis...`;
  };

  const iterationPresets = [
    { label: 'Quick (10)', value: 10 },
    { label: 'Standard (100)', value: 100 },
    { label: 'Intensive (500)', value: 500 },
    { label: 'Stress (1000)', value: 1000 }
  ];

  const metrics = getOperationMetrics(scheme);

  return (
    <Section title={`📊 Performance Test (${scheme.toUpperCase()})`} className="performance-section">
      <div className="controls">
        <label>Iterations:</label>
        <Input type="number" value={iterations} onChange={handleIterationChange} min="1" max="1000" />
        
        <div className="preset-buttons">
          <label>Quick Presets:</label>
          <div className="inline-controls">
            {iterationPresets.map(preset => (
              <Button key={preset.value} onClick={(e) => handlePresetClick(preset.value, e)} variant="secondary" className="preset-btn">
                {preset.label}
              </Button>
            ))}
          </div>
        </div>
        
        <div className="test-controls">
          <Button onClick={handleRunPerformanceTest} loading={localLoading.testing} disabled={localLoading.testing || iterations < 1 || iterations > 1000} className="test-button">
            {localLoading.testing ? 'Running Test...' : 'Run Performance Test'}
          </Button>
          <Button onClick={handleClearResults} variant="secondary" disabled={testResults.length === 0}>
            Clear Results
          </Button>
        </div>
        
        {testResults.length > 0 && (
          <div className="results-selector">
            <label>View Test Results:</label>
            <select value={selectedResultIndex} onChange={(e) => handleSelectResult(parseInt(e.target.value))} className="select">
              <option value={-1}>Select test result...</option>
              {testResults.map((result, index) => (
                <option key={index} value={index}>
                  Test {index} - {result.iterations} iterations - {new Date(result.timestamp).toLocaleTimeString()}
                </option>
              ))}
            </select>
          </div>
        )}
        
        {localLoading.testing && (
          <div className="progress-indicator">
            <div className="progress-bar"><div className="progress-fill"></div></div>
            <div className="progress-text">Running {iterations} {scheme.toUpperCase()} cryptographic operation iterations...</div>
          </div>
        )}
      </div>
      
      {testResults.length > 0 && (
        <div className="performance-grid">
          {selectedResultIndex >= 0 && testResults[selectedResultIndex] && (
            metrics.map(metric => (
              <div className="perf-metric" key={metric.key}>
                <div className="perf-value">{metric.value || `${testResults[selectedResultIndex][metric.key]}ms`}</div>
                <div className="perf-label">{metric.label}</div>
              </div>
            ))
          )}
        </div>
      )}
      
      <Output content={getOutputContent()} isError={!!(localError || globalError)} />
    </Section>
  );
}

export default PerformanceTest;
