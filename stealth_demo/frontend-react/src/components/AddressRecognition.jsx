import React from 'react'
import { useSchemeContext } from '../hooks/useSchemeContext'
import StealthAddressRecognition from '../display/stealth/StealthAddressRecognition'
import SitaibaAddressRecognition from '../display/sitaiba/SitaibaAddressRecognition'
import HdwsaAddressRecognition from '../display/hdwsa/HdwsaAddressRecognition'

function AddressRecognition() {
  const { currentScheme } = useSchemeContext()

  if (currentScheme === 'stealth') {
    return <StealthAddressRecognition />
  } else if (currentScheme === 'sitaiba') {
    return <SitaibaAddressRecognition />
  } else if (currentScheme === 'hdwsa') {
    return <HdwsaAddressRecognition />
  }

  return (
    <div className="card">
      <h3>❌ 未支援的方案</h3>
      <p>當前方案 "{currentScheme}" 的地址識別功能尚未實現</p>
    </div>
  )
}

export default AddressRecognition