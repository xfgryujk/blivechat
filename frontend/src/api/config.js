import axios from 'axios'

import {mergeConfig} from '@/utils'

export const DEFAULT_CONFIG = {
  minGiftPrice: 6.911, // $1
  mergeSimilarDanmaku: true,
  showDanmaku: true,
  showGift: true,
  maxSpeed: 4,

  blockGiftDanmaku: true,
  blockLevel: 0,
  blockNewbie: true,
  blockNotMobileVerified: true,
  blockKeywords: '',
  blockUsers: '',
  blockMedalLevel: 0,

  css: ''
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

export async function createRemoteConfig (config) {
  config = mergeConfig(config, DEFAULT_CONFIG)
  return (await axios.post('/config', config)).data
}

export async function setRemoteConfig (id, config) {
  config = mergeConfig(config, DEFAULT_CONFIG)
  return (await axios.put(`/config/${id}`, config)).data
}

export async function getRemoteConfig (id) {
  let config = (await axios.get(`/config/${id}`)).data
  return mergeConfig(config, DEFAULT_CONFIG)
}

export default {
  DEFAULT_CONFIG,
  setLocalConfig,
  getLocalConfig,
  createRemoteConfig,
  setRemoteConfig,
  getRemoteConfig
}
