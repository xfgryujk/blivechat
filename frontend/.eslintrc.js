module.exports = {
  "root": true,
  "env": {
    "browser": true,
    "node": true
  },
  "parserOptions": {
    "parser": "@babel/eslint-parser"
  },
  "extends": [
    "plugin:vue/essential",
    "eslint:recommended"
  ],
  "rules": {
    "array-bracket-spacing": ["error", "never"], // 数组括号内不加空格
    "arrow-parens": ["error", "as-needed"], // 箭头函数单个参数不加括号
    "arrow-spacing": "error", // 箭头前后加空格
    "block-spacing": "error", // 块大括号内加空格
    "brace-style": "error", // 大括号不独占一行
    "comma-spacing": "error", // 逗号前面不加空格，后面加空格
    "comma-style": "error", // 逗号在语句后面而不是下一条的前面
    "computed-property-spacing": "error", // 计算属性名前后不加空格
    "curly": "error", // 禁止省略大括号
    "dot-notation": "error", // 使用点访问成员
    "eol-last": "error", // 文件末尾加换行符
    "func-call-spacing": "error", // 调用函数名和括号间不加空格
    "func-style": ["error", "declaration", { "allowArrowFunctions": true }], // 使用函数定义语法，而不是把函数表达式赋值到变量
    "indent": ["error", 2], // 缩进2空格
    "key-spacing": ["error", { "mode": "minimum" }],
    "keyword-spacing": "error", // 关键词前后加空格
    "lines-between-class-members": "error", // 类成员定义间加空格
    "max-lines-per-function": ["error", 150], // 每个函数最多行数
    "max-nested-callbacks": ["error", 3], // 每个函数最多嵌套回调数
    "new-parens": "error", // new调用构造函数加空格
    "no-array-constructor": "error", // 使用数组字面量，而不是数组构造函数
    "no-floating-decimal": "error", // 禁止省略浮点数首尾的0
    "no-implicit-coercion": "error", // 禁止隐式转换
    "no-empty": ["error", { "allowEmptyCatch": true }], // 禁止空的块，除了catch
    "no-extra-parens": ["error", "all", { "nestedBinaryExpressions": false }], // 禁止多余的括号
    "no-labels": "error", // 禁止使用标签
    "no-lone-blocks": "error", // 禁止没用的块
    "no-mixed-operators": "error", // 禁止混用不同优先级的操作符而不加括号
    "no-multi-spaces": ["error", { "ignoreEOLComments": true }], // 禁止多个空格，除了行尾注释前
    "no-multiple-empty-lines": "error", // 最多2个连续空行
    "no-nested-ternary": "error", // 禁止嵌套三元表达式
    "no-sequences": "error", // 禁止使用逗号操作符
    "no-tabs": "error", // 禁止使用tab
    "no-trailing-spaces": ["error", { "skipBlankLines": true }], // 禁止行尾的空格，除了空行
    "no-unused-expressions": "error", // 禁止没用的表达式
    "no-useless-concat": "error", // 禁止没用的字符串连接
    "no-useless-rename": "error", // 禁止没用的模块导入重命名、解构赋值重命名
    "no-useless-return": "error", // 禁止没用的return
    "no-var": "error", // 禁止使用var声明变量
    "no-void": "error", // 禁止使用void
    "no-whitespace-before-property": "error", // 禁止访问属性的点前后加空格
    "object-curly-spacing": ["error", "always"], // 对象字面量括号内加空格
    "operator-assignment": "error", // 尽量使用+=
    "operator-linebreak": ["error", "before"], // 操作符放行首
    "prefer-object-spread": "error", // 使用{...obj}，而不是Object.assign
    "prefer-rest-params": "error", // 使用...args，而不是arguments
    "prefer-spread": "error", // 使用func(...args)，而不是apply
    "prefer-template": "error", // 使用模板字符串，而不是字符串连接
    "rest-spread-spacing": ["error", "never"], // 解包操作符不加空格
    "semi": ["error", "never"], // 禁止使用多余的分号
    "semi-spacing": "error", // 分号前面不加空格，后面加空格
    "semi-style": "error", // 分号在语句后面而不是下一条的前面
    "space-before-blocks": "error", // 块大括号前加空格
    "space-before-function-paren": ["error", "never"], // 函数定义名称和括号间不加空格
    "space-in-parens": "error", // 括号内不加空格
    "space-infix-ops": "error", // 二元操作符前后加空格
    "space-unary-ops": "error", // 关键词一元操作符后加空格，符号一元操作符不加
    "spaced-comment": ["error", "always", { "block": { "balanced": true } }], // 注释前面加空格
    "template-curly-spacing": "error", // 模板字符串中变量大括号内不加空格

    "no-shadow": "warn", // 变量名和外部作用域重复

    "no-console": "off", // 线上尽量不要用console输出，看不到的

    "vue/multi-word-component-names": "off", // Vue组件名允许用1个单词
  }
}
