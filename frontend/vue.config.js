const API_BASE_URL = 'http://localhost:12450'

module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: API_BASE_URL,
        ws: true
      },
      '/upload': {
        target: API_BASE_URL
      }
    }
  },
  chainWebpack: config => {
    const APP_VERSION = `v${process.env.npm_package_version}`

    config.plugin('define')
      .tap(args => {
        let defineMap = args[0]
        let env = defineMap['process.env']
        env['APP_VERSION'] = JSON.stringify(APP_VERSION)
        return args
      })
  }
}
