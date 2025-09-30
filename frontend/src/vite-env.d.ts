/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_API_VERSION?: string
  readonly VITE_ENABLE_ANALYTICS?: string
  readonly VITE_ENABLE_WEARABLE_SYNC?: string
  readonly VITE_ENVIRONMENT?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
