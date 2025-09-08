import React from 'react';
import { Section, Select, DataList, Output } from './common';
import { truncateHex } from '../utils/helpers';

function BaseIdentityTracing({
  title,
  children,
  selectedAddrIndex,
  onAddressChange,
  addresses,
  items,
  outputContent,
  isError,
  globalLoading
}) {
  // Filter addresses based on the scheme provided by the parent component
  const filteredAddresses = addresses.filter(addr => addr.scheme === (title.includes('SITAIBA') ? 'sitaiba' : 'stealth'));

  return (
    <Section title={title}>
      <div className="controls">
        <label>Select address to trace:</label>
        <Select
          value={selectedAddrIndex}
          onChange={onAddressChange}
          disabled={globalLoading.all}
        >
          <option value="">Select address...</option>
          {filteredAddresses.map((addr, index) => (
            // Important: The value must be the original index in the `addresses` array
            <option key={addr.id} value={addresses.indexOf(addr)}>
              {addr.id} - Owner: {addr.key_id} - {truncateHex(addr.addr_hex, 8)}
            </option>
          ))}
        </Select>
        
        {children}
      </div>
      
      <DataList items={items} />
      
      <Output 
        content={outputContent}
        isError={isError}
      />
    </Section>
  );
}

export default BaseIdentityTracing;
