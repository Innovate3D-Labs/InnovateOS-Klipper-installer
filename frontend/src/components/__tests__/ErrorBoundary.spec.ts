import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ErrorBoundary from '../ErrorBoundary.vue'
import { createTestingPinia } from '@pinia/testing'
import { useMainStore } from '@/store'

// Mock router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}))

describe('ErrorBoundary', () => {
  const createWrapper = (props = {}) => {
    return mount(ErrorBoundary, {
      props: {
        shouldReset: true,
        ...props
      },
      global: {
        plugins: [createTestingPinia()]
      }
    })
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders slot content when no error', () => {
    const wrapper = createWrapper()
    const slotContent = '<div class="test">Test Content</div>'
    wrapper.setProps({
      default: () => slotContent
    })
    
    expect(wrapper.html()).toContain(slotContent)
    expect(wrapper.find('.error-boundary').exists()).toBe(false)
  })

  it('renders error content when error occurs', async () => {
    const wrapper = createWrapper()
    const error = {
      title: 'Test Error',
      message: 'Something went wrong',
      details: 'Error details',
      severity: 'critical'
    }

    // Simulate error
    await wrapper.setData({ error })

    expect(wrapper.find('.error-boundary').exists()).toBe(true)
    expect(wrapper.text()).toContain('Test Error')
    expect(wrapper.text()).toContain('Something went wrong')
  })

  it('toggles error details visibility', async () => {
    const wrapper = createWrapper()
    const error = {
      title: 'Test Error',
      message: 'Something went wrong',
      details: 'Error details',
      severity: 'critical'
    }

    await wrapper.setData({ error })
    
    // Initially details should be hidden
    expect(wrapper.find('.details-content').exists()).toBe(false)

    // Click to show details
    await wrapper.find('.details-toggle').trigger('click')
    expect(wrapper.find('.details-content').exists()).toBe(true)
    expect(wrapper.find('.details-content').text()).toContain('Error details')

    // Click to hide details
    await wrapper.find('.details-toggle').trigger('click')
    expect(wrapper.find('.details-content').exists()).toBe(false)
  })

  it('emits retry event when retry button clicked', async () => {
    const wrapper = createWrapper()
    const error = {
      title: 'Test Error',
      message: 'Something went wrong',
      severity: 'critical'
    }

    await wrapper.setData({ error })
    await wrapper.find('.btn-primary').trigger('click')

    expect(wrapper.emitted('retry')).toBeTruthy()
    expect(wrapper.vm.error).toBeNull()
  })

  it('resets application state when reset button clicked', async () => {
    const wrapper = createWrapper()
    const store = useMainStore()
    const error = {
      title: 'Test Error',
      message: 'Something went wrong',
      severity: 'critical'
    }

    await wrapper.setData({ error })
    await wrapper.find('.btn-outline').trigger('click')

    expect(store.resetState).toHaveBeenCalled()
    expect(wrapper.emitted('reset')).toBeTruthy()
    expect(wrapper.vm.error).toBeNull()
  })

  it('captures and handles component errors', () => {
    const wrapper = createWrapper()
    const error = new Error('Component error')
    
    // Simulate component error
    wrapper.vm.onErrorCaptured(error, { $: { type: { name: 'TestComponent' } } }, 'test')

    expect(wrapper.vm.error).toBeTruthy()
    expect(wrapper.vm.error.title).toBe('Component Error')
    expect(wrapper.vm.error.message).toBe('Component error')
    expect(wrapper.emitted('error')).toBeTruthy()
  })

  it('respects shouldReset prop', async () => {
    const wrapper = createWrapper({ shouldReset: false })
    const store = useMainStore()
    const error = {
      title: 'Test Error',
      message: 'Something went wrong',
      severity: 'critical'
    }

    await wrapper.setData({ error })
    await wrapper.find('.btn-outline').trigger('click')

    expect(store.resetState).not.toHaveBeenCalled()
    expect(wrapper.emitted('reset')).toBeFalsy()
  })
})
