import { Component, ErrorInfo, ReactNode } from "react";

export default class ErrorBoundary extends Component<{ children: ReactNode }, { error?: Error }> {
  state: { error?: Error } = {};

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Frontend render failure", error, info);
  }

  render() {
    if (this.state.error) {
      return <div className="grid min-h-screen place-items-center bg-slate-950 p-6 text-white"><div className="max-w-lg rounded-lg border border-red-900 bg-red-950/30 p-6"><h1 className="text-xl font-bold">Analytics interface failed to render</h1><p className="mt-2 text-sm text-red-200">{this.state.error.message}</p><button className="mt-5 rounded-md bg-white px-4 py-2 text-sm font-semibold text-slate-900" onClick={() => window.location.reload()}>Reload application</button></div></div>;
    }
    return this.props.children;
  }
}
