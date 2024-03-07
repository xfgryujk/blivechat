<template>
  <div>
    <div style="display: flex; align-items: center;">
      <h1 style="display: inline;">{{ $t('plugins.plugins') }}</h1>
      <el-button round icon="el-icon-question" class="push-inline-end" @click="isHelpVisible = true">{{
        $t('plugins.help')
      }}</el-button>
      <el-dialog :title="$t('plugins.help')" :visible.sync="isHelpVisible">
        <div style="word-break: initial;" v-html="$t('plugins.helpContent')"></div>
      </el-dialog>
    </div>

    <el-empty v-if="plugins.length === 0" description=""></el-empty>
    <el-row v-else :gutter="16">
      <el-col v-for="plugin in plugins" :key="plugin.id" :sm="24" :md="12">
        <el-card class="card">
          <div class="card-body">
            <div class="title-line">
              <h3 class="name">{{ plugin.name }}</h3>
              <span class="version">{{ plugin.version }}</span>
              <span class="author push-inline-end">{{ $t('plugins.author') }}{{ plugin.author }}</span>
            </div>
            <div class="description">{{ plugin.description }}</div>

            <div class="operations">
              <el-tooltip :content="$t('plugins.disabledByServer')" :disabled="serverConfig.enableAdminPlugins">
                <el-button type="primary" :disabled="!serverConfig.enableAdminPlugins || !plugin.isConnected"
                  :loading="getPluginCtx(plugin.id).isOperating" @click="adminPlugin(plugin)"
                >{{ $t('plugins.admin') }}</el-button>
              </el-tooltip>
              <el-tag v-if="plugin.isConnected" type="success" class="status push-inline-end">{{ $t('plugins.connected') }}</el-tag>
              <el-tag v-else type="danger" class="status push-inline-end">{{ $t('plugins.unconnected') }}</el-tag>
              <el-switch :value="plugin.enabled" :disabled="!serverConfig.enableAdminPlugins || getPluginCtx(plugin.id).isOperating"
                @change="enabled => setPluginEnabled(plugin, enabled)"
              ></el-switch>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as mainApi from '@/api/main'
import * as pluginsApi from '@/api/plugins'

export default {
  name: 'Plugins',
  data() {
    return {
      serverConfig: {
        enableAdminPlugins: true
      },
      isHelpVisible: false,
      plugins: [],
      pluginCtxMap: {},
    }
  },
  mounted() {
    this.updateServerConfig()
    this.updatePlugins()
  },
  methods: {
    getPluginCtx(pluginId) {
      let ctx = this.pluginCtxMap[pluginId]
      if (ctx === undefined) {
        ctx = {
          isOperating: false,
        }
        this.$set(this.pluginCtxMap, pluginId, ctx)
      }
      return ctx
    },
    async updateServerConfig() {
      try {
        this.serverConfig = (await mainApi.getServerInfo()).config
      } catch (e) {
        this.$message.error(`Failed to fetch server information: ${e}`)
        throw e
      }
    },
    async updatePlugins() {
      try {
        this.plugins = (await pluginsApi.getPlugins()).plugins
      } catch (e) {
        this.$message.error(`Failed to fetch plugins: ${e}`)
        throw e
      }
    },
    async adminPlugin(plugin) {
      let ctx = this.getPluginCtx(plugin.id)
      ctx.isOperating = true
      try {
        await pluginsApi.openAdminUi(plugin.id)
      } catch (e) {
        this.$message.error(`Request failed: ${e}`)
        throw e
      } finally {
        ctx.isOperating = false
      }
    },
    async setPluginEnabled(plugin, enabled) {
      let ctx = this.getPluginCtx(plugin.id)
      ctx.isOperating = true
      try {
        let res
        try {
          res = await pluginsApi.setEnabled(plugin.id, enabled)
        } catch (e) {
          this.$message.error(`Request failed: ${e}`)
          throw e
        }
        plugin.enabled = res.enabled
        if (!res.isSwitchSuccess) {
          this.$message.error(`Failed to switch the plugin: ${res.msg}`)
        }

        await new Promise(resolve => window.setTimeout(resolve, 3000))
        this.updatePlugins()
      } finally {
        ctx.isOperating = false
      }
    },
  }
}
</script>

<style scoped>
.push-inline-end {
  margin-inline-start: auto;
}

.card {
  margin-block-end: 16px;
}

.card-body {
  height: 200px;
  display: flex;
  flex-flow: column nowrap;
}

.title-line {
  margin-block-end: 1em;
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

.description {
  margin-block-end: 1em;
  flex: auto;
  overflow-y: auto;
}

.operations {
  flex: none;
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
}

.status {
  margin-inline-end: 8px;
}
</style>
