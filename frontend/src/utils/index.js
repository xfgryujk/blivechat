export function mergeConfig(config, defaultConfig) {
  let res = {}
  for (let i in defaultConfig) {
    res[i] = i in config ? config[i] : defaultConfig[i]
  }
  return res
}

export function toBool(val) {
  if (typeof val === 'string') {
    return ['false', 'no', 'off', '0', ''].indexOf(val.toLowerCase()) === -1
  }
  return Boolean(val)
}

export function toInt(val, _default) {
  let res = parseInt(val)
  if (isNaN(res)) {
    res = _default
  }
  return res
}

export function toFloat(val, _default) {
  let res = parseFloat(val)
  if (isNaN(res)) {
    res = _default
  }
  return res
}

export function formatCurrency(price) {
  let minimumFractionDigits
  if (price < 10) {
    minimumFractionDigits = 2
  } else if (price < 100) {
    minimumFractionDigits = 1
  } else {
    minimumFractionDigits = 0
  }
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits
  }).format(price)
}

export function getTimeTextHourMin(date) {
  let hour = `00${date.getHours()}`.slice(-2)
  let min = `00${date.getMinutes()}`.slice(-2)
  return `${hour}:${min}`
}

export function getUuid4Hex() {
  let chars = []
  for (let i = 0; i < 32; i++) {
    let char = Math.floor(Math.random() * 16).toString(16)
    chars.push(char)
  }
  return chars.join('')
}
