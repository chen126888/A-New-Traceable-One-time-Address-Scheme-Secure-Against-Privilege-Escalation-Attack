import React from 'react'
import { useSchemeContext } from '../hooks/useSchemeContext'
import StealthMessageSigning from '../display/stealth/StealthMessageSigning'
import SitaibaNoSigning from '../display/sitaiba/SitaibaNoSigning'
import HdwsaMessageSigning from '../display/hdwsa/HdwsaMessageSigning'

function MessageSigning() {
  const { currentScheme } = useSchemeContext()

  if (currentScheme === 'stealth') {
    return <StealthMessageSigning />
  } else if (currentScheme === 'hdwsa') {
    return <HdwsaMessageSigning />
  }

  // This component is only rendered for schemes that support signing,
  // so no explicit check for 'sitaiba' is needed here.
  return null
}

export default MessageSigning