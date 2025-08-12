import React from 'react'
import { useSchemeContext } from '../hooks/useSchemeContext'
import StealthMessageSigning from '../display/stealth/StealthMessageSigning'
import SitaibaNoSigning from '../display/sitaiba/SitaibaNoSigning'

function MessageSigning() {
  const { currentScheme, supportsSigning } = useSchemeContext()

  if (currentScheme === 'stealth' && supportsSigning) {
    return <StealthMessageSigning />
  } else if (currentScheme === 'sitaiba' || !supportsSigning) {
    return null
  }

  return null
}

export default MessageSigning