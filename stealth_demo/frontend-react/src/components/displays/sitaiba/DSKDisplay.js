import React from 'react'
import { truncateHex } from '../../../utils/helpers'

// SITAIBA DSK 顯示組件
export const DSKDisplay = ({ dskList, selectedDSKIndex, localError, globalError }) => {
  const error = localError || globalError
  if (error) {
    return `Error: ${error}`
  }
  
  if (selectedDSKIndex >= 0 && dskList[selectedDSKIndex]) {
    const dsk = dskList[selectedDSKIndex]
    return `🔍 DSK Details - ${dsk.id}
🆔 Index: ${selectedDSKIndex}
📧 For Address: ${dsk.address_id} (Index: ${dsk.address_index})
🔑 Using Key: ${dsk.key_id} (Index: ${dsk.key_index})
🛠️ Generation Method: ${dsk.method}
📊 Status: ${dsk.status}

🔐 DSK (One-time Secret Key):
${dsk.dsk_hex}

🏠 Target Address:
${dsk.for_address}

👤 Owner Public Key A:
${dsk.owner_A}

👤 Owner Public Key B:
${dsk.owner_B}`
  }
  
  // 顯示最新生成的DSK
  if (dskList.length > 0) {
    const latestDSK = dskList[dskList.length - 1]
    return `✅ DSK Generated Successfully!
🆔 DSK ID: ${latestDSK.id}
📧 For Address: ${latestDSK.address_id}
🔑 Using Key: ${latestDSK.key_id}
🔐 DSK: ${truncateHex(latestDSK.dsk_hex)}`
  }
  
  return 'Select an address and key to generate DSK...'
}

// SITAIBA DSK 列表項目
export const DSKListItems = ({ dskList, selectedDSKIndex, onDSKClick }) => {
  return dskList.map((dsk, index) => ({
    id: dsk.id,
    header: `${dsk.id} (${dsk.address_id})`,
    details: [
      `Key: ${dsk.key_id}`,
      `DSK: ${truncateHex(dsk.dsk_hex, 12)}`
    ],
    selected: index === selectedDSKIndex,
    onClick: () => onDSKClick(index)
  }))
}