import React from 'react'
import { useSchemeContext } from '../hooks/useSchemeContext'
import StealthIdentityTracing from '../display/stealth/StealthIdentityTracing'
import SitaibaIdentityTracing from '../display/sitaiba/SitaibaIdentityTracing'

function IdentityTracing() {
  const { currentScheme } = useSchemeContext()

  if (currentScheme === 'stealth') {
    return <StealthIdentityTracing />
  } else if (currentScheme === 'sitaiba') {
    return <SitaibaIdentityTracing />
  }

  return (
    <div className="card">
      <h3>❌ 未支援的方案</h3>
      <p>當前方案 "{currentScheme}" 的身份追蹤功能尚未實現</p>
    </div>
  )
}

export default IdentityTracing