export function mergeConfig (config, defaultConfig) {
  let res = {}
  for (let i in defaultConfig) {
    res[i] = i in config ? config[i] : defaultConfig[i]
  }
  return res
}

export function formatCurrency (price) {
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: price < 100 ? 2 : 0
  }).format(price)
}

export default {
  mergeConfig,
  formatCurrency
}
