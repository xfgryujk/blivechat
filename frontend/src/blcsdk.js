/** @module blcsdk */

(function(root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory)
  } else {
    root.blcsdk = factory()
  }
}(typeof self !== 'undefined' ? self : this, function() {
  const exports = {}

  const VERSION = '1.0.1'
  /**
   * 取SDK版本
   * @returns {string} "1.0.0"
   */
  function getVersion() {
    return VERSION
  }
  exports.getVersion = getVersion

  // 初始化消息的Promise {promise, resolve, reject}
  let initPromise = null
  // 初始化消息，包含版本、配置等信息
  let initMsg = null

  /**
   * 消息处理器
   * @type {MsgHandler}
   */
  let msgHandler = null
  /**
   * 用户设置的消息处理器
   * @type {MsgHandler}
   */
  let rawMsgHandler = null

  /**
   * @typedef InitOptions
   * @property {boolean} noMsgDelay 去掉消息延迟，但会导致消息不平滑
   * @property {boolean} noCssInjection 不注入OBS的自定义CSS和blivechat服务器预设CSS
   */

  let initOptions = {
    noCssInjection: false,
  }

  /**
   * 初始化SDK
   * 
   * 在调用除了{@link setMsgHandler}以外的其他接口之前必须先调用这个
   */
  async function init(
    /** @type {?InitOptions} */
    {noMsgDelay = false, noCssInjection = false} = {}
  ) {
    if (initPromise) {
      throw new Error('Cannot call init() again')
    }
    // initPromise = Promise.withResolvers()
    initPromise = {}
    initPromise.promise = new Promise((resolve, reject) => {
      initPromise.resolve = resolve
      initPromise.reject = reject
    })

    if (window.parent === window) {
      initPromise.reject(new Error('No parent window'))
      return initPromise.promise
    }

    initOptions.noCssInjection = noCssInjection

    msgHandler = noMsgDelay ? new SdkMsgHandler() : new SmoothedSdkMsgHandler()
    window.addEventListener('message', onWindowMessage)

    // 连接blivechat
    blcSendMsg('blcTemplateConnect')
    setTimeout(() => initPromise.reject(new Error('Timed out waiting for blcInit message')), 10 * 1000)

    // 等待初始化消息
    initMsg = await initPromise.promise
    console.debug('blcsdk initialized, initMsg=', initMsg)
  }
  exports.init = init

  /**
   * 设置消息处理器
   * @param {?MsgHandler} handler 消息处理器
   */
  function setMsgHandler(handler) {
    rawMsgHandler = handler
  }
  exports.setMsgHandler = setMsgHandler

  /**
   * 取blivechat前端版本
   * @returns {string} "v1.10.0-dev"
   */
  function getBlcVersion() {
    if (!initMsg) {
      throw new Error('Please call init() first')
    }
    return initMsg.blcVersion
  }
  exports.getBlcVersion = getBlcVersion

  /**
   * 取blivechat前端用的SDK版本。是父窗口用的版本，不是这个包的{@link getVersion}返回值
   * @returns {string} "1.0.0"
   */
  function getBlcSdkVersion() {
    if (!initMsg) {
      throw new Error('Please call init() first')
    }
    return initMsg.sdkVersion
  }
  exports.getBlcSdkVersion = getBlcSdkVersion

  /**
   * @typedef Config
   * @property {boolean} showGiftName 显示礼物名
   * @property {boolean} mergeSimilarDanmaku 合并相似弹幕
   * @property {boolean} mergeGift 合并礼物
   * @property {number} maxNumber 最大弹幕数
   */

  /**
   * 取blivechat前端房间部分配置
   * @returns {Config}
   */
  function getConfig() {
    if (!initMsg) {
      throw new Error('Please call init() first')
    }
    return Object.freeze(initMsg.config)
  }
  exports.getConfig = getConfig

  function blcSendMsg(type, data = null) {
    if (window.parent === window) {
      return
    }
    let msg = { type, data }
    window.parent.postMessage(msg, '*')
  }

  function onWindowMessage(event) {
    if (event.source !== window.parent) {
      return
    }

    let { type, data } = event.data
    switch (type) {
    case 'blcAddMsg':
      msgHandler.addMsg(data)
      break
    case 'blcUpdateMsg':
      msgHandler.updateMsg(data.id, data.newValuesObj)
      break
    case 'blcDelMsgs':
      msgHandler.delMsgs(data.ids)
      break

    case 'blcInit':
      initPromise.resolve(data)
      break
    case 'blcInjectCss':
      injectCss(data)
      break
    }
  }

  function injectCss({injectCssUrls = [], injectCss = ''}) {
    if (initOptions.noCssInjection) {
      return
    }

    for (let url of injectCssUrls) {
      let el = document.createElement('link')
      el.rel = 'stylesheet'
      el.href = url
      document.head.appendChild(el)
    }

    if (injectCss !== '') {
      let el = document.createElement('style')
      el.textContent = injectCss
      document.head.appendChild(el)
    }
  }

  /** 模板消息处理器接口 */
  class MsgHandler {
    /**
     * 添加消息
     * @param {AnyDisplayMsg} msg
     */
    addMsg(msg) {}

    /**
     * 删除消息，主要用于撤回醒目留言
     * @param {string[]} ids 要删除的消息ID
     */
    delMsgs(ids) {}

    /**
     * 更新消息字段，主要用于更新翻译结果
     * @param {string} id 要更新的消息ID
     * @param {Object} newValuesObj 字段和对应的新值
     */
    updateMsg(id, newValuesObj) {}
  }
  exports.MsgHandler = MsgHandler

  class SdkMsgHandler extends MsgHandler {
    addMsg(msg) { this._callRawHandler('addMsg', msg) }
    delMsgs(ids) { this._callRawHandler('delMsgs', ids) }
    updateMsg(id, newValuesObj) { this._callRawHandler('updateMsg', id, newValuesObj) }
    _callRawHandler(...args) { doCallRawHandler(...args) }
  }

  function doCallRawHandler(funcName, ...args) {
    if (!rawMsgHandler) {
      return
    }
    try {
      let func = rawMsgHandler[funcName]
      return func.call(rawMsgHandler, ...args)
    } catch (e) {
      console.error(e)
    }
  }

  // 发送消息时间间隔范围
  const MSG_MIN_INTERVAL = 80
  const MSG_MAX_INTERVAL = 1000

  class SmoothedSdkMsgHandler extends SdkMsgHandler {
    constructor() {
      super()
      // 消息队列
      this._queue = []
      // 消费消息队列的定时器ID
      this._emitSmoothedMsgTimerId = null
      // 最近进队列的时间间隔，用来估计下次进队列的时间
      this._enqueueIntervals = []
      // 上次进队列的时间
      this._lastEnqueueTime = null
      // 估计的下次进队列时间间隔
      this._estimatedEnqueueInterval = null

      this._boundEmitSmoothedMsgs = this._emitSmoothedMsgs.bind(this)
    }

    _callRawHandler(funcName, ...args) {
      let msg = {funcName, args}
      this._enqueueMsg(msg)
    }

    _enqueueMsg(msg) {
      // 估计进队列时间间隔
      if (!this._lastEnqueueTime) {
        this._lastEnqueueTime = new Date()
      } else {
        let curTime = new Date()
        let interval = curTime - this._lastEnqueueTime
        // 真实的进队列时间间隔模式大概是这样：2500, 300, 300, 300, 2500, 300, ...
        // B站消息有缓冲，会一次发多条消息。这里把波峰视为发送了一次真实的WS消息，所以要过滤掉间隔太小的
        if (interval > 1000 || this._enqueueIntervals.length < 5) {
          this._enqueueIntervals.push(interval)
          if (this._enqueueIntervals.length > 5) {
            this._enqueueIntervals.splice(0, this._enqueueIntervals.length - 5)
          }
          // 这边估计得尽量大，只要不太早把消息缓冲发完就是平滑的。有MESSAGE_MAX_INTERVAL保底，不会让消息延迟太大
          // 其实可以用单调队列求最大值，偷懒不写了
          this._estimatedEnqueueInterval = Math.max(...this._enqueueIntervals)
        }
        // 上次入队时间还是要设置，否则会太早把消息缓冲发完，然后较长时间没有新消息
        this._lastEnqueueTime = curTime
      }

      this._queue.push(msg)

      if (!this._emitSmoothedMsgTimerId) {
        this._emitSmoothedMsgTimerId = setTimeout(this._boundEmitSmoothedMsgs)
      }
    }

    _emitSmoothedMsgs() {
      this._emitSmoothedMsgTimerId = null
      if (this._queue.length <= 0) {
        return
      }

      // 估计的下次进队列剩余时间
      let estimatedNextEnqueueRemainTime = 10 * 1000
      if (this._estimatedEnqueueInterval) {
        estimatedNextEnqueueRemainTime = Math.max(this._lastEnqueueTime - new Date() + this._estimatedEnqueueInterval, 1)
      }
      // 计算发送的消息数，保证在下次进队列之前发完
      // 下次进队列之前应该发多少条消息
      let shouldEmitNum = Math.max(this._queue.length, 0)
      // 下次进队列之前最多能发多少次
      let maxCanEmitCount = estimatedNextEnqueueRemainTime / MSG_MIN_INTERVAL
      // 这次发多少条消息
      let numToEmit
      if (shouldEmitNum < maxCanEmitCount) {
        // 队列中消息数很少，每次发1条也能发完
        numToEmit = 1
      } else {
        // 每次发1条以上，保证按最快速度能发完
        numToEmit = Math.ceil(shouldEmitNum / maxCanEmitCount)
      }

      // 发消息
      let msgs = this._queue.splice(0, numToEmit)
      for (let msg of msgs) {
        doCallRawHandler(msg.funcName, ...msg.args)
      }

      if (this._queue.length <= 0) {
        return
      }
      // 消息没发完，计算下次发消息时间
      let sleepTime
      if (numToEmit === 1) {
        // 队列中消息数很少，随便定个[MESSAGE_MIN_INTERVAL, MESSAGE_MAX_INTERVAL]的时间
        sleepTime = estimatedNextEnqueueRemainTime / this._queue.length
        sleepTime *= 0.5 + Math.random()
        if (sleepTime > MSG_MAX_INTERVAL) {
          sleepTime = MSG_MAX_INTERVAL
        } else if (sleepTime < MSG_MIN_INTERVAL) {
          sleepTime = MSG_MIN_INTERVAL
        }
      } else {
        // 按最快速度发
        sleepTime = MSG_MIN_INTERVAL
      }
      this._emitSmoothedMsgTimerId = setTimeout(this._boundEmitSmoothedMsgs, sleepTime)
    }
  }

  /**
   * 消息类型
   * @enum {number}
   */
  const MsgType = Object.freeze({
    /** 评论 @see TextMsg */
    TEXT: 0,
    /** 礼物 @see GiftMsg */
    GIFT: 1,
    /** 上舰 @see MemberMsg */
    MEMBER: 2,
    /** 醒目留言 @see SuperChatMsg */
    SUPER_CHAT: 3,
  })
  exports.MsgType = MsgType

  /**
   * 作者类型
   * @enum {number}
   */
  const AuthorType = Object.freeze({
    NORMAL: 0,
    /** 舰队 */
    MEMBER: 1,
    /** 房管 */
    ADMIN: 2,
    /** 主播 */
    OWNER: 3,
  })
  exports.AuthorType = AuthorType

  /**
   * 舰队等级。因为历史原因，消息里的字段名叫`privilegeType`
   * @enum {number}
   */
  const GuardLevel = Object.freeze({
    NONE: 0,
    /** 总督 */
    LV3: 1,
    /** 提督 */
    LV2: 2,
    /** 舰长 */
    LV1: 3,
  })
  exports.GuardLevel = GuardLevel

  /**
   * 一段内容的类型
   * @enum {number}
   */
  const ContentPartType = Object.freeze({
    /** 文本 */
    TEXT: 0,
    /** 图片 */
    IMAGE: 1,
  })
  exports.ContentPartType = ContentPartType

  //
  // 以下只用于类型注解，运行时没什么用
  //

  /**
   * 用于显示的消息
   * @typedef {TextMsg | GiftMsg | MemberMsg | SuperChatMsg} AnyDisplayMsg
   */

  /**
   * 评论消息。因为历史原因叫TextMsg，实际上会包含表情图片
   * @typedef TextMsg
   * @property {string} id 消息ID
   * @property {MsgType} type 消息类型
   * @property {string} avatarUrl 用户头像URL
   * @property {Date} time 时间
   * @property {string} authorName 用户名
   * @property {AuthorType} authorType 用户类型
   * @property {string} content 纯文本表示的内容
   * @property {AnyContentPart[]} contentParts 解析后的内容，包括文本、图片
   * @property {GuardLevel} privilegeType 舰队等级
   * @property {string} translation 内容的翻译，刚添加时一般是空的，之后通过更新消息赋值
   * @property {string} uid 用户Open ID或ID，使用房间ID连接时不保证是唯一的
   * @property {number} medalLevel 勋章等级，如果没戴当前房间勋章则为0
   * @property {string} medalName 勋章名，如果没戴当前房间勋章则为空字符串
   */
  exports.TextMsg = /** @type {TextMsg} */ (undefined)

  /**
   * 一段内容
   * @typedef {TextContentPart | ImageContentPart} AnyContentPart
   */
  /**

  * 一段文本内容
   * @typedef TextContentPart
   * @property {ContentPartType} type 内容类型
   * @property {string} text 内容
   */

  /**
   * 一段图片内容
   * @typedef ImageContentPart
   * @property {ContentPartType} type 内容类型
   * @property {string} text 纯文本表示的内容
   * @property {string} url 图片URL
   * @property {number} width 宽度，加载失败则为0
   * @property {number} height 高度，加载失败则为0
   */

  /**
   * 礼物消息
   * @typedef GiftMsg
   * @property {string} id 消息ID
   * @property {MsgType} type 消息类型
   * @property {string} avatarUrl 用户头像URL
   * @property {Date} time 时间
   * @property {string} authorName 用户名
   * @property {string} authorNamePronunciation 用户名读音
   * @property {number} price 总价（元），免费礼物则为0
   * @property {string} giftName 礼物名
   * @property {number} num 数量
   * @property {number} totalFreeCoin 免费礼物总价（银瓜子数），付费礼物则为0
   * @property {number} giftId 礼物ID
   * @property {string} giftIconUrl 礼物图标URL
   * @property {string} uid 用户Open ID或ID，使用房间ID连接时不保证是唯一的
   * @property {GuardLevel} privilegeType 舰队等级
   * @property {number} medalLevel 勋章等级，如果没戴当前房间勋章则为0
   * @property {string} medalName 勋章名，如果没戴当前房间勋章则为空字符串
   */
  exports.GiftMsg = /** @type {GiftMsg} */ (undefined)

  /**
   * 上舰消息
   * @typedef MemberMsg
   * @property {string} id 消息ID
   * @property {MsgType} type 消息类型
   * @property {string} avatarUrl 用户头像URL
   * @property {Date} time 时间
   * @property {string} authorName 用户名
   * @property {string} authorNamePronunciation 用户名读音
   * @property {GuardLevel} privilegeType 舰队等级
   * @property {number} num 数量
   * @property {string} unit 单位（"月"）
   * @property {number} price 总价（元）
   * @property {string} uid 用户Open ID或ID，使用房间ID连接时不保证是唯一的
   * @property {number} medalLevel 勋章等级，如果没戴当前房间勋章则为0
   * @property {string} medalName 勋章名，如果没戴当前房间勋章则为空字符串
   */
  exports.MemberMsg = /** @type {MemberMsg} */ (undefined)

  /**
   * 醒目留言消息
   * @typedef SuperChatMsg
   * @property {string} id 消息ID
   * @property {MsgType} type 消息类型
   * @property {string} avatarUrl 用户头像URL
   * @property {Date} time 时间
   * @property {string} authorName 用户名
   * @property {string} authorNamePronunciation 用户名读音
   * @property {number} price 价格（元）
   * @property {string} content 内容
   * @property {string} translation 内容的翻译，刚添加时一般是空的，之后通过更新消息赋值
   * @property {string} uid 用户Open ID或ID，使用房间ID连接时不保证是唯一的
   * @property {GuardLevel} privilegeType 舰队等级
   * @property {number} medalLevel 勋章等级，如果没戴当前房间勋章则为0
   * @property {string} medalName 勋章名，如果没戴当前房间勋章则为空字符串
   */
  exports.SuperChatMsg = /** @type {SuperChatMsg} */ (undefined)

  return exports
}))
