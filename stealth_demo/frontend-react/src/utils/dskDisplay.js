import { truncateHex } from './helpers';

export const getDSKDetails = (scheme, dsk, index) => {
  if (!dsk) return '';

  if (scheme === 'sitaiba') {
    return `🔍 SITAIBA DSK Details - ${dsk.id}\n🆔 Index: ${index}\n📧 Corresponding Address: ${dsk.address_id} (Index: ${dsk.address_index})\n🔑 Key Used: ${dsk.key_id} (Index: ${dsk.key_index})\n🎯 Scheme: ${dsk.scheme || 'sitaiba'}\n📊 Status: ${dsk.status}\n\n🔐 DSK (Zr Group Element):\n${dsk.dsk_hex}\n\n🏠 Corresponding Address:\n${dsk.for_address}\n\n👤 Owner Public Key:\nA: ${dsk.owner_A}\nB: ${dsk.owner_B}\n\n💡 SITAIBA DSK Features:\n• DSK belongs to Zr group (unlike Stealth's G1 group)\n• Cannot be used for message signing (SITAIBA doesn't support signing)\n• Can be used to verify address ownership`;
  }

  // Default to stealth
  return `🔍 DSK Details - ${dsk.id}\n🆔 Index: ${index}\n📧 For Address: ${dsk.address_id} (Index: ${dsk.address_index})\n🔑 Using Key: ${dsk.key_id} (Index: ${dsk.key_index})\n🛠️ Generation Method: ${dsk.method}\n📊 Status: ${dsk.status}\n\n🔐 DSK (One-time Secret Key):\n${dsk.dsk_hex}\n\n🏠 Target Address:\n${dsk.for_address}\n\n👤 Owner Public Key A:\n${dsk.owner_A}\n\n👤 Owner Public Key B:\n${dsk.owner_B}`;
};

export const getLatestDSKSummary = (scheme, dsk) => {
  if (!dsk) return '';

  if (scheme === 'sitaiba') {
    return `✅ SITAIBA DSK Generated Successfully!\n🆔 DSK ID: ${dsk.id}\n🎯 Scheme: SITAIBA\n📧 Corresponding Address: ${dsk.address_id}\n🔑 Key Used: ${dsk.key_id}\n🔐 DSK (Zr Group): ${truncateHex(dsk.dsk_hex)}`;
  }

  // Default to stealth
  return `✅ DSK Generated Successfully!\n🆔 DSK ID: ${dsk.id}\n📧 For Address: ${dsk.address_id}\n🔑 Using Key: ${dsk.key_id}\n🛠️ Method: ${dsk.method}\n🔐 DSK: ${truncateHex(dsk.dsk_hex)}`;
};
