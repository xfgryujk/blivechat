<template>
  <el-tooltip :content="$t('stylegen.fontSelectTip')">
    <el-select :value="innerValue" @input="onInnerInput" @visible-change="updateRecentFonts"
      multiple filterable allow-create default-first-option popper-class="font-select-popper" style="position: relative;"
    >
      <el-option-group
        v-for="(groupCfg, index) in [
          { fonts: recentFonts, label: $t('stylegen.recentFonts'), isRecent: true },
          { fonts: PRESET_FONTS, label: $t('stylegen.presetFonts') },
        ]"
        :key="index"
        :label="groupCfg.label"
      >
        <el-option v-for="font in groupCfg.fonts" :key="font" :value="font">
          <span class="fonts-select-name-line">
            <span>{{ font }}</span>
            <el-button v-if="groupCfg.isRecent" type="text" class="fonts-select-btn" style="color: #f56c6c;"
              @click="() => deleteRecentFont(font)"
            >
              <i class="el-icon-delete"></i>
            </el-button>
          </span>
          <span class="fonts-select-sample" :style="{'font-family': font}">Sample 样例 サンプル</span>
        </el-option>
      </el-option-group>

      <el-option-group :label="$t('stylegen.networkFonts')">
        <el-option v-for="font in NETWORK_FONTS" :key="font" :value="font"></el-option>
      </el-option-group>
    </el-select>
  </el-tooltip>
</template>

<script>
import * as common from './common'
import * as fonts from './fonts'

export default {
  name: 'FontSelect',
  props: {
    value: String
  },
  data() {
    return {
      recentFonts: this.getRecentFonts(), // 这里只作为缓存，以localStorage为准
      PRESET_FONTS: fonts.PRESET_FONTS,
      NETWORK_FONTS: fonts.NETWORK_FONTS,

      innerValue: [],
    }
  },
  watch: {
    value: {
      immediate: true,
      handler(val) {
        this.innerValue = common.fontsStrToArr(val)
      }
    }
  },
  methods: {
    onInnerInput(val) {
      let addedFonts = val.filter(font => this.innerValue.indexOf(font) === -1)

      this.innerValue = val
      this.$emit('input', common.fontsArrToStr(this.innerValue))

      for (let font of addedFonts) {
        this.addRecentFont(font)
      }
    },
    updateRecentFonts() {
      this.recentFonts = this.getRecentFonts()
    },

    getRecentFonts() {
      return common.fontsStrToArr(window.localStorage.recentFonts || '')
    },
    setRecentFonts(recentFonts) {
      window.localStorage.recentFonts = common.fontsArrToStr(recentFonts)
    },
    addRecentFont(font) {
      let recentFonts = this.getRecentFonts()
      let index = recentFonts.indexOf(font)
      if (index !== -1) {
        recentFonts.splice(index, 1)
      }
      recentFonts.unshift(font)

      this.setRecentFonts(recentFonts)
      this.updateRecentFonts()
    },
    deleteRecentFont(font) {
      let recentFonts = this.getRecentFonts()
      let index = recentFonts.indexOf(font)
      if (index !== -1) {
        recentFonts.splice(index, 1)
        this.setRecentFonts(recentFonts)
      }
      this.updateRecentFonts()
    }
  }
}
</script>

<style scoped>
.el-select {
  width: 100%;
}

.font-select-popper .el-select-group .el-select-dropdown__item {
  display: flex;
  flex-direction: column;
  padding: 8px 20px;
  height: fit-content;
}

.fonts-select-name-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  line-height: 1.5em;
}

.fonts-select-btn {
  opacity: 0.2;
  transition: 0.5s;
  padding: 0 0 0 8px;
  margin-right: 20px;
}

.fonts-select-btn:hover {
  opacity: 1;
}

.fonts-select-sample {
  opacity: 0.4;
  line-height: 1.5em;
}
</style>
