import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Claude Skills & Hooks',
  description: 'Claude Code plugin marketplace',

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Git Plugin', link: '/git/' },
      { text: 'Frappe Dev', link: '/frappe-dev/' },
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
          { text: 'version', link: '/git/version' },
          { text: 'auto-stage', link: '/git/auto-stage' },
          { text: 'pre-stop-commit', link: '/git/pre-stop-commit' },
        ]
      },
      {
        text: 'Frappe Dev Plugin',
        items: [
          { text: 'Overview', link: '/frappe-dev/' },
          { text: 'frappe-app', link: '/frappe-dev/frappe-app' },
          { text: 'frappe-doctype', link: '/frappe-dev/frappe-doctype' },
          { text: 'frappe-api', link: '/frappe-dev/frappe-api' },
          { text: 'frappe-service', link: '/frappe-dev/frappe-service' },
          { text: 'frappe-test', link: '/frappe-dev/frappe-test' },
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
