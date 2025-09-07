import React from 'react'
import { useSchemeContext } from '../hooks/useSchemeContext'
import StealthPerformanceTest from '../display/stealth/StealthPerformanceTest'
import SitaibaPerformanceTest from '../display/sitaiba/SitaibaPerformanceTest'
import HdwsaPerformanceTest from '../display/hdwsa/HdwsaPerformanceTest'

function PerformanceTest() {
  const { currentScheme } = useSchemeContext()

  if (currentScheme === 'stealth') {
    return <StealthPerformanceTest />
  } else if (currentScheme === 'sitaiba') {
    return <SitaibaPerformanceTest />
  } else if (currentScheme === 'hdwsa') {
    return <HdwsaPerformanceTest />
  }

  return (
    <div className="card">
      <h3>❌ 未支援的方案</h3>
      <p>當前方案 "{currentScheme}" 的性能測試功能尚未實現</p>
    </div>
  )
}

export default PerformanceTest