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

  async traceIdentity(addressIndex) {
    return this.post('/trace', { address_index: addressIndex })
  }

  async performanceTest(iterations = 100) {
    return this.post('/performance_test', { iterations })
  }

  async getStatus() {
    return this.get('/status')
  }

  async resetSystem() {
    console.log('🚫 resetSystem called - DISABLED to stop loop')
    return Promise.resolve({ status: 'disabled' })
  }
}

export const apiService = new ApiService()