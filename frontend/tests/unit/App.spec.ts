import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import App from '@/App.vue'
import axios from 'axios'

vi.mock('axios')

describe('App.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders properly', () => {
    const wrapper = mount(App)
    expect(wrapper.text()).toContain('InnovateOS Klipper Installer')
  })

  it('detects board on mount', async () => {
    const mockBoard = {
      board: 'STM32F103',
      interface: 'serial',
      port: '/dev/ttyUSB0'
    }

    vi.mocked(axios.get).mockResolvedValueOnce({ data: mockBoard })

    const wrapper = mount(App)
    await wrapper.vm.$nextTick()

    expect(axios.get).toHaveBeenCalledWith('/api/detect-board')
    expect(wrapper.vm.board).toEqual(mockBoard)
  })

  it('handles board detection error', async () => {
    vi.mocked(axios.get).mockRejectedValueOnce(new Error('Detection failed'))

    const wrapper = mount(App)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.error).toBe('Board detection failed')
  })

  it('starts installation', async () => {
    const mockResponse = {
      status: 'started',
      install_id: 'abc123'
    }

    vi.mocked(axios.post).mockResolvedValueOnce({ data: mockResponse })

    const wrapper = mount(App)
    await wrapper.vm.startInstallation()

    expect(axios.post).toHaveBeenCalledWith('/api/install', {
      printer_id: wrapper.vm.selectedPrinter,
      webInterface_id: wrapper.vm.selectedInterface
    })
    expect(wrapper.vm.installId).toBe('abc123')
  })

  it('handles WebSocket messages', async () => {
    const wrapper = mount(App)
    const mockMessage = {
      type: 'status',
      data: {
        progress: 50,
        message: 'Installing...'
      }
    }

    // Simuliere eine WebSocket-Nachricht
    wrapper.vm.handleWebSocketMessage({ data: JSON.stringify(mockMessage) })

    expect(wrapper.vm.progress).toBe(50)
    expect(wrapper.vm.status).toBe('Installing...')
  })
})
