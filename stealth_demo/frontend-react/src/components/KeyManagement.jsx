import React from 'react'
import { useSchemeContext } from '../hooks/useSchemeContext'
import StealthKeyManagement from '../display/stealth/StealthKeyManagement'
import SitaibaKeyManagement from '../display/sitaiba/SitaibaKeyManagement'

function KeyManagement() {
  const { currentScheme } = useSchemeContext()

  if (currentScheme === 'stealth') {
    return <StealthKeyManagement />
  } else if (currentScheme === 'sitaiba') {
    return <SitaibaKeyManagement />
  }

  return (
    <div className="card">
      <h3>❌ 未支援的方案</h3>
      <p>當前方案 "{currentScheme}" 的金鑰管理功能尚未實現</p>
    </div>
  )
}

export default KeyManagement