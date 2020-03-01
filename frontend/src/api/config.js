import {mergeConfig} from '@/utils'

export const DEFAULT_CONFIG = {
  minGiftPrice: 7, // $1
  showDanmaku: true,
  showGift: true,
  showGiftName: false,
  mergeSimilarDanmaku: true,
  mergeGift: true,
  maxNumber: 60,

  blockGiftDanmaku: true,
  blockLevel: 0,
  blockNewbie: true,
  blockNotMobileVerified: true,
  blockKeywords: '',
  blockUsers: '',
  blockMedalLevel: 0,

  autoTranslate: false
}

export function setLocalConfig (config) {
  config = mergeConfig(config, DEFAULT_CONFIG)
  window.localStorage.config = JSON.stringify(config)
}

export function getLocalConfig () {
  if (!window.localStorage.config) {
    return DEFAULT_CONFIG
  }
  return mergeConfig(JSON.parse(window.localStorage.config), DEFAULT_CONFIG)
}
