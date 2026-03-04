// Test setup file for vitest
import { config } from '@vue/test-utils'
import ElementPlus from 'element-plus'

// Configure Vue Test Utils
config.global.plugins = [ElementPlus]
config.global.stubs = {
  teleport: true,
  transition: false
}
