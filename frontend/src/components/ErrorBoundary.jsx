/**
 * AirVision AI — Error boundary
 * Catches render-time errors anywhere in the tree and shows a friendly
 * recovery screen instead of a white page.
 */

import { Component } from 'react'
import ReportProblemIcon from '@mui/icons-material/ReportProblem'

export default class ErrorBoundary extends Component {
  state = { hasError: false, message: '' }

  static getDerivedStateFromError(error) {
    return { hasError: true, message: error?.message || 'Unknown error' }
  }

  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error('AirVision error boundary:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-slate-100 p-6 dark:bg-slate-950">
          <div className="card max-w-md p-8 text-center">
            <ReportProblemIcon className="mx-auto mb-4 text-5xl text-amber-500" />
            <h1 className="mb-2 text-xl font-bold text-slate-900 dark:text-white">
              Something went wrong
            </h1>
            <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">
              {this.state.message}
            </p>
            <button
              type="button"
              className="btn-primary mx-auto"
              onClick={() => this.setState({ hasError: false, message: '' })}
            >
              Try again
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
