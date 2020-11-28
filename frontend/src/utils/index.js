export function mergeConfig (config, defaultConfig) {
  let res = {}
  for (let i in defaultConfig) {
    res[i] = i in config ? config[i] : defaultConfig[i]
  }
  return res
}

export function toBool (val) {
  if (typeof val === 'string') {
    return ['false', 'no', 'off', '0', ''].indexOf(val.toLowerCase()) === -1
  }
  return !!val
}

export function toInt (val, _default) {
  let res = parseInt(val)
  if (isNaN(res)) {
    res = _default
  }
  return res
}

export function formatCurrency (price) {
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: price < 100 ? 2 : 0
  }).format(price)
}

export function getTimeTextHourMin (date) {
  let hour = date.getHours()
  let min = ('00' + date.getMinutes()).slice(-2)
  return `${hour}:${min}`
}

export function getUuid4Hex () {
  let chars = []
  for (let i = 0; i < 32; i++) {
    let char = Math.floor(Math.random() * 16).toString(16)
    chars.push(char)
  }
  return chars.join('')
}
