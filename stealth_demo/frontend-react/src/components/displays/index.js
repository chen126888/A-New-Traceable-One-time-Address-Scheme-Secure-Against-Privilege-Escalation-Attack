// Display component mapping for different schemes
import * as sitaibaDisplays from './sitaiba'
import * as stealthDisplays from './stealth'

const schemeDisplays = {
  sitaiba: sitaibaDisplays,
  stealth: stealthDisplays,
}

export const getDisplayComponent = (schemeName, componentName) => {
  // Handle empty or null scheme name during initialization
  if (!schemeName) {
    // Don't log warning for empty scheme name during initialization
    return null
  }
  
  const schemeComponents = schemeDisplays[schemeName]
  if (!schemeComponents) {
    console.warn(`No display components found for scheme: ${schemeName}`)
    return null
  }
  
  const component = schemeComponents[componentName]
  if (!component) {
    console.warn(`Display component '${componentName}' not found for scheme '${schemeName}'`)
    return null
  }
  
  return component
}