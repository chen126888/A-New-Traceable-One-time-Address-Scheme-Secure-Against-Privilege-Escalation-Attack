// API服務層 - 統一管理所有API調用
const API_BASE = '/api'

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' })
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getParamFiles() {
    return this.get('/param_files')
  }

  async setup(paramFile) {
    return this.post('/setup', { param_file: paramFile })
  }

  async generateKey() {
    return this.get('/keygen')
  }

  async getKeys() {
    return this.get('/keylist')
  }

  async generateAddress(keyIndex) {
    return this.post('/addrgen', { key_index: keyIndex })
  }

  async verifyAddress(addressIndex, keyIndex) {
    return this.post('/verify_addr', {
      address_index: addressIndex,
      key_index: keyIndex,
    })
  }

  async generateDSK(addressIndex, keyIndex) {
    return this.post('/dskgen', {
      address_index: addressIndex,
      key_index: keyIndex,
    })
  }

  async signMessage(message, dskIndex) {
    return this.post('/sign', {
      message: message,
      dsk_index: dskIndex,
    })
  }

  async verifySignature(message, qSigmaHex, hHex, addressIndex) {
    return this.post('/verify_signature', {
      message: message,
      q_sigma_hex: qSigmaHex,
      h_hex: hHex,
      address_index: addressIndex,
    })
  }

  async verifySignatureWithTxData(txData) {
    return this.post('/verify_signature', {
      message: txData.message,
      q_sigma_hex: txData.q_sigma_hex,
      h_hex: txData.h_hex,
      addr_hex: txData.addr_hex,
      r2_hex: txData.r2_hex,
      c_hex: txData.c_hex,
    })
  }

  async traceIdentity(addressIndex) {
    return this.post('/trace', { address_index: addressIndex })
  }

  async performanceTest(iterations = 100) {
    return this.post('/performance_test', { iterations })
  }

  async getStatus() {
    return this.get('/status')
  }

  // 重新啟用 reset 函數，但加上防護機制
  async resetSystem() {
    console.log('🔄 Reset system called')
    try {
      return this.post('/reset', {})
    } catch (error) {
      console.error('Reset failed:', error)
      // 即使失敗也返回成功，避免循環
      return { status: 'reset_attempted', error: error.message }
    }
  }
}

export const apiService = new ApiService()