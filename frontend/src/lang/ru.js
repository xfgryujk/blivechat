export default {
  sidebar: {
    home: 'Домой',
    stylegen: 'Генератор стилей',
    help: 'Помощь',
    projectAddress: 'Адрес проекта',
    giftRecordOfficial: 'Официальная запись Суперчата',
    giftRecord: 'Запись Суперчата'
  },
  home: {
    roomIdEmpty: "ID комнаты не может быть пустым",
    roomIdInteger: 'ID комнаты должен быть положительным целым числом.',

    general: 'Общее',
    roomId: 'ID комнаты',
    showDanmaku: 'Показать сообщения',
    showGift: 'Показать суперчаты',
    showGiftName: 'Показать название подарка',
    mergeSimilarDanmaku: 'Объединить похожие сообщения',
    mergeGift: 'Объединить подарки',
    minGiftPrice: 'Минимальная цена суперчатов для показа (CNY)',
    maxNumber: 'Максимальное количество сообщений',

    block: 'Блокировать',
    giftDanmaku: 'Блокировать системные сообщения (эффект подарка)',
    blockLevel: 'Заблокировать уровень пользователя ниже, чем',
    informalUser: 'Блокировать неформальных пользователей',
    unverifiedUser: 'Блокировать непроверенных пользователей',
    blockKeywords: 'Заблокировать ключевые слова',
    onePerLine: 'По одному на строку',
    blockUsers: 'Заблокировать пользователей',
    blockMedalLevel: 'Уровень медали блока ниже, чем',

    advanced: 'Продвинутый',
    autoTranslate: 'Автоматический перевод сообщений на японский язык',

    roomUrl: 'URL комнаты',
    copy: 'Копировать',
    enterRoom: 'Войти в комнату',
    exportConfig: 'Конфигурация экспорта',
    importConfig: 'Конфигурация импорта',

    failedToParseConfig: 'Не удалось разобрать конфигурацию: '
  },
  stylegen: {
    outlines: 'Контуры',
    showOutlines: 'Показать контуры',
    outlineSize: 'Размер контура',
    outlineColor: 'Цвет контура',

    avatars: 'Аватары',
    showAvatars: 'Показать аватары',
    avatarSize: 'Размер аватара',

    userNames: 'Имена пользователей',
    font: 'Шрифт',
    fontSize: 'Размер шрифта',
    lineHeight: 'Высота строки (0 по умолчанию)',
    normalColor: 'Нормальный цвет',
    ownerColor: 'Цвет владельца',
    moderatorColor: 'Цвет модератора',
    memberColor: 'Цвет элемента',
    showBadges: 'Показать значки',
    showColon: 'Показывать двоеточие после имени',

    messages: 'Сообщения',
    color: 'цвет',
    onNewLine: 'На новой линии',

    time: 'Отметки времени',
    showTime: 'Показать отметки времени',

    backgrounds: 'Фоны',
    bgColor: 'Фоновый цвет',
    useBarsInsteadOfBg: 'Используйте полосы вместо фона',
    messageBgColor: 'Цвет фона сообщения',
    ownerMessageBgColor: 'Цвет фона владельца',
    moderatorMessageBgColor: 'Цвет фона модератораЦвет фона элемента',
    memberMessageBgColor: 'Цвет фона элемента',

    scAndNewMember: 'Суперчат / Новый участник',
    firstLineFont: 'Шрифт первой строки',
    firstLineFontSize: 'Размер шрифта первой строки',
    firstLineLineHeight: 'Высота первой строки (0 по умолчанию)',
    firstLineColor: 'Цвет первой строки',
    secondLineFont: 'Шрифт второй строки',
    secondLineFontSize: 'Размер шрифта второй строки',
    secondLineLineHeight: 'Высота второй строки (по умолчанию 0)',
    secondLineColor: 'Цвет второй линии',
    scContentLineFont: 'Шрифт содержимого Суперчата',
    scContentLineFontSize: 'Размер шрифта содержимого Суперчата',
    scContentLineLineHeight: 'Высота строки контента Суперчата (0 по умолчанию)',
    scContentLineColor: 'Цвет содержания Суперчата',
    showNewMemberBg: 'Показать фон нового участника',
    showScTicker: 'Показать тикер Суперчата',
    showOtherThings: 'Показать все, кроме тикера Суперчата',

    animation: 'Анимация',
    animateIn: 'Анимировать в',
    fadeInTime: 'Время исчезновения (миллисекунды)',
    animateOut: 'Анимировать (удалить старые сообщения)',
    animateOutWaitTime: 'Время ожидания (секунды)',
    fadeOutTime: 'Время исчезновения (миллисекунды)',
    slide: 'слайд',
    reverseSlide: 'Обратный слайд',
    playAnimation: 'Воспроизвести анимацию',

    result: 'Результат',
    copy: 'Копировать',
    resetConfig: 'Сбросить конфигурацию'
  },
  help: {
    help: 'Помощь',
    p1: '1. Copy the room ID from the Bilibili live room webpage',
    p2: '2. Введите идентификатор комнаты в идентификатор комнаты на главной странице.  Скопируйте URL комнаты',
    p3: '3. Создавайте стили с помощью генератора стилей.  Скопируйте CSS',
    p4: '4. Добавьте исходный код браузера в OBS.',
    p5: '5. Введите ранее скопированный URL комнаты в URL и введите ранее скопированный CSS в пользовательский CSS'
  }
}
