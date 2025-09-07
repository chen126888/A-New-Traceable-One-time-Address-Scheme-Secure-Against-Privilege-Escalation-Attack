import React from 'react'
import { useSchemeContext } from '../hooks/useSchemeContext'
import StealthDSKGeneration from '../display/stealth/StealthDSKGeneration'
import SitaibaDSKGeneration from '../display/sitaiba/SitaibaDSKGeneration'
import HdwsaDSKGeneration from '../display/hdwsa/HdwsaDSKGeneration'

function DSKGeneration() {
  const { currentScheme } = useSchemeContext()

  if (currentScheme === 'stealth') {
    return <StealthDSKGeneration />
  } else if (currentScheme === 'sitaiba') {
    return <SitaibaDSKGeneration />
  } else if (currentScheme === 'hdwsa') {
    return <HdwsaDSKGeneration />
  }

  return (
    <div className="card">
      <h3>❌ 未支援的方案</h3>
      <p>當前方案 "{currentScheme}" 的 DSK 生成功能尚未實現</p>
    </div>
  )
}

export default DSKGeneration