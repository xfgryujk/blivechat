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

export function getTimeTextMinSec (date) {
  let min = ('00' + date.getMinutes()).slice(-2)
  let sec = ('00' + date.getSeconds()).slice(-2)
  return `${min}:${sec}`
}

export default {
  mergeConfig,
  formatCurrency,
  getTimeTextMinSec
}
