<template>
  <el-select :value="value" @input="val => $emit('input', val)">
    <el-option label="100 Thin" :value="100"></el-option>
    <el-option label="200 ExtraLight" :value="200"></el-option>
    <el-option label="300 Light" :value="300"></el-option>
    <el-option label="400 Regular" :value="400"></el-option>
    <el-option label="500 Medium" :value="500"></el-option>
    <el-option label="600 SemiBold" :value="600"></el-option>
    <el-option label="700 Bold" :value="700"></el-option>
    <el-option label="800 ExtraBold" :value="800"></el-option>
    <el-option label="900 Black" :value="900"></el-option>
  </el-select>
</template>

<script>
export default {
  name: 'FontWeightSelect',
  props: {
    value: Number
  },
}
</script>

<style scoped>
.el-select {
  width: 100%;
}
</style>
