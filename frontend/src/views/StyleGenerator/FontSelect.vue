<template>
  <el-select :value="value" @input="val => $emit('input', val)" filterable allow-create default-first-option>
    <el-option-group>
      <el-option v-for="font in LOCAL_FONTS" :key="font" :value="font"></el-option>
    </el-option-group>
    <el-option-group>
      <el-option v-for="font in NETWORK_FONTS" :key="font" :value="font"></el-option>
    </el-option-group>
  </el-select>
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
      LOCAL_FONTS: fonts.LOCAL_FONTS,
      NETWORK_FONTS: fonts.NETWORK_FONTS
    }
  }
}
</script>

<style scoped>
.el-select {
  width: 100%
}
</style>
