import {mergeConfig} from '@/utils'

export const DEFAULT_CONFIG = {
  minGiftPrice: 7, // $1
  showDanmaku: true,
  showGift: true,
  showGiftName: false,
  mergeSimilarDanmaku: false,
  mergeGift: true,
  maxNumber: 60,

  blockGiftDanmaku: true,
  blockLevel: 0,
  blockNewbie: false,
  blockNotMobileVerified: false,
  blockKeywords: '',
  blockUsers: '',
  blockMedalLevel: 0,

  relayMessagesByServer: false,
  autoTranslate: false,
  giftUsernamePronunciation: ''
}

export function setLocalConfig (config) {
  config = mergeConfig(config, DEFAULT_CONFIG)
  window.localStorage.config = JSON.stringify(config)
}

export function getLocalConfig () {
  try {
    return mergeConfig(JSON.parse(window.localStorage.config), DEFAULT_CONFIG)
  } catch {
    return {...DEFAULT_CONFIG}
  }
}
