import { truncateHex } from './helpers';

export const getRecognitionResultDetails = (scheme, recognitionResult, selectedAddr, selectedKey) => {
  if (!recognitionResult) return '';

  const commonDetails = `🔍 ${scheme.toUpperCase()} Address Recognition Result:\n📧 Address: ${recognitionResult.address_id}\n🔑 Key Used: ${recognitionResult.key_id}\n👤 Is Owner: ${recognitionResult.is_owner ? '✅ Yes' : '❌ No'}\n✅ Recognition Result: ${recognitionResult.recognized ? '✅ Recognized' : '❌ Not Recognized'}\n🔧 Recognition Method: ${recognitionResult.method}\n📊 Status: ${recognitionResult.status}\n🎯 Scheme: ${recognitionResult.scheme || scheme}\n\n📋 Detailed Information:\n🏠 Address: ${truncateHex(selectedAddr?.addr_hex)}\n🔑 Key A: ${truncateHex(selectedKey?.A_hex)}\n🔑 Key B: ${truncateHex(selectedKey?.B_hex)}`;

  if (scheme === 'sitaiba') {
    return `${commonDetails}\n\n💡 SITAIBA Recognition Features:\n• Fast Recognition: Uses only r1, r2, A, a parameters\n• Full Recognition: Uses all parameters for recognition`;
  }

  // Default to stealth
  return `${commonDetails}\n\n💡 Stealth Recognition Features:\n• Fast Recognition: Uses optimized algorithm\n• Full Recognition: Uses complete verification\n\n${recognitionResult.is_owner && recognitionResult.recognized ? 
  '✅ Address recognized and belongs to this key.' : 
  recognitionResult.recognized ? 
    '✅ Address is recognized but not owned by this key.' :
    '❌ Address recognition failed.'
}`;
};
