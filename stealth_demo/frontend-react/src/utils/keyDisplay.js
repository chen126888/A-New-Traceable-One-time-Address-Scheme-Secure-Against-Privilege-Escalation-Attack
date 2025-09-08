import { truncateHex } from './helpers';

export const getKeyDetails = (scheme, key, index) => {
  if (!key) return '';

  const commonDetails = `🔍 Key Details - ${key.id}
🆔 Index: ${index}
📄 Parameter File: ${key.param_file || 'Unknown'}
🎯 Scheme: ${key.scheme || scheme}
📊 Status: ${key.status}`;

  if (scheme === 'sitaiba') {
    return `${commonDetails}

🔓 Public Key A (G1 Group):
${key.A_hex}

🔓 Public Key B (G1 Group):
${key.B_hex}

🔐 Private Key a (Zr Group):
${key.a_hex}

🔐 Private Key b (Zr Group):
${key.b_hex}

💡 SITAIBA Features:
• Private keys a, b belong to Zr group
• Public keys A, B belong to G1 group
• Supports fast and full address recognition
• Does not support message signing functionality`;
  }

  // Default to stealth
  return `${commonDetails}

🔓 Public Key A:
${key.A_hex}

🔓 Public Key B:
${key.B_hex}

🔐 Private Key a:
${key.a_hex}

🔐 Private Key b:
${key.b_hex}`;
};

export const getLatestKeySummary = (scheme, key) => {
  if (!key) return '';
  
  const commonSummary = `✅ ${scheme.toUpperCase()} Key Generation Successful!
🆔 Key ID: ${key.id}
🎯 Scheme: ${scheme.toUpperCase()}
🔓 Public Key A: ${truncateHex(key.A_hex)}
🔓 Public Key B: ${truncateHex(key.B_hex)}
🔐 Private Key a: ${truncateHex(key.a_hex)}
🔐 Private Key b: ${truncateHex(key.b_hex)}`;

  return commonSummary;
};
