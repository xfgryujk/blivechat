import Vue from 'vue'
import VueI18n from 'vue-i18n'

import zh from '@/lang/zh'

let loadedLocales = ['zh']

Vue.use(VueI18n)

export async function setLocale(locale) {
  if (loadedLocales.indexOf(locale) === -1) {
    // eslint-disable-next-line prefer-template
    let langModule = await import('@/lang/' + locale)
    i18n.setLocaleMessage(locale, langModule.default)
    loadedLocales.push(locale)
  }
  window.localStorage.lang = i18n.locale = locale
}

export const i18n = new VueI18n({
  locale: 'zh',
  fallbackLocale: 'zh',
  messages: {
    zh
  }
})

function getDefaultLocale() {
  let locale = window.localStorage.lang
  if (!locale) {
    let lang = navigator.language
    if (lang.startsWith('zh')) {
      locale = 'zh'
    } else if (lang.startsWith('ja')) {
      locale = 'ja'
    } else {
      locale = 'en'
    }
  }
  return locale
}
setLocale(getDefaultLocale())
