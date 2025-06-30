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
  // 移除可能的 0x 前綴
  const cleanStr = str.startsWith('0x') ? str.slice(2) : str
  // 檢查是否只包含十六進制字符且長度為偶數
  return /^[0-9a-fA-F]*$/.test(cleanStr) && cleanStr.length % 2 === 0 && cleanStr.length > 0
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
    case 'email':
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
    case 'range':
      const [min, max] = (arguments[2] || []).split(',').map(Number)
      const num = Number(value)
      return !isNaN(num) && num >= min && num <= max
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

/**
 * 安全地解析JSON
 */
export function safeJsonParse(str, defaultValue = null) {
  try {
    return JSON.parse(str)
  } catch (e) {
    return defaultValue
  }
}

/**
 * 深拷貝對象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (obj instanceof Object) {
    const clonedObj = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
}

/**
 * 防抖函數
 */
export function debounce(func, wait, immediate = false) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      timeout = null
      if (!immediate) func(...args)
    }
    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    if (callNow) func(...args)
  }
}

/**
 * 節流函數
 */
export function throttle(func, limit) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 復制文本到剪貼板
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (err) {
    // 降級方案
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    try {
      document.execCommand('copy')
      return true
    } catch (fallbackErr) {
      return false
    } finally {
      document.body.removeChild(textArea)
    }
  }
}

/**
 * 等待指定時間
 */
export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 錯誤處理包裝器
 */
export function withErrorHandling(fn, errorHandler = console.error) {
  return async (...args) => {
    try {
      return await fn(...args)
    } catch (error) {
      errorHandler(error)
      throw error
    }
  }
}

/**
 * 檢查對象是否為空
 */
export function isEmpty(obj) {
  if (obj == null) return true
  if (Array.isArray(obj) || typeof obj === 'string') return obj.length === 0
  if (obj instanceof Map || obj instanceof Set) return obj.size === 0
  return Object.keys(obj).length === 0
}

/**
 * 獲取數組中的隨機元素
 */
export function randomElement(array) {
  return array[Math.floor(Math.random() * array.length)]
}

/**
 * 將十六進制字符串轉換為字節數組
 */
export function hexToBytes(hex) {
  if (!isValidHex(hex)) {
    throw new Error('Invalid hexadecimal string')
  }
  const cleanHex = hex.startsWith('0x') ? hex.slice(2) : hex
  const bytes = []
  for (let i = 0; i < cleanHex.length; i += 2) {
    bytes.push(parseInt(cleanHex.substr(i, 2), 16))
  }
  return bytes
}

/**
 * 將字節數組轉換為十六進制字符串
 */
export function bytesToHex(bytes) {
  return bytes.map(byte => byte.toString(16).padStart(2, '0')).join('')
}

/**
 * 比較兩個十六進制字符串是否相等
 */
export function hexEqual(hex1, hex2) {
  if (!hex1 || !hex2) return false
  const clean1 = hex1.startsWith('0x') ? hex1.slice(2) : hex1
  const clean2 = hex2.startsWith('0x') ? hex2.slice(2) : hex2
  return clean1.toLowerCase() === clean2.toLowerCase()
}