import VueI18n from 'vue-i18n'

import zh from '@/lang/zh'

let lastSetLocale = 'zh'
let loadedLocales = ['zh']

export async function setLocale(locale) {
  lastSetLocale = locale
  if (loadedLocales.indexOf(locale) === -1) {
    // eslint-disable-next-line prefer-template
    let langModule = await import('@/lang/' + locale)
    i18n.setLocaleMessage(locale, langModule.default)
    loadedLocales.push(locale)

    // 加载完成之前又调用了setLocale，这次的不生效
    if (locale !== lastSetLocale) {
      return
    }
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
