/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_WS_URL: string
  readonly VITE_APP_VERSION: string
  readonly VITE_GITHUB_URL: string
  readonly VITE_DOCS_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
