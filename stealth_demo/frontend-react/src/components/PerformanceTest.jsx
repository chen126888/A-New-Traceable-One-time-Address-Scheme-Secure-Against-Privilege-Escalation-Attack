import React from 'react'
import { useSchemeContext } from '../hooks/useSchemeContext'
import StealthPerformanceTest from '../display/stealth/StealthPerformanceTest'
import SitaibaPerformanceTest from '../display/sitaiba/SitaibaPerformanceTest'

function PerformanceTest() {
  const { currentScheme } = useSchemeContext()

  if (currentScheme === 'stealth') {
    return <StealthPerformanceTest />
  } else if (currentScheme === 'sitaiba') {
    return <SitaibaPerformanceTest />
  }

  return (
    <div className="card">
      <h3>❌ 未支援的方案</h3>
      <p>當前方案 "{currentScheme}" 的性能測試功能尚未實現</p>
    </div>
  )
}

export default PerformanceTest