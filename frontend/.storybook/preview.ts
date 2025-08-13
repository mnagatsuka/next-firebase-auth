import '../src/app/globals.css'
import type { Preview } from '@storybook/nextjs-vite'
import { setupWorker } from 'msw/browser'

// Create a single MSW worker instance
const worker = setupWorker()

const preview: Preview = {
  parameters: {
    
    controls: { 
      expanded: true,
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    a11y: {
      test: 'todo'
    },
    docs: {
      autodocs: 'tag',
    },
  },
  loaders: [
    async () => {
      // Start MSW worker once
      if (!worker.listHandlers().length) {
        await worker.start({
          onUnhandledRequest: 'warn',
          quiet: false,
        })
      }
      return {}
    },
  ],
  beforeEach: async (context) => {
    // Reset handlers and apply story-specific handlers
    worker.resetHandlers()
    const { parameters } = context
    if (parameters.msw?.handlers) {
      worker.use(...parameters.msw.handlers)
    }
  },
};

export default preview;