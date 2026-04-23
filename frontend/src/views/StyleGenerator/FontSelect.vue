<template>
  <el-tooltip :content="$t('stylegen.fontSelectTip')">
    <el-select :value="innerValue" @input="onInnerInput" @visible-change="onSelectVisibleChange"
      multiple filterable allow-create default-first-option popper-class="font-select-popper" style="position: relative;"
    >
      <el-option-group
        v-for="(groupCfg, index) in [
          { fonts: recentFonts, label: $t('stylegen.recentFonts'), showSample: true, isRecent: true },
          { fonts: PRESET_FONTS, label: $t('stylegen.presetFonts'), showSample: true },
          { fonts: NETWORK_FONTS, label: $t('stylegen.networkFonts') },
          { fonts: localFonts, label: $t('stylegen.localFonts') },
        ]"
        :key="index"
        :label="groupCfg.label"
      >
        <!-- 留一个占位，不然model更新时显示的列表不会更新... -->
        <el-option v-if="groupCfg.fonts.length === 0" value="-" disabled></el-option>

        <template v-else>
          <template v-if="groupCfg.showSample">
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
          </template>

          <template v-else>
            <el-option v-for="font in groupCfg.fonts" :key="font" :value="font"></el-option>
          </template>
        </template>
      </el-option-group>
    </el-select>
  </el-tooltip>
</template>

<script>
import { ref } from 'vue'

import * as common from './common'
import * as fonts from './fonts'

let sharedRecentFonts = ref([]) // 这里只作为缓存，以localStorage为准
let sharedLocalFonts = ref([])

export default {
  name: 'FontSelect',
  props: {
    value: String
  },
  data() {
    return {
      PRESET_FONTS: fonts.PRESET_FONTS,
      NETWORK_FONTS: fonts.NETWORK_FONTS,

      innerValue: [],
    }
  },
  computed: {
    recentFonts() {
      return sharedRecentFonts.value
    },
    localFonts() {
      return sharedLocalFonts.value
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
    onSelectVisibleChange(visible) {
      if (!visible) {
        return
      }
      this.updateRecentFonts()
      this.updateLocalFonts()
    },

    updateRecentFonts() {
      sharedRecentFonts.value = this.getRecentFonts()
    },
    async updateLocalFonts() {
      sharedLocalFonts.value = await fonts.getLocalFonts()
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

<style>
.font-select-popper .el-select-dropdown__wrap {
  max-height: 500px;
}
</style>

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
