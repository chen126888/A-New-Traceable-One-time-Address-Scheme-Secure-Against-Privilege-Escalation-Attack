import React from 'react'
import { useSchemeContext } from '../hooks/useSchemeContext'
import StealthAddressGeneration from '../display/stealth/StealthAddressGeneration'
import SitaibaAddressGeneration from '../display/sitaiba/SitaibaAddressGeneration'
import HdwsaAddressGeneration from '../display/hdwsa/HdwsaAddressGeneration'

function AddressGeneration() {
  const { currentScheme } = useSchemeContext()

  if (currentScheme === 'stealth') {
    return <StealthAddressGeneration />
  } else if (currentScheme === 'sitaiba') {
    return <SitaibaAddressGeneration />
  } else if (currentScheme === 'hdwsa') {
    return <HdwsaAddressGeneration />
  }

  return (
    <div className="card">
      <h3>❌ 未支援的方案</h3>
      <p>當前方案 "{currentScheme}" 的地址生成功能尚未實現</p>
    </div>
  )
}

export default AddressGeneration