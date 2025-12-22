import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Claude Skills & Hooks',
  description: 'Claude Code plugin marketplace',

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Git Plugin', link: '/git/' },
      { text: 'Settings Sync', link: '/settings-sync/' },
    ],

    sidebar: [
      {
        text: 'Getting Started',
        items: [
          { text: 'Introduction', link: '/' },
          { text: 'Installation', link: '/installation' },
        ]
      },
      {
        text: 'Git Plugin',
        items: [
          { text: 'Overview', link: '/git/' },
          { text: 'commit', link: '/git/commit' },
          { text: 'auto-stage', link: '/git/auto-stage' },
          { text: 'pre-stop-commit', link: '/git/pre-stop-commit' },
        ]
      },
      {
        text: 'Settings Sync Plugin',
        items: [
          { text: 'Overview', link: '/settings-sync/' },
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/sergio-bershadsky/ai' }
    ]
  }
})
