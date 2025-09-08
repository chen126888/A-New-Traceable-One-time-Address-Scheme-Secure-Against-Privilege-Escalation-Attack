import { truncateHex } from './helpers';

export const getSystemSetupDetails = (scheme, traceKey, selectedParam) => {
  if (!traceKey) return '';

  if (scheme === 'sitaiba') {
    return `✅ SITAIBA System Initialization Successful!\n📄 Parameter File: ${selectedParam}\n🔑 Tracer Public Key (TK): ${truncateHex(traceKey.TK_hex)}\n🔐 Tracer Private Key (k): ${truncateHex(traceKey.k_hex)}\n📊 G1 Group Size: ${traceKey.g1_size} bytes\n📊 Zr Group Size: ${traceKey.zr_size} bytes\n🎯 Scheme: ${traceKey.scheme}\n✅ Status: ${traceKey.status}`;
  }

  // Default to stealth
  return `✅ System Initialized Successfully!\n📄 Parameter File: ${selectedParam}\n🔑 Trace Key: ${truncateHex(traceKey.TK_hex)}\n🔐 K Value: ${truncateHex(traceKey.k_hex)}\n📊 G1 Size: ${traceKey.g1_size} bytes\n📊 Zr Size: ${traceKey.zr_size} bytes\n✅ Status: ${traceKey.status}`;
};
