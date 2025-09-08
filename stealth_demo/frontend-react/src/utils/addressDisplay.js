import { truncateHex } from './helpers';

// Handles the detailed view when an address is selected from the list
export const getAddressDisplayDetails = (scheme, address) => {
  if (!address) return '';

  const commonDetails = `🔍 Address Details - ${address.id}
🆔 Index: ${address.key_index}
👤 Owner Key: ${address.key_id} (Index: ${address.key_index})
📊 Status: ${address.status}`;

  if (scheme === 'sitaiba') {
    return `${commonDetails}
🎯 Scheme: sitaiba

🏠 Address (G1 Group):
${address.addr_hex}

🎲 Random Parameter R1 (G1 Group):
${address.r1_hex}

🎲 Random Parameter R2 (G1 Group):
${address.r2_hex}

💡 SITAIBA Address Features:
• Address and random parameters are in G1 group
• Supports fast and full address recognition
• Address can be used for DSK generation and identity tracing
• No C parameter required (unlike Stealth)`;
  }

  // Default to stealth
  return `${commonDetails}
🎯 Scheme: stealth

🏠 Address:
${address.addr_hex}

🎲 R1:
${address.r1_hex}

🎲 R2:
${address.r2_hex}

🔒 C:
${address.c_hex}`;
};

// Handles the summary view for the most recently generated address
export const getLatestAddressSummary = (scheme, address) => {
  if (!address) return '';

  const commonSummary = `✅ ${scheme.toUpperCase()} Address Generated Successfully!
🆔 Address ID: ${address.id}
👤 Owner Key: ${address.key_id}
🏠 Address: ${truncateHex(address.addr_hex)}
🎲 R1: ${truncateHex(address.r1_hex)}
🎲 R2: ${truncateHex(address.r2_hex)}`;

  if (scheme === 'sitaiba') {
    return commonSummary;
  }

  // Default to stealth
  return `${commonSummary}
🔒 C: ${truncateHex(address.c_hex)}`;
};
