// 工具函數集合

/**
 * 截斷十六進制字符串用於顯示
 */
export function truncateHex(hex, length = 16) {
  if (!hex) return ''
  if (hex.length <= length * 2) return hex
  return hex.substring(0, length) + '...' + hex.substring(hex.length - 8)
}

/**
 * 格式化時間戳
 */
export function formatTimestamp(timestamp) {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleString()
}

/**
 * 檢查是否為有效的十六進制字符串
 */
export function isValidHex(str) {
  if (!str) return false
  return /^[0-9a-fA-F]+$/.test(str) && str.length % 2 === 0
}

/**
 * 驗證表單字段
 */
export function validateField(value, type) {
  switch (type) {
    case 'required':
      return value && value.toString().trim() !== ''
    case 'number':
      return !isNaN(value) && isFinite(value)
    case 'positiveNumber':
      return !isNaN(value) && isFinite(value) && Number(value) > 0
    case 'hex':
      return isValidHex(value)
    default:
      return true
  }
}

/**
 * 生成隨機ID
 */
export function generateId(prefix = 'item') {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}