module.exports = {
  title: 'My Site',
  tagline: 'The tagline of my site',
  url: 'https://github.com/Imperial-iGEM/DJANGO-Assembly-Methods',
  baseUrl: '/DJANGO-Assembly-Methods/',
  onBrokenLinks: 'throw',
  favicon: 'img/favicon.ico',
  organizationName: 'Imperial-iGEM', // Usually your GitHub org/user name.
  projectName: 'DJANGO-Assembly-Methods', // Usually your repo name.
  themeConfig: {
    navbar: {
      title: 'SOAP Lab',
      logo: {
        alt: 'SOAP Lab Logo',
        src: 'img/soaplab.png',
      },
      items: [
        {
          to: 'docs/',
          activeBasePath: 'docs',
          label: 'Docs',
          position: 'left',
        },
        {to: 'blog', label: 'Blog', position: 'left'},
        {
          href: 'https://github.com/Imperial-iGEM/DJANGO-Assembly-Methods',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'SOAP Lab Explained',
              to: 'docs/',
            },
            {
              label: 'Script generation',
              to: 'docs/moclo_script_generation',
            },
          ],
        },
        {
          title: 'SBOL Community',
          items: [
            {
              label: 'SBOL',
              href: 'https://sbolstandard.org/',
            },
            {
              label: 'SynBioHub',
              href: 'https://synbiohub.org/',
            },
            {
              label: 'SBOL Stack',
              href: 'http://ico2s.org/servers/sbol_stack.html',
            },
            {
              label: 'SBOL Canvas',
              href: 'https://sbolcanvas.org/',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Twitter',
              href: 'https://twitter.com/IGem2020',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/Imperial-iGEM/DJANGO-Assembly-Methods',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Imperial iGEM, Inc. Built with Docusaurus.`,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl:
            'https://github.com/facebook/docusaurus/edit/master/website/',
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo.
          editUrl:
            'https://github.com/facebook/docusaurus/edit/master/website/blog/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
