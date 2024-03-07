import axios from 'axios'

export async function getPlugins() {
  return (await axios.get('/api/plugin/plugins')).data
}

export async function setEnabled(pluginId, enabled) {
  return (await axios.post('/api/plugin/enable_plugin', {
    pluginId,
    enabled
  })).data
}

export async function openAdminUi(pluginId) {
  return (await axios.post('/api/plugin/open_admin_ui', { pluginId })).data
}
