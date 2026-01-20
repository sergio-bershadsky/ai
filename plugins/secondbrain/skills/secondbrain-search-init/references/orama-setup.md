# Orama Search Setup Reference

## Dependencies to Add

When enabling Orama for VitePress browser search, add these to `package.json`:

### Dependencies (runtime)

```json
{
  "dependencies": {
    "@orama/orama": "^3.0.0",
    "@orama/plugin-embeddings": "^3.0.0"
  }
}
```

### Dev Dependencies (build time)

```json
{
  "devDependencies": {
    "@tensorflow/tfjs-backend-webgl": "^4.22.0",
    "gray-matter": "^4.0.3",
    "tsx": "^4.19.0"
  }
}
```

### Scripts to Add

```json
{
  "scripts": {
    "docs:build": "npm run search:build && vitepress build docs",
    "search:build": "tsx docs/.vitepress/search/build-search-index.ts"
  }
}
```

## Files to Create

### 1. SearchBox.vue Component

Location: `docs/.vitepress/theme/components/SearchBox.vue`

Copy from: `${CLAUDE_PLUGIN_ROOT}/templates/scaffolding/vitepress/theme/components/SearchBox.vue.tmpl`

### 2. Build Script

Location: `docs/.vitepress/search/build-search-index.ts`

Copy from: `${CLAUDE_PLUGIN_ROOT}/templates/scaffolding/vitepress/search/build-search-index.ts.tmpl`

### 3. Theme Integration

Update `docs/.vitepress/theme/index.ts`:

```typescript
import SearchBox from './components/SearchBox.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('SearchBox', SearchBox)
  }
}
```

### 4. Layout Integration

In VitePress layout, replace default search with SearchBox:

```vue
<template>
  <div class="nav-search">
    <SearchBox />
  </div>
</template>
```

## Verification

After setup:

1. Run `npm install` to install dependencies
2. Run `npm run search:build` to generate index
3. Run `npm run docs:dev` and test search
4. Run `npm run docs:build` to verify production build
