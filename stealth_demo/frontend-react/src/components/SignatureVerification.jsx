import React from 'react'
import { useSchemeContext } from '../hooks/useSchemeContext'
import StealthSignatureVerification from '../display/stealth/StealthSignatureVerification'
import HdwsaSignatureVerification from '../display/hdwsa/HdwsaSignatureVerification'

function SignatureVerification() {
  const { currentScheme, supportsVerification } = useSchemeContext()

  if (currentScheme === 'stealth' && supportsVerification) {
    return <StealthSignatureVerification />
  } else if (currentScheme === 'hdwsa' && supportsVerification) {
    return <HdwsaSignatureVerification />
  } else if (currentScheme === 'sitaiba' || !supportsVerification) {
    return null
  }

  return null
}

export default SignatureVerification