import axios from 'axios'
import _ from 'lodash'
import CircuitBreaker from 'opossum'

axios.defaults.timeout = 10 * 1000

export const apiClient = axios.create({
  timeout: 10 * 1000,
})

export let getBaseUrl
if (!process.env.BACKEND_DISCOVERY) {
  const onRequest = config => {
    config.baseURL = getBaseUrl()
    return config
  }

  const onRequestError = e => {
    throw e
  }

  apiClient.interceptors.request.use(onRequest, onRequestError, { synchronous: true })

  getBaseUrl = function() {
    return window.location.origin
  }
} else {
  const onRequest = config => {
    let baseUrl = getBaseUrl()
    if (baseUrl === null) {
      throw new Error('No available endpoint')
    }
    config.baseURL = baseUrl
    return config
  }

  const onRequestError = e => {
    throw e
  }

  const onResponse = response => {
    let promise = Promise.resolve(response)
    let baseUrl = response.config.baseURL
    let breaker = getOrAddCircuitBreaker(baseUrl)
    breaker.fire(promise).catch(() => {})
    return response
  }

  const onResponseError = e => {
    let promise = Promise.reject(e)
    if (!e.response || (500 <= e.response.status && e.response.status < 600)) {
      let baseUrl = e.config.baseURL
      let breaker = getOrAddCircuitBreaker(baseUrl)
      breaker.fire(promise).catch(() => {})
    }
    return promise
  }

  apiClient.interceptors.request.use(onRequest, onRequestError, { synchronous: true })
  apiClient.interceptors.response.use(onResponse, onResponseError)

  const DISCOVERY_URLS = process.env.NODE_ENV === 'production' ? [
    // 只有公共服务器会开BACKEND_DISCOVERY，这里可以直接跨域访问
    'https://api1.blive.chat/api/endpoints',
    'https://api2.blive.chat/api/endpoints',
  ] : [
    `${window.location.origin}/api/endpoints`,
    'http://localhost:12450/api/endpoints',
  ]
  let baseUrls = process.env.NODE_ENV === 'production' ? [
    'https://api1.blive.chat',
    'https://api2.blive.chat',
  ] : [
    window.location.origin,
    'http://localhost:12450',
  ]
  let curBaseUrl = null
  let baseUrlToCircuitBreaker = new Map()

  const doUpdateBaseUrls = async() => {
    async function requestGetUrls(discoveryUrl) {
      try {
        return (await axios.get(discoveryUrl)).data.endpoints
      } catch (e) {
        console.warn('Failed to discover server endpoints from one source:', e)
        throw e
      }
    }

    let _baseUrls = []
    try {
      let promises = DISCOVERY_URLS.map(requestGetUrls)
      _baseUrls = await Promise.any(promises)
    } catch {
    }
    if (_baseUrls.length === 0) {
      console.error('Failed to discover server endpoints from any source')
      return
    }

    // 按响应时间排序
    let sortedBaseUrls = []
    let errorBaseUrls = []

    async function testEndpoint(baseUrl) {
      try {
        let url = `${baseUrl}/api/server_info`
        await axios.get(url, { timeout: 3 * 1000 })
        sortedBaseUrls.push(baseUrl)
      } catch {
        errorBaseUrls.push(baseUrl)
      }
    }

    await Promise.all(_baseUrls.map(testEndpoint))
    sortedBaseUrls = sortedBaseUrls.concat(errorBaseUrls)

    baseUrls = sortedBaseUrls
    if (baseUrls.indexOf(curBaseUrl) === -1) {
      curBaseUrl = null
    }

    console.log('Found server endpoints:', baseUrls)
  }
  const updateBaseUrls = _.throttle(doUpdateBaseUrls, 3 * 60 * 1000)

  getBaseUrl = function() {
    updateBaseUrls()

    if (curBaseUrl !== null) {
      let breaker = getOrAddCircuitBreaker(curBaseUrl)
      if (!breaker.opened) {
        return curBaseUrl
      }
      curBaseUrl = null
    }

    // 找第一个未熔断的
    for (let baseUrl of baseUrls) {
      let breaker = getOrAddCircuitBreaker(baseUrl)
      if (!breaker.opened) {
        curBaseUrl = baseUrl
        console.log('Switch server endpoint to', curBaseUrl)
        return curBaseUrl
      }
    }
    return null
  }

  const getOrAddCircuitBreaker = baseUrl => {
    let breaker = baseUrlToCircuitBreaker.get(baseUrl)
    if (breaker === undefined) {
      breaker = new CircuitBreaker(promise => promise, {
        timeout: false,
        rollingCountTimeout: 60 * 1000,
        errorThresholdPercentage: 70,
        resetTimeout: 60 * 1000,
      })
      baseUrlToCircuitBreaker.set(baseUrl, breaker)
    }
    return breaker
  }

  await updateBaseUrls()
}
