// Stealth Display Components Export
export { StealthSystemSetup } from './StealthSystemSetup.jsx'
export { StealthKeyGeneration } from './StealthKeyGeneration.jsx'
export { StealthDskDisplay } from './StealthDskDisplay.jsx'
export { StealthMessageSigning } from './StealthMessageSigning.jsx'
export { StealthSignatureVerify } from './StealthSignatureVerify.jsx'

// Import stealth components
import { StealthAddressGeneration } from './StealthAddressGeneration.jsx'
import { StealthAddressVerification } from './StealthAddressVerification.jsx'
import { StealthDSKGeneration, StealthDSKListItems } from './StealthDSKGeneration.jsx'
import { StealthMessageSigning } from './StealthMessageSigning.jsx'
import { StealthSignatureVerify } from './StealthSignatureVerify.jsx'
import { StealthIdentityTracing } from './StealthIdentityTracing.jsx'
import { truncateHex } from '../../../utils/helpers'

// Create adapters to match the expected component names
export const AddressDisplay = StealthAddressGeneration
export const AddressVerificationDisplay = StealthAddressVerification
export const DSKDisplay = StealthDSKGeneration
export const DSKListItems = StealthDSKListItems

// Create adapter for MessageSigningDisplay that matches the interface expected by MessageSigning component
export const MessageSigningDisplay = ({ signatureList, selectedSignatureIndex, onSignatureClick, localError, globalError }) => {
  // If there's a latest signature, show it with the stealth format
  if (signatureList.length > 0) {
    const latestSig = signatureList[signatureList.length - 1]
    return StealthMessageSigning({
      signResult: latestSig,
      error: localError || globalError
    })
  }
  
  return StealthMessageSigning({
    signResult: null,
    error: localError || globalError
  })
}

// Stealth Address List Items - adapted for stealth address format
export const AddressListItems = ({ addresses, selectedIndex, onAddressClick }) => {
  return addresses.map((addr, index) => {
    // Handle both normalized format (id) and raw API format (addr_id)
    const addressId = addr.id || `stealth_addr_${addr.addr_id ?? index}`
    const keyId = addr.key_id ?? 'Unknown'
    
    return {
      id: addressId,
      header: `${addressId} (Owner: ${keyId})`,
      details: [
        `Addr: ${truncateHex(addr.addr_hex || addr.address?.hex, 20)}`,
        `R1: ${truncateHex(addr.r1_hex || addr.R1?.hex, 12)}`,
        `R2: ${truncateHex(addr.r2_hex || addr.R2?.hex, 12)}`,
        `C: ${truncateHex(addr.c_hex || addr.C?.hex, 12)}`
      ],
      selected: index === selectedIndex,
      onClick: () => onAddressClick(index)
    }
  })
}

export const TraceDisplay = StealthIdentityTracing

// Stealth Trace List Items - adapted for stealth trace format  
export const TraceListItems = ({ traces, selectedIndex, onTraceClick }) => {
  if (!traces || traces.length === 0) return []
  
  return traces.map((trace, index) => ({
    id: trace.trace_id || `trace_${index}`,
    header: `Trace ${index} - Addr: ${trace.addr_id}`,
    details: [
      `Match: ${trace.match ? '✅ Yes' : '❌ No'}`,
      `Recovered B: ${truncateHex(trace.recovered_B?.hex || trace.recovered_B, 16)}`
    ],
    selected: index === selectedIndex,
    onClick: () => onTraceClick(index)
  }))
}

// Create adapter for SignatureVerificationDisplay that matches the interface expected by SignatureVerification component
export const SignatureVerificationDisplay = ({ verificationResult, txMessages, selectedTxIndex, localError, globalError }) => {
  return StealthSignatureVerify({
    verifyResult: verificationResult,
    error: localError || globalError
  })
}