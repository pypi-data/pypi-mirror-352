# Changelog

<a name="6.2.0"></a>
## [6.2.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/6.1.1...6.2.0) (2025-05-31)

### ✨ Features

- **entrypoint, gitlab:** detect legacy missing 'squash_option' attribute ([260c433](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/260c4332a3ddf006ed8806e8b74f74d45edfc51c))

### 🐛 Bug Fixes

- **gitlab:** avoid exceptions upon group last owner member removal ([fed6ef0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/fed6ef00a2cf22a38cf58de70579c7b7fec739a0))
- **main:** exclusive '--run-housekeeping' and '--prune-unreachable-objects' ([4a0a170](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/4a0a1707816a4404fdf14e58e370f960f961a7e8))

### 📚 Documentation

- **license, mkdocs:** raise copyright year to '2025' ([671d6e8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/671d6e80a70cc519cdd302c704cbb01cb307f6b2))

### 🚀 CI

- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@4.1.0' ([63ebbc5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/63ebbc536f8252ecb5c0066a2deca5518c58487b))


<a name="6.1.1"></a>
## [6.1.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/6.1.0...6.1.1) (2025-02-28)

### ✨ Features

- **gitlab:** detect 'pages' jobs to preserve 'Pages' GitLab feature ([8ff360c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/8ff360cd81c0b05dcbc987108fe9d22a02c139b7))


<a name="6.1.0"></a>
## [6.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/6.0.1...6.1.0) (2025-02-10)

### ✨ Features

- **entrypoint, gitlab:** show already valid settings in green ([ed29b3a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/ed29b3a24a86e9fd37cc5857c7f3010b77bb34fa))
- **entrypoint, gitlab:** show GitLab username upon authentication ([6beea96](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6beea961771d3e3c58b0be3896d65d5353493adf))

### 🐛 Bug Fixes

- **entrypoint:** prevent acces to projects shared with groups ([c2308cd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/c2308cd8f5aceb3ba8c7f7733ab7f95f91676fcf))

### 📚 Documentation

- **docs:** use '<span class=page-break>' instead of '<div>' ([fe38e5e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/fe38e5ee4067f919191ce61b35c714a48ec927b3))
- **prepare:** avoid 'TOC' injection if 'hide:  - toc' is used ([b05111b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/b05111bc9f25a9dcf29db56fecfc8240a2cae575))

### 🎨 Styling

- **colors:** ignore 'Colored' import 'Incompatible import' warning ([56cb0df](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/56cb0df63be7cebd812204f30609bb6b04dec94b))

### ⚙️ Cleanups

- **sonar-project:** configure coverage checks in SonarCloud ([0a23f99](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/0a23f99271c9f3ef27b0d678ff2f7e635059a62d))

### 🚀 CI

- **gitlab-ci:** run coverage jobs if 'sonar-project.properties' changes ([b3efefc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/b3efefc5e958093797e54ed69aac9d27f33f834c))
- **gitlab-ci:** watch for 'docs/.*' changes in 'pages' jobs ([a4c1b0d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/a4c1b0dbc07298e65815c62a3593bcc5039c1e10))


<a name="6.0.1"></a>
## [6.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/6.0.0...6.0.1) (2025-01-01)

### 🐛 Bug Fixes

- **gitlab:** catch 'StopIteration' exceptions upon missing boards ([e200557](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/e200557e86edc81c556421adb613e7d4e81c56ed))


<a name="6.0.0"></a>
## [6.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/5.4.0...6.0.0) (2025-01-01)

### ✨ Features

- **cli:** implement '--{get,set}-project-issues-boards' features ([0a88810](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/0a88810784efeb97f4f3cd1bdd22741bfb482288))
- **cli, gitlab:** implement '--set-roles-create-{projects,subgroups}' ([56f7aba](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/56f7aba1a74ac1fde1c1d5c96ecc733683a94762))
- **entrypoint:** show projects description after '# ...' ([fbd6678](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/fbd6678ce14808d0b5a7b000e9f503ccf6829d44))
- **entrypoint:** allow empty description and custom indent in 'confirm' ([03fb17c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/03fb17c49957a5377edc572ef161a45e5df2cad1))
- **entrypoint:** use '...' quotes in 'confirm' function ([6e77117](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6e77117320ea2949c56308039fba0682f80d56b9))

### 🐛 Bug Fixes

- **cli:** use package name for 'Updates' checks ([06d795e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/06d795e0e870d2992cf20f4761c230267d4978bf))
- **entrypoint:** show '# /' if no description is set ([fbf2a28](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/fbf2a2807fdd49f957da676ba16030a733be8505))
- **gitlab:** support GitLab Premium delayed project/group deletions ([0ebc2c1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/0ebc2c1117a119366515399b95cc7c1bcde78d02))

### 📚 Documentation

- **mkdocs:** minor '(prefers-color-scheme...)' syntax improvements ([3964c8f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3964c8f53df20d048e848634da08c7498fd0c1d2))
- **mkdocs:** remove 'preview.py' and 'template.svg' files exclusions ([8caccf0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/8caccf0ca0ce828343c2c433df4eeeb2b3142553))
- **mkdocs, pages:** use 'MKDOCS_EXPORTER_PDF_OUTPUT' for PDF file ([e05833d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/e05833d94647f9827b66eebea1c3eceacdf7b124))
- **pages:** rename PDF link title to 'Export as PDF' ([f0b2b58](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f0b2b5804debdc4c0289dffb717d8ac8dd313c21))
- **pdf:** avoid header / footer lines on front / back pages ([84ed713](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/84ed713b6b690c4d2900634f4e97a376b04b65a4))
- **pdf:** minor stylesheets codestyle improvements ([7373bd6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/7373bd62de55a70375bcf9f4a6d812c82bbc7280))
- **pdf:** reverse PDF front / back cover pages colors for printers ([7505256](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/7505256812186297b3f85f98a496f10730771b88))
- **prepare:** use 'mkdocs.yml' to get project name value ([837d15b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/837d15b1f345249da3620ed7debc1ce916e634b7))
- **readme:** add missing '--' separator after '--reset-features' ([bd038df](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/bd038df4d21894a844489f5462ebd5e282566d96))
- **stylesheets:** resolve lines and arrows visibility in dark mode ([89b16f6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/89b16f6dec671af4be1f15f749f45b283088f53c))
- **templates:** add 'Author' and 'Description' to PDF front page ([eff3014](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/eff3014e2fd7f229fcd548ddaebd180951a101ed))
- **templates:** add 'Date' detail on PDF front page ([f1042d9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f1042d9463ee3cc1389608ce7a2016d1e5c1eb89))
- **templates:** use Git commit SHA1 as version if no Git tag found ([37e1080](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/37e108093449c531bb579b4c057708079c4cff19))

### 🧪 Test

- **test:** fix daily updates coverage test syntax ([0eac0ac](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/0eac0acdab4b14add861e507c214cf9178a2bca4))

### 🚀 CI

- **gitlab-ci:** avoid PDF slow generation locally outside 'pdf' job ([77fc8e8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/77fc8e88c8090133f10c27974037e99b075ee74e))
- **gitlab-ci:** validate host network interfaces support ([d706e44](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/d706e44166c72cbae17fb8ca989bd5a0bc93e9f5))
- **gitlab-ci:** enable '.local: no_regex' feature ([9235ece](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/9235ece9a5d326e4faa45715f79cea75a478cbd6))
- **gitlab-ci:** append Git version to PDF output file name ([6e8cd69](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6e8cd693ec6fefe56da07e3793f839d3e1bccb00))
- **gitlab-ci:** rename PDF to 'gitlab-projects-settings' ([63344bd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/63344bd3bf582ed9a893602e68e7f581dde46f4e))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@4.0.0' ([708acf7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/708acf7a548f54790f7e4e1e83016019811b74d9))
- **gitlab-ci:** ensure 'pages' job does not block pipeline if manual ([077e41f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/077e41f1c25e8c609df86104e2b1a1339e9f9b4e))
- **gitlab-ci:** change release title to include tag version ([51b8089](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/51b80895a57f7bc7c1429dfd27ac44c0a210633f))


<a name="5.4.0"></a>
## [5.4.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/5.3.1...5.4.0) (2024-10-28)

### ✨ Features

- **cli:** implement '--[add,remove]-jobs-token-allowlist' for CI job tokens ([96aea14](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/96aea1424f4a57a334430cd9970b5ba91665c703))
- **main:** support '--update-description[s]' parameter ([0adb104](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/0adb1045e5445501743348c732cc5329cf320554))
- **main:** support '--*-project[s]' and '--*-group[s]' parameters ([55210bf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/55210bf96f7a54314b54d8734f4de1acaa660b9a))

### 🐛 Bug Fixes

- **main:** ensure 'FORCE_COLOR=0' if using '--no-color' flag ([b38f7e1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/b38f7e1d08b6f7b96d03b779d51de61ef689738e))

### 📚 Documentation

- **assets:** prepare mkdocs to generate mermaid diagrams ([1787a67](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/1787a676a0e28b9a9ef52caab256342a5371b7e4))
- **cliff:** improve 'Unreleased' and refactor to 'Development' ([2829e95](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2829e95156e7010af53d252eb484cdaf30ed1a5b))
- **covers:** resolve broken page header / footer titles ([4419933](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/44199332dadb2b7a1dfa991db26dc3dcbf513593))
- **custom:** change to custom header darker blue header bar ([6fcc006](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6fcc0068f525473ef89a15e6b6cdb42f5ff26116))
- **docs:** improve documentation PDF outputs with page breaks ([bb43490](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/bb4349026d81678daea498ea60929566c8b59351))
- **mkdocs:** enable 'git-revision-date-localized' plugin ([525b346](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/525b346c13992bec6c074f1e3a5facb56a475950))
- **mkdocs:** change web pages themes colors to 'blue' ([7335cda](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/7335cdad11c0601ce917ea26a713ae84873ce342))
- **mkdocs:** fix 'git-revision-date-localized' syntax ([106dce0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/106dce06a37414b81f58c32fdd3f8884f15eb9ac))
- **mkdocs:** migrate to 'awesome-pages' pages navigation ([6d94b4f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6d94b4f67d6d43a83e8f1032139366606a2294a8))
- **mkdocs:** change 'auto / light / dark' themes toggle icons ([4729e7e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/4729e7ea4073310b6f6b9dc944755d6608502e87))
- **mkdocs:** enable and configure 'minify' plugin ([ae98410](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/ae98410e7a2046c2f2c9d2e0b7330600a00b3c6e))
- **mkdocs:** install 'mkdocs-macros-plugin' for Jinja2 templates ([b81f17b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/b81f17bd4ed601c541f31e4019536075233d8c51))
- **mkdocs:** enable 'pymdownx.emoji' extension for Markdown ([c14a469](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/c14a469c9b5c8b3bf6f8a481633736d7c051f17c))
- **mkdocs:** implement 'mkdocs-exporter' and customize PDF style ([6afafa1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6afafa1f5a4ffe70d1c5d2df988e0b6ad9849b2b))
- **mkdocs:** set documentation pages logo to 'solid/code' ('</>') ([5d7144b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/5d7144b44aa989fdb3cbebd9b0e717a9c7d37ee9))
- **mkdocs:** enable 'permalink' headers anchors for table of contents ([40904cc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/40904cccd27caba80cdfa4ce0be1992102667241))
- **mkdocs:** prepare 'privacy' and 'offline' plugins for future usage ([39ab0e8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/39ab0e82f3e21bd67f0209b4ae52ff15bc4ad64b))
- **mkdocs:** disable Google fonts to comply with GDPR data privacy ([192266f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/192266feb2056bf0c8d1a383f301baf5c938a262))
- **mkdocs:** implement 'Table of contents' injection for PDF results ([40a2ca7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/40a2ca721b3cc83e975ea875f0ea57aeafe200e0))
- **mkdocs:** enable 'Created' date feature for pages footer ([22c27a8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/22c27a86a4428d444637b54a920751ea69ebc7dd))
- **mkdocs:** add website favicon image and configuration ([58d0e7c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/58d0e7c33fb335b8455501e9e242b21f90a4f7fb))
- **mkdocs:** implement 'book' covers to have 'limits' + 'fronts' ([f8881d9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f8881d92cb21707b077e58c4d8dfc36b8321d5bd))
- **mkdocs:** isolate assets to 'docs/assets/' subfolder ([486ae75](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/486ae757e3240a9ceeff34cfefb82beb4987fbb4))
- **mkdocs:** exclude '.git' from watched documentation sources ([a6ac5c2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/a6ac5c202c869b1b32f348b54e3e59f2604c7236))
- **mkdocs, prepare:** resolve Markdown support in hidden '<details>' ([648d940](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/648d94062647d0a845114b8712a5c7faadf59b53))
- **pages:** rename index page title to '‣ Usage' ([5e42421](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/5e4242122fb28188ecc141d20ad336a8f94ff09e))
- **pdf:** simplify PDF pages copyright footer ([7feda91](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/7feda913cc2a892edb69d9abcc5f311c4c13787d))
- **pdf:** migrate to custom state pseudo class 'state(...)' ([74187aa](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/74187aacaeae9a2ad38fbccfe4e5ca00b9391839))
- **prepare:** regenerate development 'CHANGELOG' with 'git-cliff' ([b990232](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/b9902323afa19ba8dff61974c8d00be5b2a6a82d))
- **prepare:** avoid 'md_in_html' changes to 'changelog' and 'license' ([3d02e03](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3d02e035745561eaf7ede7a1b2b7b4f76fb6013d))
- **prepare:** fix '<' and '>' changelog handlings and files list ([3de52a2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3de52a27562e5fe4faaf5a60647e28f6ecea33f5))
- **prepare:** implement 'About / Quality' badges page ([3ae64e7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3ae64e7997792409cf735409881409e8537aa6ec))
- **prepare:** improve 'Quality' project badges to GitLab ([10d7bbf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/10d7bbf2a4720f05906bd05aded9892737c83dfb))
- **prepare:** use 'docs' sources rather than '.cache' duplicates ([4b9bf71](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/4b9bf71546ec83e1b5d768a4a54d5dad14ca3aef))
- **prepare:** resolve 'docs/about' intermediates cleanup ([5f7b6ce](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/5f7b6ce1b84cadcdcee4b75bc025ae927e5f37e5))
- **prepare:** add PyPI badges and license badge to 'quality' page ([3fdea38](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3fdea386b279a985a16ab5eb7be81830d1b43a29))
- **prepare:** avoid adding TOC to generated and 'no-toc' files ([dc572e2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/dc572e2796b6473f9376727510f7e4044fece683))
- **readme:** add 'gcil:enabled' documentation badge ([5fd8354](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/5fd835465636cb190024c5cf15b0dcbeb60dfc2a))
- **readme:** add pypi, python versions, downloads and license badges ([4e0e234](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/4e0e23448029fb19ec496c238221fb24d61423b2))
- **readme:** add '~/.python-gitlab.cfg' section title ([f640412](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f64041262f5de3d609521d6a53cb54ee9425f0cf))
- **robots:** configure 'robots.txt' for pages robots exploration ([c9a7bd8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/c9a7bd84bc3cea9362753ca4170113bff3276df9))

### ⚙️ Cleanups

- **gitignore:** exclude only 'build' folder from sources root ([203338f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/203338fe122e32bfff902f9a3d9fa6eef8f1a0f8))
- **gitignore:** exclude '/build' folder or symlink too ([2a9473c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2a9473cbeba7701ee62cbc4add6a98e02bbf457b))
- **gitlab:** resolve 'too-many-positional-arguments' new lint warnings ([4d5e9d2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/4d5e9d2e893b5fb888b39d2730c41f8081807df8))
- **sonar:** wait for SonarCloud Quality Gate status ([767d52b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/767d52b258477af71658e57d30c064d49d0a6ada))
- **vscode:** use 'yzhang.markdown-all-in-one' for Markdown formatter ([facc6b8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/facc6b8349b5f45f57f18b4a4402bd75d7fa2b50))

### 🚀 CI

- **gitlab-ci:** prevent 'sonarcloud' job launch upon 'gcil' local use ([f606bbb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f606bbb75c4a0bd0cff904e12eec4c113e67a2d1))
- **gitlab-ci:** run SonarCloud analysis on merge request pipelines ([73f8c59](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/73f8c598535ff61c3159847acb509bb9caafc1f8))
- **gitlab-ci:** watch for 'config/*' changes in 'serve' job ([e5c8491](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/e5c849125cc6bba95724a7bfa7ee6c9da8ce5310))
- **gitlab-ci:** fetch Git tags history in 'pages' job execution ([9f2235c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/9f2235ce520bf90f50171b6d431bbffdf6eeb20f))
- **gitlab-ci:** fetch with '--unshallow' for full history in 'pages' ([4cc19f3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/4cc19f3e1d97fdd1bf4914993d314151901be37f))
- **gitlab-ci:** enforce 'requirements/pages.txt' in 'serve' job ([e61d8da](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/e61d8da9375e9ff3b0b9fedfc7776f3149f21ead))
- **gitlab-ci:** add 'python:3.12-slim' image mirror ([428ae8b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/428ae8b4441db20a054280780b1d0952a6091b20))
- **gitlab-ci:** inject only 'mkdocs-*' packages in 'serve' job ([f7abea0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f7abea0008278a437de5c8de1ee4f09fd97476af))
- **gitlab-ci:** install 'playwright' with chromium in 'serve' job ([a3b788f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/a3b788f3250ce50247ce2333fa559d240eed9be6))
- **gitlab-ci:** find files only for 'entr' in 'serve' ([35ebc15](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/35ebc156e2ee4923c34292f5840332ccdfb84174))
- **gitlab-ci:** improve GitLab CI job outputs for readability ([21673ff](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/21673ffd455865483ee0f73d9c3ca0ee488c89f8))
- **gitlab-ci:** deploy GitLab Pages on 'CI_DEFAULT_BRANCH' branch ([9d55a72](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/9d55a7240dd6e3ae51905af1321b55536dca4a0f))
- **gitlab-ci:** ignore 'variables.scss' in 'serve' watcher ([60d37d3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/60d37d3eb25fc4e1bb94787bd80c1779d1aacc3e))
- **gitlab-ci:** preserve only existing Docker images after 'images' ([eea9afc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/eea9afcb46c9135a2d0a058b9251393cb1e4b488))
- **gitlab-ci:** use 'MKDOCS_EXPORTER_PDF_ENABLED' to disable PDF exports ([aba6c50](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/aba6c508692f592b007e0d160183ad168762fad8))
- **gitlab-ci:** run 'pages' job on GitLab CI tags pipelines ([4cd9ea0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/4cd9ea00633181d51e9c24cdac718d4f8022e58c))
- **gitlab-ci:** isolate 'pages: rules: changes' for reuse ([2919d37](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2919d376190b8a9e05e1ee11516de83393a10d1a))
- **gitlab-ci:** allow manual launch of 'pages' on protected branches ([7fdd535](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/7fdd5351933a7cd54f9c3dce3fb7fbf2b19ea3f8))
- **gitlab-ci:** create 'pdf' job to export PDF on tags and branches ([2ee62f7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2ee62f7714a6db87660ce72afb8be1c0b6e3757b))
- **gitlab-ci:** implement local pages serve in 'pages' job ([39741d7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/39741d7f79c83c99177eb1432dd3daa284ffd758))
- **gitlab-ci:** raise minimal 'gcil' version to '11.0' ([0881a14](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/0881a1446110b86882d02ade6bd254f1b42f5b50))
- **gitlab-ci:** enable local host network on 'pages' job ([b23017f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/b23017f1831e8a704a529c9ce0cb5d2da8afd2d1))
- **gitlab-ci:** detect failures from 'mkdocs serve' executions ([64dba9f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/64dba9fcce793faa9c7ef5aacb10e30f1fb0fd5e))
- **gitlab-ci:** refactor images containers into 'registry:*' jobs ([2cbce86](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2cbce86512edfb6f5a2391b78eec6bb4727b2ba6))
- **gitlab-ci:** bind 'registry:*' dependencies to 'requirements/*.txt' ([18a5b25](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/18a5b25dec1dce2ade3597e59b593561783806ba))

### 📦 Build

- **build:** import missing 'build' container sources ([a075797](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/a0757973cfab6da31f13735b9e826e9147fa2925))
- **containers:** use 'apk add --no-cache' for lighter images ([b7bb58c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/b7bb58c88e1c37b5edeaa18bda64b8d17f54bc04))
- **pages:** add 'git-cliff' to the ':pages' image ([696a812](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/696a8122609445c58caba987282c3ad4c8fe8305))
- **pages:** migrate to 'python:3.12-slim' Ubuntu base image ([4c1bb56](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/4c1bb568bc12b4c73421498aed90b8278516ef05))
- **pages:** install 'playwright' dependencies for 'mkdocs-exporter' ([688388e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/688388eeb0e698ccbadb299ded03e3c50174d841))
- **pages:** install 'entr' in the image ([6a3d40a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6a3d40a7f15bf82c3c30538eab9ba4595f0df69c))
- **requirements:** install 'mkdocs-git-revision-date-localized-plugin' ([73f1d7f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/73f1d7f543293a22e8ea78330ebde297684d4d3e))
- **requirements:** install 'mkdocs-awesome-pages-plugin' plugin ([d5715db](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/d5715db9f9a767799a055601e7f8f8b61c873e98))
- **requirements:** install 'mkdocs-minify-plugin' for ':pages' ([bd8316a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/bd8316ae42c5731ef250d939b616fe1ad62db7ac))
- **requirements:** install 'mkdocs-exporter' in ':pages' ([abb114b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/abb114b054319c358d55126037f69f131dc58202))
- **requirements:** migrate to 'mkdocs-exporter' with PR#35 ([ab1c1d7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/ab1c1d796154547bd8ac223e9ffd9aa314aecfe6))
- **requirements:** upgrade to 'playwright' 1.48.0 ([8e9f081](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/8e9f0819ecf48f10ea513ec483d0a5ac9533f2f8))
- **requirements:** migrate to 'mkdocs-exporter' with PR#42/PR#41 ([156dd4d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/156dd4dd8def9a0065e38d7a657e822b11bba3fa))


<a name="5.3.1"></a>
## [5.3.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/5.3.0...5.3.1) (2024-08-25)

### ✨ Features

- **updates:** migrate from deprecated 'pkg_resources' to 'packaging' ([103ef37](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/103ef37f4bc54fe32705e3fab92b01ca617a0126))

### 📚 Documentation

- **mkdocs:** implement GitLab Pages initial documentation and jobs ([8643bbc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/8643bbccc427afeac233050d3718d5e229658558))
- **readme:** link against 'gcil' documentation pages ([022f572](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/022f572b65930b824f63365220cb0921dabb505f))

### ⚙️ Cleanups

- **commitizen:** migrate to new 'filter' syntax (commitizen#1207) ([fddd134](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/fddd1344e9c8097279661f0d2d66c6c167efbad8))
- **pre-commit:** add 'python-check-blanket-type-ignore' and 'python-no-eval' ([5dc3e17](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/5dc3e17f6eaee57a80699b747c22a19659a0a427))
- **pre-commit:** fail 'gcil' jobs if 'PRE_COMMIT' is defined ([5b508ba](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/5b508baf43e57ca8e77dc0e951b521c8e19549f2))
- **pre-commit:** simplify and unify 'local-gcil' hooks syntax ([f1b7c10](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f1b7c10d642a08f6af9fcacbe67ae50956a806b4))
- **pre-commit:** improve syntax for 'args' arguments ([29ed782](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/29ed7822a526b3163d2888401b511e0c94bb50db))
- **pre-commit:** migrate to 'run-gcil-*' template 'gcil' hooks ([1242370](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/1242370ce0a7f0f6132805a6f8472a181687c297))
- **pre-commit:** update against 'run-gcil-push' hook template ([28e3bc8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/28e3bc8a7f28db2e55d2123beaaf1ea29f25812b))
- **pre-commit:** migrate to 'pre-commit-crocodile' 3.0.0 ([0167d46](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/0167d46b49395ce8e0a4444e91e37fe57f6005ab))

### 🚀 CI

- **containers:** implement ':pages' image with 'mkdocs-material' ([ab8bdde](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/ab8bdde24678fb91d2ca053a82da43de3efc1ced))
- **gitlab-ci:** avoid failures of 'codestyle' upon local launches ([62f9d86](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/62f9d865170ab3ac90f41194bd02757be96a568b))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@2.1.0' component ([46515c9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/46515c90ec5a762256bbd168e9ed82a2a903c5cc))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@3.0.0' component ([412f468](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/412f468335739af7f9b6b3fe64f45969ac416562))


<a name="5.3.0"></a>
## [5.3.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/5.2.1...5.3.0) (2024-08-21)

### 🐛 Bug Fixes

- **gitlab:** fix support for Python 3.8 types union ([b83320e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/b83320ef7a07a92010cb5e72c0afc6ecc4468e9c))
- **platform:** always flush on Windows hosts without stdout TTY ([78bcaaa](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/78bcaaaf75d059a2450a0a72f08da83f404915a9))

### 📚 Documentation

- **readme:** add 'pre-commit enabled' badges ([c4ea26a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/c4ea26ac68b4922aade5de4c77aa58b0f719de22))
- **readme:** add SonarCloud analysis project badges ([8cf30fb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/8cf30fbc1610a620494a52a7830687c9e0c32ae8))
- **readme:** link 'gcil' back to 'gitlabci-local' PyPI package ([135a40c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/135a40c0608d35ef3f1527b61db062eafaddff2f))

### ⚙️ Cleanups

- **commitizen:** migrate to 'pre-commit-crocodile' 2.0.1 ([c35c1e7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/c35c1e761dc8415335a10afe3e7991acf306cbbb))
- **gitattributes:** always checkout Shell scripts with '\n' EOL ([f1917c2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f1917c230a50e3fa9cdaf5e3bca9b1de4c70818b))
- **gitignore:** ignore '.*.swp' intermediates 'nano' files ([4e2a305](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/4e2a30548896be6c2dc2e75d15e8bc1b6a074f0d))
- **pre-commit:** run 'codestyle', 'lint' and 'typings' jobs ([276de41](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/276de41ada79ce642a967cb54c728daf57ba71e1))
- **pre-commit:** migrate to 'pre-commit-crocodile' 2.0.0 ([9807569](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/9807569bd73b29e96d12c0d2914b43205b1fd4c2))

### 🚀 CI

- **gitlab-ci:** show fetched merge request branches in 'commits' ([23cc27f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/23cc27fdf6c545745950952cf80d9050924ce166))
- **gitlab-ci:** fix 'image' of 'commits' job ([f3165b2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f3165b2d0e3213655e423f1f71b9b3e0df24c8ee))
- **gitlab-ci:** always run 'commits' job on merge request pipelines ([0aaac37](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/0aaac37a68257135d987bea048e9aa8436129a23))
- **gitlab-ci:** make 'needs' jobs for 'build' optional ([1c61dc0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/1c61dc05c8206de8e5f93d06480d8f800620e6cb))
- **gitlab-ci:** validate 'pre-commit' checks in 'commits' job ([561ad01](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/561ad01ffbe8dd3e57f6249770f9e6577e44ed2f))
- **gitlab-ci:** refactor images into 'containers/*/Dockerfile' ([2f90140](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2f901407fbe75b169136f66448e784a3fc2140a8))
- **gitlab-ci:** use 'HEAD~1' instead of 'HEAD^' for Windows compatibility ([3b4ec64](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3b4ec64d07d8188fd74822130bbb916c16d7d138))
- **gitlab-ci:** check only Python files in 'typings' job ([a7661f0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/a7661f01df6f3105f16fb4116601a41c9170c316))
- **gitlab-ci:** implement SonarCloud quality analysis ([6b1518b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6b1518bbf28d12c2d2123a9461d7fa75caf6e3c1))
- **gitlab-ci:** detect and refuse '^wip|^WIP' commits ([34a1aa8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/34a1aa8e0dfa696feda920a9cf0664bee3bb4797))
- **gitlab-ci:** isolate 'commits' job to 'templates/commit.yml' ([265a9b4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/265a9b4d0f1a19ccb5e0adb4c40982c9622b1d45))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@2.0.0' component ([78576fe](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/78576fe083da06a3f967847dc2842e0a8a7dfa39))
- **gitlab-ci:** create 'hooks' local job for maintenance ([f9b9d40](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f9b9d403464be7fbe84605fe29e462b1c5d8b3ce))
- **gitlab-ci, tests:** implement coverage initial jobs and tests ([acd1dc2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/acd1dc2cfc72517369972cb4956ec486720f6344))

### 📦 Build

- **pre-commit:** migrate to 'pre-commit-crocodile' 1.1.0 ([d52d778](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/d52d7781a9c9bfb6495a793f40e1d5ef9db51d98))


<a name="5.2.1"></a>
## [5.2.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/5.2.0...5.2.1) (2024-08-16)

### 🐛 Bug Fixes

- **gitlab:** fix '--protect-tags' unknown protection level error ([f745f7e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f745f7e82acf831145d205c48b1dc6a42bcebefe))
- **package:** fix package name for 'importlib' version detection ([b5bf779](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/b5bf7799f19425fcad86381e63240cd0292044c3))

### ⚙️ Cleanups

- **hooks:** implement evaluators and matchers priority parser ([c59fa17](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/c59fa17b44d3bb1f3f2d08fd31c4adfea834ab6b))


<a name="5.2.0"></a>
## [5.2.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/5.1.0...5.2.0) (2024-08-15)

### 🐛 Bug Fixes

- **entrypoint:** prevent project labels changes if project is archived ([8289e24](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/8289e24e67a7637a4cb249241b3c4fe981fc361d))
- **setup:** refactor 'python_requires' versions syntax ([549a0e5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/549a0e5c73f7d1b423196e220b01b20cd59f4588))
- **🚨 BREAKING CHANGE 🚨 |** **setup:** drop support for Python 3.7 due to 'questionary>=2.0.0' ([2b849ca](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2b849ca192a86ea04acd962562928571635dc7a3))
- **setup:** resolve project package and name usage ([07f56ca](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/07f56ca9a2486fd6e14fd8d62474d7557edee48d))
- **updates:** ensure 'DEBUG_UPDATES_DISABLE' has non-empty value ([055804a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/055804a93f8f1b29c3209a052795b3de7e79c52f))
- **updates:** fix offline mode and SemVer versions comparisons ([8f34bba](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/8f34bba541e518f78ac0df5d1da8d03e81e682c8))

### 📚 Documentation

- **cliff:** use '|' to separate breaking changes in 'CHANGELOG' ([83697bf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/83697bf5b5f4fd8d863ac6e9be14cb57d0de7f7a))
- **license:** update copyright details for 2024 ([040d401](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/040d4018af216d1970d5a1594761baa2442a920d))
- **readme:** add 'Commitizen friendly' badge ([c178093](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/c1780930da8a61f2fad4967f23b2b52b1da65854))

### 🎨 Styling

- **cli:** improve Python arguments codestyle syntax ([3f168ab](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3f168abf9145485d4ebc8507d08d140490aab225))
- **commitizen, pre-commit:** implement 'commitizen' custom configurations ([651c1d9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/651c1d98ac18d0317d1760b05033d5c8de5cdca3))
- **pre-commit:** implement 'pre-commit' configurations ([cc00f76](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/cc00f763a8b1e3693585f1dffdb2c8987ccb1020))

### ⚙️ Cleanups

- **cli, package:** minor Python codestyle improvements ([cfb3636](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/cfb3636980db217f20f87a1b9386b51659a8506f))
- **pre-commit:** disable 'check-xml' unused hook ([69c3c15](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/69c3c1501e05f4bde23f3e2b0cce62080d543a4f))
- **pre-commit:** fix 'commitizen-branch' for same commits ranges ([c521c8a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/c521c8a6620f854e4bcdbf0c7a7ea637c3230d35))
- **setup:** refactor with more project configurations ([7248730](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/72487303eed0988325f697c9cfeb4d7c4c8fa5f0))
- **updates:** ignore coverage of online updates message ([9da21ab](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/9da21abfc2f9cffe9cdb176cb52f47b8000c178b))
- **vscode:** remove illegal comments in 'extensions.json' ([6b6edf7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6b6edf7666a3eb7242aa99d961449c5a9265a83c))

### 🚀 CI

- **gitlab-ci:** watch for 'codestyle', 'lint' and 'typings' jobs success ([26e5585](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/26e5585c8454f931dd3afee9c49070ca3b788c88))
- **gitlab-ci:** create 'commits' job to validate with 'commitizen' ([35db900](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/35db90049f9a0f8fbe360826c295ac63e8507d66))
- **gitlab-ci:** fix 'commits' job for non-default branches pipelines ([6928467](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6928467ae62452e4a2212d017070260a7031dfaa))

### 📦 Build

- **hooks:** create './.hooks/manage' hooks manager for developers ([633661b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/633661be2cd61a9ed2013b1b04790f7757897819))
- **hooks:** implement 'prepare-commit-msg' template generator ([67c8541](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/67c85410e938cfe5ae623112c013f0b2bae50655))
- **pre-commit:** enable 'check-hooks-apply' and 'check-useless-excludes' ([69a8746](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/69a8746356b09e7d69e453c17ed99adf303c3322))


<a name="5.1.0"></a>
## [5.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/5.0.2...5.1.0) (2024-08-11)

### ✨ Features

- **cli:** implement '--no-color' to disable colors ([a3b2534](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/a3b253438c714952a57168363c25c523701436f4))

### 🐛 Bug Fixes

- **package:** check empty 'environ' values before usage ([78c029c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/78c029cf236c1573be8e6f560680cb30595e1287))
- **updates:** remove unused 'recommended' feature ([9de050d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/9de050d75da8545e64c2729e3757c47806cbfcfc))

### 📚 Documentation

- **readme:** migrate from 'gitlabci-local' to 'gcil' package ([80b42e9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/80b42e9129c5b3f1a481522785f79d2db26200cf))

### ⚙️ Cleanups

- **cli:** resolve unused variable value initialization ([6381f03](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6381f03997ed46447dfbf995c3ff79106047d394))
- **colors:** resolve 'pragma: no cover' detection ([17e38e5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/17e38e51519f2176507c45c5a3ef7c899bb2747a))
- **platform:** disable coverage of 'SUDO' without write access ([7f5a35f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/7f5a35ffe37ed4e9ebb69ad379c9384cb16f8c63))
- **setup:** remove faulty '# pragma: exclude file' flag ([1635dbc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/1635dbcfdae3eed7a27ad55a5b75749c6b9d3b81))


<a name="5.0.2"></a>
## [5.0.2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/5.0.1...5.0.2) (2024-08-10)

### ✨ Features

- **setup:** add support for Python 3.12 ([1fd8ed2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/1fd8ed29bfe29d99e9b2d2dfa8f0bd0fc36c94e5))

### 🧪 Test

- **setup:** disable sources coverage of the build script ([ea25fba](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/ea25fbaa9e300df74b0a87f0564776402a34497c))

### 🚀 CI

- **gitlab-ci:** raise latest Python test images from 3.11 to 3.12 ([83c6dd9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/83c6dd938af7801db91230ca7df4506c00d0435f))
- **gitlab-ci:** deprecate outdated and unsafe 'unify' tool ([365a9e9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/365a9e95f49ea06d3dde03c44d55292aede2cac6))


<a name="5.0.1"></a>
## [5.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/5.0.0...5.0.1) (2024-08-10)

### ✨ Features

- **gitlab-projects-settings:** migrate under 'RadianDevCore/tools' group ([6c618dd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6c618dd75133aed882b55475d7ac1b7def888fa8))

### 🐛 Bug Fixes

- **settings:** ensure 'Settings' class initializes settings file ([2ec90d6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2ec90d6b70f42c30ff30defa3c1ed9241173ab04))
- **src:** use relative module paths in '__init__' and '__main__' ([220c444](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/220c444acdc90a3f5ea25ae894d6ba9064f37ee1))


<a name="5.0.0"></a>
## [5.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/4.2.1...5.0.0) (2024-08-08)

### 🛡️ Security

- **🚨 BREAKING CHANGE 🚨 |** **cli:** acquire tokens only from environment variables ([3f211bd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3f211bd41e92f022c3648b670643c7f13ff5cd2d))

### ✨ Features

- **🚨 BREAKING CHANGE 🚨 |** **cli:** refactor CLI into simpler GitLab URL bound parameters ([1aa72a4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/1aa72a4d5157ccb0be248fa7720cedf5d371e99e))
- **cli:** implement '--confirm' to bypass interactive user confirmations ([1bf9b99](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/1bf9b99be28d99b232b098cc3040e7f5b8f8d4f0))
- **cli:** add tool identifier header with name and version ([4362101](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/436210131eba06452f6b79e4ed46815c9f08fbd7))
- **cli:** implement '.python-gitlab.cfg' GitLab configurations files ([271c7c8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/271c7c8f9a645e5cacfc1fc9990dab2bfbad0663))
- **cli, argparse:** implement environment variables helpers ([7f4caec](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/7f4caecf2c867944fa3aaa39d6f4c0eac4b0aebc))
- **cli, gitlab:** implement '--prune-unreachable-objects' feature ([d07b179](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/d07b1799110a1d64a48f07042275f84e0a3e8841))
- **cli, gitlab:** implement '--erase-jobs-artifacts' to erase jobs artifacts ([75109f3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/75109f3820f42d8807f6430d2a3871494855bcda))
- **cli, gitlab:** implement '--erase-jobs-contents' to erase jobs contents ([24b82bc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/24b82bcdebbecb0e1ecf1f9cb8999950b6b22793))
- **cli, gitlab:** implement CI job token and public authentications ([291777c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/291777c1d752cb3ca15761abb1dccc63114a2f4c))
- **cli, gitlab:** implement '--{get,set}-project-labels' with JSON ([f1bf888](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f1bf888e8e1ac54f18d1ad8c864eb176a61b1657))
- **cli, gitlab:** implement '--{get,set}-group-labels' with JSON ([24305b5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/24305b5a00b1dbb7d395d3add72132424bc36015))
- **cli, gtlab:** implement '--set-merge-method' for merge requests ([969e9ec](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/969e9ec0445dffcca7e9b4ce77f710cf231befb4))
- **cli, gtlab:** implement '--set-merge-squash' for merge requests ([6d50073](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6d500735e97d32204ed4ef64d9c8e6915aab70ea))
- **cli, gtlab:** implement '--set-merge-pipelines' for merge requests ([13f150d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/13f150d5335557d89c1f6d31ab6439d44569603b))
- **cli, gtlab:** implement '--set-merge-skipped' for merge requests ([d65d112](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/d65d1120fa035db1bb8194fa441cb53a14d20e3b))
- **cli, gtlab:** implement '--set-merge-resolved' for merge requests ([9d3c51c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/9d3c51ca49a561f070c8009ec0dbd4d90a3725d8))
- **entrypoint:** wrap '--available-features' outputs with ' ([09cd008](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/09cd008cbd43d2e5ddb2a785cd94a60b4bbcc4f3))

### 🐛 Bug Fixes

- **environments:** add missing ':' to the README help description ([48b947b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/48b947bb3cbafd59f584bc90a24d3533e3a510a4))
- **gitlab:** wait 3 seconds after group and project deletions ([9a273bb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/9a273bb38babc82d72f768dbad320c550fc3670d))

### 📚 Documentation

- **cliff:** document 'security(...)' first in changelog ([eced346](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/eced346b5227cacb57da930865b65d8cef55e83e))
- **readme:** document '~/.python-gitlab.cfg' configuration file ([c62ae1e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/c62ae1e6b4ba45f894a212d2ad4ed3d68476cfae))

### ⚙️ Cleanups

- **cli/main:** minor codestyle improvement of 'import argparse' ([1b84f36](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/1b84f368684ef0a8e34f20267fa6e90400df1a06))
- **entrypoint:** refactor 'confirm' against 'gitlab-projects-migrate' ([35f5139](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/35f513955a44377c73c4d8cee2f9a04330b7d63f))
- **entrypoint, gitlab:** bind 'ProjectFeatures' names directly ([39d0d07](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/39d0d07748e00c0074f011b14304e26ccb7f0fe7))
- **gitlab:** acquire project and group despite '--dry-run' use ([462041d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/462041db1b2817daa0a93712a040a5c2abdb1d50))
- **types:** cleanup inconsistent '()' over base classes ([ef60d62](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/ef60d6200a3a45ea6dd88253f8892721314ff4ee))

### 🚀 CI

- **gitlab-ci:** migrate from 'git-chglog' to 'git-cliff' ([99fad86](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/99fad86afc05c7360d186e5bd28b355161136ad3))


<a name="4.2.1"></a>
## [4.2.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/4.2.0...4.2.1) (2024-06-10)

### 🐛 Bug Fixes

- **gitlab:** restore support for old GitLab 13.12 instances ([de82a80](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/de82a807754d512a756c35b4b2ecbbe0c6e54424))

### 📚 Documentation

- **chglog:** add 'ci' as 'CI' configuration for 'CHANGELOG.md' ([440c1ed](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/440c1edde7c8b62919943c4f6ffa4c40bc54a14f))

### 🚀 CI

- **gitlab-ci:** support docker pull and push without remote ([c0becd7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/c0becd77921b7fdabe810e5f7983dd9f49c320ae))
- **gitlab-ci:** use 'CI_DEFAULT_BRANCH' to access 'develop' branch ([c0fc6dd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/c0fc6ddd3ade421fadb5d8df8b8f786137d2fdb0))
- **gitlab-ci:** change commit messages to tag name ([264dc2e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/264dc2e999bb16cae4c5a517df8863cc282384d2))
- **setup:** update Python package keywords hints ([3f5d7d1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3f5d7d187f8e65307a91f06fe0ac40b0aaf6d14a))


<a name="4.2.0"></a>
## [4.2.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/4.1.0...4.2.0) (2024-05-26)

### ✨ Features

- **entrypoint:** improve outputs logs upon delections ([fd25605](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/fd256050a79365d05a0bd3a9beaf71113cb85057))
- **main:** show newer updates message upon incompatible arguments ([2ca5244](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2ca5244b5bfed48408dc634cc58a36551510d5f7))
- **main, entrypoint:** implement '--dump' to dump JSON objects ([dc98c05](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/dc98c05c0e2785d5fffd03e36dfd5c8bbebd9330))

### 📚 Documentation

- **readme:** add 'gitlab-projects-settings' examples documentation ([4614846](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/4614846934f900fc8fa3644333732ed045f03d3b))


<a name="4.1.0"></a>
## [4.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/4.0.0...4.1.0) (2024-05-17)

### ✨ Features

- **entrypoint:** implement prompt confirmation upon deletions ([539ccf8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/539ccf8dc9329bc096ac3e6f9f6e2f1bb8aaad58))
- **gitlab:** isolate 'ProtectionLevels' enumeration ([18abccf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/18abccfc4124d1c7295ce4c8f5f9f83f5087bd4a))
- **main, gitlab:** handle '--protect-tags' default to 'no-one' ([6607c87](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/6607c87536dda09ff994cbcb523e7eb6788088e7))
- **requirements:** prepare 'questionary' library integration ([5007320](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/50073206afe64c82704cdf9177ea24a2adecd5a9))


<a name="4.0.0"></a>
## [4.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/3.0.0...4.0.0) (2024-05-15)

### ✨ Features

- **entrypoint, gitlab:** implement '--{disable,enable}-features' ([19791ac](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/19791ac6578aee830057f8840447db2e00b35b9b))
- **gitlab:** automatically wait for group and project deletions ([7f02512](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/7f0251254a1fff00fd33b61a24b02189b037c0a7))
- **gitlab:** isolate GitLab project features enumeration ([fae4640](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/fae4640f44f86e031058736b60be3075abe6e3a0))
- **gitlab:** prepare future access levels in 'project_reset_features' ([a42e515](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/a42e515deed4f8eeeec6d758197bd007a0b9ec34))
- **gitlab:** parse input features list and accept similar texts ([3df67d7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3df67d75b9fb1a2b8822c645480997d8fb3264f5))
- **main:** document optional '--' positional arguments separator ([878c719](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/878c719fcfedc43aa98ab90fbe4cab2eb97c22de))
- **main, gitlab:** implement '--reset-features [KEEP_FEATURES]' ([592a08c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/592a08c9111b7ffca8e0f47bd650723769ba754e))
- **main, gitlab:** implement '--available-features' for user help ([5c90151](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/5c90151d6ec9e7b858e468c7153fb2985713151b))
- **main, settings:** implement 'Settings' from 'gitlabci-local' ([29cac8b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/29cac8b59e4605f16cf80528f39e3a955bd84f7d))
- **main, upgrades:** implement 'Upgrades' from 'gitlabci-local' ([80665f0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/80665f08414fffff4f59b303fd9ae2850f8b401e))

### 🐛 Bug Fixes

- **entrypoint:** use full paths instead of 'id' integer fields ([d06b36e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/d06b36e84b63d121d09846dea69506e2338e27ed))
- **entrypoint:** avoid missing 'namespace_id' in 'User' responses ([17889e9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/17889e956fbbec41fc17217d88d0ecc3b0ad7a7a))
- **entrypoint:** refactor to return no error upon final actions ([4d379ba](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/4d379bade031c2912604550beaf6b80b79b2f7c9))
- **entrypoint, gitlab:** resolve Python typings new warnings ([51b4f44](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/51b4f449d1148298831a7b78ad66ecf3065ddb9a))
- **gitlab:** accept deletion denials in 'project_reset_members' ([3b261f2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3b261f269fa3225f5a01cd1acc2e501ea686b0df))
- **gitlab:** disable 'Repository' group feature after its members ([939c303](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/939c303113d53335e2de17d7f9c2ed10a3b9ffca))
- **gitlab:** disable all 'Repository' member features too ([42f3d18](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/42f3d180b18343de6d501d1f0f07619228ac1f5f))

### 🚜 Code Refactoring

- **gitlab:** isolate 'GitLabFeature.AccessLevels' constants ([9ba30b6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/9ba30b62c93de8d846e271a3fa0eed084d7fde8c))
- **gitlab:** isolate GitLab types to 'types/gitlab.py' ([7a5f5eb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/7a5f5eb450e66823506cc221398696fbb8572d0c))
- **gitlab:** optimize and centralize GitLab features handlings ([2c52366](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2c52366fe1bee8f5a589bf6060083e6ea1c0b563))

### 🧪 Test

- **version:** add 'DEBUG_VERSION_FAKE' for debugging purposes ([fe3acdf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/fe3acdf5df1db57d58792bb8a4ab2e27dbaa567b))

### ⚙️ Cleanups

- **entrypoint:** minor Python codestyle improvement ([66ddb28](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/66ddb2807e08ad96b2e0e8f5249d4d965e825a96))

### 🚀 CI

- **gitlab-ci:** handle optional parameters and multiline in 'readme' ([394f670](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/394f670e15e1e9cefcba59e6b5979454b67828c8))
- **gitlab-ci:** detect 'README.md' issues in 'readme' job ([094e565](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/094e565ea5b5dfc219f95bb3256d31c640b788ff))
- **gitlab-ci:** implement 'images' and use project specific images ([dd08c4a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/dd08c4a1e69823176cea1c7ff3a10fd1c62b63f3))
- **gitlab-ci:** deprecate requirements install in 'lint' job ([b7b7aa7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/b7b7aa7b96083aa8ce61a7d40d0178afa111d29e))
- **gitlab-ci:** support multiple 'METAVAR' words in 'readme' job ([2b6da44](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2b6da44bf4298d281637b114828ebd33d3bba43a))


<a name="3.0.0"></a>
## [3.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/2.1.0...3.0.0) (2024-05-06)

### ✨ Features

- **cli, gitlab:** implement '--{archive,unarchive}-project' ([be6c241](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/be6c2415d618bf362bbda6828350120fc66bd29f))
- **cli, gitlab:** implement '--delete-{group,project}' ([3184259](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/318425966e008bf82244237dcaf6cda58cdd1679))
- **cli, gitlab:** implement '--run-housekeeping' ([2824960](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/282496067d8c7e591b21fba0c9e9c64a8800e0d7))
- **entrypoint:** always flush progress output logs ([d170a82](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/d170a82aeabe7d341cc40ca4b7ed37eacc9f4782))
- **entrypoint:** preserve main group description if exists ([f6f8a21](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f6f8a21e726cd5823fa9cc610bd8134c60797805))
- **entrypoint, gitlab:** adapt name for '--update-description' ([2a5b165](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2a5b16595958ac7c2b7f22af6e6e4ba26bab0b8e))
- **entrypoint, gitlab:** add support for user namespace projects ([1629e28](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/1629e28d593082eeed30bdeef4b211faecf5c3ed))
- **gitlab:** detect 'Token Access' usage for 'CI/CD' features ([24fb65a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/24fb65a11220f2f54a4e3e712e1d3c697f31bd7b))
- **gitlab:** detect multiple branches to keep 'Merge requests' ([2130b2a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2130b2a87b1fbda05374c0d43252c5fbee15cc04))
- **namespaces:** migrate 'Helper' class to 'Namespaces' class ([81dbd95](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/81dbd95e0be6cd58df4479b8446ed227dc823381))

### 🐛 Bug Fixes

- **entrypoint:** enforce against missing '.description' values ([85e6d91](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/85e6d9180ffd10086c6e8d068ca4862aaa7f9a74))
- **entrypoint:** detect if GitLab actions can continue ([3074446](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/307444694fcb9c5ef1f6b76d9982559699c1cc6d))
- **entrypoint:** resolve support for private user namespaces ([ec9092a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/ec9092a8fa399a7224a5e577079a504eb6b08f19))
- **gitlab:** get all members in 'project_reset_members' ([7db707c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/7db707c95c875e08719cc003c9fb516c5acff186))
- **gitlab:** get all branches and tags upon 'list()' calls ([5a46bf2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/5a46bf2d2712df3bea8047aa1c99d58d8ed569c4))
- **gitlab:** delay groups deletion by 10s and projects by 5s ([e56e054](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/e56e0548cab97c3aa39806685350edb6729f3e04))
- **gitlab:** enforce 'group_delete' usage in '--dry-run' mode ([29bdd98](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/29bdd98429292aa0f0ef155a45387454a11a602a))

### ⚙️ Cleanups

- **gitlab:** minor comments changes in 'project_reset_features' ([3470932](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3470932b0306a49f4d300536f2b778c551dc98ee))

### 🚀 CI

- **gitlab-ci:** move 'readme' job after 'build' and local 'install' ([cc44651](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/cc44651d87ffeb7c13b4dc4892faf3ffbaea49cd))


<a name="2.1.0"></a>
## [2.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/2.0.2...2.1.0) (2024-04-28)

### ✨ Features

- **entrypoint:** keep description if already contains group ([abe2d34](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/abe2d3419926fd4d265c39278d56d80957b22c06))
- **entrypoint:** sort groups and projects recursively ([d2fa32c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/d2fa32c56cc8c0242c154e8b05e31927ab54a1c5))

### 🐛 Bug Fixes

- **entrypoint:** fix project '--update-description' logs output ([3861e78](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3861e78dd491e6acc862214ba7fca8200c0d0d82))


<a name="2.0.2"></a>
## [2.0.2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/2.0.1...2.0.2) (2024-04-28)

### ✨ Features

- **main:** limit '--help' width to terminal width or 120 chars ([53916fd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/53916fda053a74f712147b3f3b7ff05fc31708bd))

### 📚 Documentation

- **readme:** document GitLab tokens' creation instructions ([5253faa](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/5253faaf37efb24eca38a3d30a3ca3665d0ef0f1))

### 🚀 CI

- **gitlab-ci:** disable 'typing' mypy caching with 'MYPY_CACHE_DIR' ([efeca44](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/efeca449553840bf1afaee2203a70164b8825483))


<a name="2.0.1"></a>
## [2.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/2.0.0...2.0.1) (2024-04-27)

### ✨ Features

- **entrypoint, gitlab:** isolate 'GitLabFeature.Helper.capitalize' ([7e25627](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/7e25627ebc82fb051fea7bb5e09c5e504dbf0e33))

### 🐛 Bug Fixes

- **entrypoint:** fix description updates faulty descriptions ([98a6e75](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/98a6e7559b5202c50f79b8e0505e7d7adae0cbb7))
- **entrypoint, gitlab:** implement description to name fallbacks ([11c931f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/11c931f886583dcc2bed26e149f96101bf664010))


<a name="2.0.0"></a>
## [2.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/1.1.0...2.0.0) (2024-04-27)

### ✨ Features

- **cli:** isolate 'features/settings.py' to 'cli/entrypoint.py' ([97b1214](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/97b121457c21b06e07edc6be8e27c5ae26e61c35))
- **main:** change '--set-description' metavar to 'TEXT' ([9640f6f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/9640f6fbe3df0c822fef2c6cf1d877b5e88f3b1f))
- **main:** align 'RawTextHelpFormatter' to 30 chars columns ([d9e6273](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/d9e6273755463173288f0c038ffcb8a7b66e6f0d))
- **settings:** change project/group descriptions color ([7dfaea1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/7dfaea1ef3b38997bc1181c0fe61f535ce4e31e4))

### 🐛 Bug Fixes

- **gitlab:** enforce '--dry-run' usage and improve Python codestyle ([bc1203a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/bc1203a63997101bba72814c206c99fad9304543))
- **settings:** apply 'subgroup' feature to subgroup groups ([977596e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/977596eb4d2ebfd4ffb6ed95e55b4ca89ff12ed1))

### 🚜 Code Refactoring

- **entrypoint:** minor Python codestyle improvements ([3b559f4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3b559f4b814b45eeaef5201756c289f83d007ab0))
- **src:** isolate all sources under 'src/' ([48f5d40](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/48f5d40b0813e40f8028289f55ddca6a672bdae9))

### 📚 Documentation

- **readme:** regenerate '--help' details in 'README.md' ([784121b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/784121b80313b62d526926d63b71073848af1653))

### ⚙️ Cleanups

- **gitlab:** minor Python codestyle improvements ([b32f815](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/b32f8158937709f269a455b5a89e4c2d0a3f06c4))
- **settings:** minor Python codestyle improvements ([f1c179d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f1c179dd3b16ff4466e021a1d1cb04730a9a805f))
- **src:** ignore 'import-error' over '__init__' and '__main__' ([2fad230](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/2fad2300cb63867978ae1d3ff6038bbc4bbe8ac5))

### 🚀 CI

- **gitlab-ci:** implement 'readme' local job to update README details ([3ba2118](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/3ba21189642ab01762d3e5a8cd6fb7b47b3f0e1a))
- **gitlab-ci, setup:** migrate to 'src' sources management ([388187f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/388187f9102982375fdb5dbc176aba019cccbb12))


<a name="1.1.0"></a>
## [1.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/1.0.1...1.1.0) (2024-04-25)

### ✨ Features

- **main:** rename '--avoid-*' parameters to '--exclude-*' ([f70ae44](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/f70ae4446d8ceaafa6ff992adc1596a95e0a3f45))

### 🚜 Code Refactoring

- **settings:** minor functions codestyle improvement ([e22206e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/e22206ef37f070db6e7d51ac096ab577647fdeb8))


<a name="1.0.1"></a>
## [1.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/compare/1.0.0...1.0.1) (2024-04-24)

### 📚 Documentation

- **setup:** fix PyPI 'gitlab-projects-settings' documentation ([66f2f97](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/66f2f976c97ae9a86f3151509f0035a867a0d1ff))


<a name="1.0.0"></a>
## [1.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commits/1.0.0) (2024-04-24)

### ✨ Features

- **gitlab-projects-settings:** initial sources implementation ([13a723f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-settings/commit/13a723fd4f04cc871567944d7c978bc23b55eed6))


