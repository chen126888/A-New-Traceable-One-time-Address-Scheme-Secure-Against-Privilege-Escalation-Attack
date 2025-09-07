import React from 'react'
import { useSchemeContext } from '../hooks/useSchemeContext'
import StealthSystemSetup from '../display/stealth/StealthSystemSetup'
import SitaibaSystemSetup from '../display/sitaiba/SitaibaSystemSetup'
import HdwsaSystemSetup from '../display/hdwsa/HdwsaSystemSetup'

function SystemSetup() {
  const { currentScheme } = useSchemeContext()

  if (currentScheme === 'stealth') {
    return <StealthSystemSetup />
  } else if (currentScheme === 'sitaiba') {
    return <SitaibaSystemSetup />
  } else if (currentScheme === 'hdwsa') {
    return <HdwsaSystemSetup />
  }

  return (
    <div className="card">
      <h3>❌ 未支援的方案</h3>
      <p>當前方案 "{currentScheme}" 尚未實現</p>
    </div>
  )
}

export default SystemSetup