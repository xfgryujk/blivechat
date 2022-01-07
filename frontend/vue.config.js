module.exports = {
  chainWebpack: config => {
    const APP_VERSION = process.env.npm_package_version

    config.plugin('define')
      .tap(args => {
        let defineMap = args[0]
        let env = defineMap['process.env']
        env['APP_VERSION'] = JSON.stringify(APP_VERSION)
        return args
      })
  }
}
