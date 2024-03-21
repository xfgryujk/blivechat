<template>
  <el-tooltip :content="$t('stylegen.fontSelectTip')">
    <el-select multiple :value="inputVal" popper-class="font-select-popper" @visible-change="updateNativeFonts"
      @input="handlerSelectInput" filterable allow-create default-first-option :style="`position:relative;`">
      <el-option-group :label="$t('stylegen.nativeFont')">
        <el-option v-for=" font in NATIVE_FONTS" :key="font" :value="font">
          <span class="fonts-select-span-title">
            <span :style="`font-family:${font}`">{{ font }} </span>
            <el-link :underline="false" type="primary" class="fonts-select-btn"
              @click.stop="() => handlerNativeBtnDelete(font)"><i class="el-icon-delete">&nbsp;</i></el-link>
          </span>
          <span :style="`font-family:${font};`" class="fonts-select-span-sample">{{ $t('stylegen.sampleText') }}</span>
        </el-option>
      </el-option-group>
      <el-option-group :label="$t('stylegen.localFont')">
        <el-option v-for="font in LOCAL_FONTS" :key="font" :value="font">
          <span class="fonts-select-span-title">
            <span :style="`font-family:${font}`">{{ font }} </span>
          </span>
          <span :style="`font-family:${font};`" class="fonts-select-span-sample">{{ $t('stylegen.sampleText') }}</span>
        </el-option>
      </el-option-group>
      <el-option-group :label="$t('stylegen.webFont')">
        <el-option v-for="font in NETWORK_FONTS" :key="font" :value="font"></el-option>
      </el-option-group>
    </el-select>
  </el-tooltip>
</template>

<script>
import * as fonts from './fonts'

export default {
  name: 'FontSelect',
  props: {
    value: String
  },
  data() {
    return {
      inputVal: undefined,
      nativeFontsLocalStorageName: 'blivechatNativeFontsName',
      NATIVE_FONTS: Array,
      LOCAL_FONTS: fonts.LOCAL_FONTS,
      NETWORK_FONTS: fonts.NETWORK_FONTS
    }
  },
  methods: {
    updateNativeFonts() {
      this.NATIVE_FONTS = this.getNativeFontNames()
    },

    isNewNativeFont(fontName) {
      if (this.LOCAL_FONTS.includes(fontName)) {
        return false
      }
      if (this.NETWORK_FONTS.includes(fontName)) {
        return false
      }
      if (this.NATIVE_FONTS.includes(fontName)) {
        return false
      }
      return true
    },

    getNativeFontNames() {
      let nativeFontsNameStr = localStorage.getItem(this.nativeFontsLocalStorageName)
      if (nativeFontsNameStr && nativeFontsNameStr.length > 0) {
        return nativeFontsNameStr.split(',')
      } else {
        return []
      }
    },

    addNativeFontNames(fontName) {
      let nativeFontsNameArr = this.getNativeFontNames()
      nativeFontsNameArr.push(fontName)
      localStorage.setItem(this.nativeFontsLocalStorageName, nativeFontsNameArr.join(','))
    },

    deleteNativeFontNames(fontName) {
      let nativeFontsNameArr = this.getNativeFontNames()
      let _index = nativeFontsNameArr.indexOf(fontName)
      if (_index != -1) {
        let newNativeFontsNameArr = nativeFontsNameArr.filter((_, index) => index != _index)
        localStorage.setItem(this.nativeFontsLocalStorageName, newNativeFontsNameArr.join(','))
        this.updateNativeFonts()
      }
    },

    handlerNativeBtnDelete(fontName) {
      this.deleteNativeFontNames(fontName)
    },

    handlerSelectInput(value) {
      for (let item of value) {
        if (this.isNewNativeFont(item)) {
          this.addNativeFontNames(item)
          this.updateNativeFonts()
        }
      }
      this.inputVal = value
    }
  },
  watch: {
    inputVal(newVal) {
      this.$emit('input', newVal.join(','))
    },
  },
  created() {
    this.NATIVE_FONTS = this.getNativeFontNames()
  }
}
</script>

<style scoped>
.el-select {
  width: 100%
}

.font-select-popper .el-select-group .el-select-dropdown__item {
  display: flex;
  padding: 8px 20px;
  flex-direction: column;
  height: fit-content;
}

.fonts-select-span-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  line-height: 1.5;
}

.fonts-select-btn {
  opacity: 0.2;
  transition: .5s;
  padding: 0 0 0 8px;
  margin-right: 20px;

}

.fonts-select-btn:hover {
  opacity: 1;
}

.fonts-select-span-sample {
  opacity: 0.4;
  line-height: 1.5;
}
</style>
