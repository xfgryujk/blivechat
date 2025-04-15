<template>
  <div>
    <el-radio-group :value="selectedIndex" @input="onSelect">
      <el-radio :label="INDEX_DEFAULT" border>
        <div class="card-body">
          <div class="title-line">
            <h3 class="name">{{ $t('home.templateDefaultTitle') }}</h3>
          </div>
          <div class="description-line">
            <div class="description">
              <p>{{ $t('home.templateDefaultDescription') }}</p>
            </div>
          </div>
        </div>
      </el-radio>

      <el-radio :label="INDEX_CUSTOM" border>
        <div class="card-body">
          <div class="title-line">
            <h3 class="name">{{ $t('home.templateCustomUrlTitle') }}</h3>
          </div>
          <div class="description-line">
            <div class="description">
              <p>{{ $t('home.templateCustomUrlDescription') }}</p>
            </div>
          </div>
          <div>
            <el-input v-model="customUrl" placeholder="https://example.com/path/to/you/template/index.html"></el-input>
          </div>
        </div>
      </el-radio>

      <el-radio v-for="(template, index) in templates" :key="template.id" :label="index" border>
        <div class="card-body">
          <div class="title-line">
            <h3 class="name">{{ template.name }}</h3>
            <span class="version">{{ template.version }}</span>
            <span class="author push-inline-end">{{ $t('home.author') }}{{ template.author }}</span>
          </div>
          <div class="description-line">
            <el-image v-if="template.thumbnail !== ''" class="thumbnail" lazy fit="cover" :src="template.thumbnail"></el-image>
            <div class="description">
              <p v-if="template.description !== ''">{{ template.description }}</p>
              <p>URL: {{ template.url }}</p>
            </div>
          </div>
        </div>
      </el-radio>
    </el-radio-group>
  </div>
</template>

<script>
import * as mainApi from '@/api/main'

const INDEX_DEFAULT = 'default'
const INDEX_CUSTOM = 'custom'

export default {
  name: 'TemplateSelect',
  props: {
    value: String
  },
  data() {
    return {
      INDEX_DEFAULT,
      INDEX_CUSTOM,

      templates: [],
      customUrl: '',
    }
  },
  computed: {
    selectedIndex() {
      if (this.value == '') {
        return INDEX_DEFAULT
      }
      let index = this.templates.findIndex(template => template.url === this.value)
      if (index !== -1) {
        return index
      }
      return INDEX_CUSTOM
    }
  },
  watch: {
    value: {
      immediate: true,
      handler(val) {
        if (this.selectedIndex === INDEX_CUSTOM) {
          this.customUrl = val
        }
      }
    },
    customUrl(val) {
      if (this.selectedIndex === INDEX_CUSTOM) {
        this.$emit('input', val)
      }
    }
  },
  mounted() {
    this.updateTemplates()
  },
  methods: {
    async updateTemplates() {
      try {
        this.templates = (await mainApi.getTemplates()).templates
      } catch (e) {
        this.$message.error(`Failed to fetch templates: ${e}`)
        throw e
      } finally {
        if (this.selectedIndex !== INDEX_CUSTOM) {
          this.customUrl = ''
        }
      }
    },
    onSelect(selectedIndex) {
      let url
      if (selectedIndex === INDEX_DEFAULT) {
        url = ''
      } else if (selectedIndex === INDEX_CUSTOM) {
        url = this.customUrl
      } else {
        url = this.templates[selectedIndex].url
      }
      this.$emit('input', url)
    }
  }
}
</script>

<style scoped>
.el-radio-group {
  display: block;
}

.el-radio {
  display: block;
  height: unset;
  margin: 0 0 16px 0 !important;
  padding: 20px;
}

.el-radio >>> .el-radio__input {
  display: none;
}

.el-radio >>> .el-radio__label {
  padding-left: unset;
}

.push-inline-end {
  margin-inline-start: auto;
}

.card-body {
  display: flex;
  flex-flow: column nowrap;
  gap: 1em;
}

.title-line {
  flex: none;
  display: flex;
  flex-flow: row nowrap;
  align-items: baseline;
  text-wrap: nowrap;
}

.name {
  margin-block: 0 0;
  margin-inline-end: 8px;
  display: inline;
}

.version {
  color: #909399;
}

.author {
  color: #606266;
}

.description-line {
  flex: none;
  display: flex;
  flex-flow: row nowrap;
  gap: 1em;
  max-height: 300px;
}

.thumbnail {
  flex: none;
  width: 190px;
  height: 105px;
}

.description {
  flex: auto;
  overflow-y: auto;
  text-wrap: wrap;
  word-wrap: break-word;
}

@media only screen and (max-width: 992px) {
  .description-line {
    flex-wrap: wrap;
    max-height: unset;
  }

  .thumbnail {
    max-width: 100%;
  }
}
</style>
