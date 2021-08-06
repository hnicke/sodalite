# Changelog

<!--next-version-placeholder-->

## v0.21.34 (2021-08-06)
### Fix
* Fix urwid display error ([#237](https://github.com/hnicke/sodalite/issues/237)) ([`eb89c43`](https://github.com/hnicke/sodalite/commit/eb89c43a9057f1c261ec619017fcda860010ae02))

## v0.21.33 (2021-08-06)
### Fix
* Fix arch linux packaging ([`2d06338`](https://github.com/hnicke/sodalite/commit/2d06338a868ac075fb1210897f1c8dd6cad8844d))

## v0.21.32 (2021-08-06)
### Fix
* Replace 'vim' hook with generic 'edit' hook ([#236](https://github.com/hnicke/sodalite/issues/236)) ([`e24c4dc`](https://github.com/hnicke/sodalite/commit/e24c4dccfd9cd4348a2a95d8222edec2ea8c9382))

## v0.21.31 (2021-08-06)
### Fix
* Entries which end up having no key get a key reassigned eventually ([#235](https://github.com/hnicke/sodalite/issues/235)) ([`ad67c78`](https://github.com/hnicke/sodalite/commit/ad67c78f128a66798ace44d6f5d94ed7677ba58f))

## v0.21.30 (2021-08-06)
### Fix
* Do not crash if env var PWD is not set ([#234](https://github.com/hnicke/sodalite/issues/234)) ([`52a48c9`](https://github.com/hnicke/sodalite/commit/52a48c9d6ca3e8adf4c9bcf80123100acc69ee74))

## v0.21.29 (2021-08-06)
### Fix
* Fix debian repository dispatch ([`9655e29`](https://github.com/hnicke/sodalite/commit/9655e292672f392124c927641bf5dfec82a754b8))

## v0.21.28 (2021-08-06)
### Fix
* Dispatch add_package event to debian repository ([#230](https://github.com/hnicke/sodalite/issues/230)) ([`bfeadd5`](https://github.com/hnicke/sodalite/commit/bfeadd5d860a296d78b4072321b6f426a3508847))

## v0.21.27 (2021-08-06)
### Fix
* Test automated release to debian repository ([`2218594`](https://github.com/hnicke/sodalite/commit/22185940685d5ae47686f000f6405789f19b62ea))

## v0.21.26 (2021-08-05)
### Fix
* Upload debian package to release ([`dfe0522`](https://github.com/hnicke/sodalite/commit/dfe052206df90de9b249555a730653fdff3c79a3))

## v0.21.25 (2021-08-05)
### Fix
* Fix file preview with older versions of watchdog (like 0.9.0) ([#228](https://github.com/hnicke/sodalite/issues/228)) ([`1ce79b3`](https://github.com/hnicke/sodalite/commit/1ce79b35231ccfff622677edea98c1dba3afd660))
* Fix shell integration on ubuntu ([#227](https://github.com/hnicke/sodalite/issues/227)) ([`9c947f9`](https://github.com/hnicke/sodalite/commit/9c947f9c5a75efffad89d907c9bd4ef7e31d4670))

## v0.21.24 (2021-08-05)
### Fix
* Unpin dependencies ([#224](https://github.com/hnicke/sodalite/issues/224)) ([`085b580`](https://github.com/hnicke/sodalite/commit/085b580306d89f94625feacd839228a2cc3f2c21))

## v0.21.23 (2021-08-05)
### Fix
* Fix shipping package data ([#220](https://github.com/hnicke/sodalite/issues/220)) ([`11bb034`](https://github.com/hnicke/sodalite/commit/11bb034254a9d2983ebec9554de4ea871463a828))

## v0.21.22 (2021-08-05)
### Fix
* Ship missing configuration file ([#219](https://github.com/hnicke/sodalite/issues/219)) ([`1b3707b`](https://github.com/hnicke/sodalite/commit/1b3707bba176458e804d7874064c2607e62e7e5e))

## v0.21.21 (2021-08-05)
### Fix
* Gracefully exit when config file was not found ([#218](https://github.com/hnicke/sodalite/issues/218)) ([`ae4fef4`](https://github.com/hnicke/sodalite/commit/ae4fef484a0fbee625a62f475cb0d44543c975f0))

## v0.21.20 (2021-08-05)
### Fix
* Fix call to watchdog ([#217](https://github.com/hnicke/sodalite/issues/217)) ([`c260cab`](https://github.com/hnicke/sodalite/commit/c260cab96e4f9b9cedd5a741858b1137d0316aa4))

## v0.21.19 (2021-08-04)
### Fix
* Suggest 'vim' action only for plain text files ([#215](https://github.com/hnicke/sodalite/issues/215)) ([`5f647ee`](https://github.com/hnicke/sodalite/commit/5f647ee24d5d79b2623ac07afa6f6f20ce1bbdb0))

## v0.21.18 (2021-08-04)
### Fix
* In help screen, hide unsuitable actions in regards to current context ([#214](https://github.com/hnicke/sodalite/issues/214)) ([`25020f7`](https://github.com/hnicke/sodalite/commit/25020f757c6ac010580a2a9f8977cd3041c16604))

## v0.21.17 (2021-08-04)
### Fix
* Improve startup time ([#212](https://github.com/hnicke/sodalite/issues/212)) ([`2053052`](https://github.com/hnicke/sodalite/commit/2053052b22c5f7a71a285c7b55aa30791015c490))

## v0.21.16 (2021-08-04)
### Fix
* Make filesystem change detection more reliable ([#211](https://github.com/hnicke/sodalite/issues/211)) ([`903c5fa`](https://github.com/hnicke/sodalite/commit/903c5fa0a6ece6dd5cb77c3f820d795a54cc59c0))

## v0.21.15 (2021-08-04)
### Fix
* Fix external filesystem change detection ([#210](https://github.com/hnicke/sodalite/issues/210)) ([`0eb855a`](https://github.com/hnicke/sodalite/commit/0eb855afce07e335f72a0708ed6d2ad97049144e))

## v0.21.14 (2021-08-04)
### Fix
* Fix bug in key assign algorithm which led to entries without keys ([`cd10e8f`](https://github.com/hnicke/sodalite/commit/cd10e8fb3de8cc4b5051bd150323d7996c1487ad))

## v0.21.13 (2021-08-04)
### Fix
* Handle non-existing files and directories in a better way ([`7e82f53`](https://github.com/hnicke/sodalite/commit/7e82f53054576ba51d2f2dfc06dfd9a6a08bd67a))

## v0.21.12 (2021-08-04)
### Fix
* Use brown instead of red highlight color in operate mode ([#205](https://github.com/hnicke/sodalite/issues/205)) ([`9e8a5c3`](https://github.com/hnicke/sodalite/commit/9e8a5c375c9ebeb3d3f0c5f59799f7b1d851e138))

## v0.21.11 (2021-08-04)
### Fix
* Update PKGBUILD checksums before publishing package to Aur ([#204](https://github.com/hnicke/sodalite/issues/204)) ([`447e382`](https://github.com/hnicke/sodalite/commit/447e382f1f45609abcb9462f1b10a61a150c12c9))

## v0.21.10 (2021-08-04)
### Fix
* Bump version in PKGBUILD accordingly ([#203](https://github.com/hnicke/sodalite/issues/203)) ([`0c16aed`](https://github.com/hnicke/sodalite/commit/0c16aed9edde661ba6018d416a57bb05c867d4b2))

## v0.21.9 (2021-08-04)
### Fix
* For Aur package, use PKGBUILD from this repo ([#202](https://github.com/hnicke/sodalite/issues/202)) ([`e32dc3c`](https://github.com/hnicke/sodalite/commit/e32dc3c610ddebf05484c48d54f039c7a0260cab))

## v0.21.8 (2021-08-04)
### Fix
* Improve pipeline speed ([#199](https://github.com/hnicke/sodalite/issues/199)) ([`a401de5`](https://github.com/hnicke/sodalite/commit/a401de50afebee3d9566e817385da89448d303d6))

## v0.21.7 (2021-08-04)
### Fix
* Auto-bump aur package after release ([#198](https://github.com/hnicke/sodalite/issues/198)) ([`4171660`](https://github.com/hnicke/sodalite/commit/417166004c8070c1f598cfba8ef0280095ba31ee))

## v0.21.6 (2021-08-04)
### Fix
* Do not bundle tests package ([#197](https://github.com/hnicke/sodalite/issues/197)) ([`98f0fbf`](https://github.com/hnicke/sodalite/commit/98f0fbf217fb39408b1c667ea4ba767712116db3))

## v0.21.5 (2021-08-04)
### Fix
* Ditch poetry ([#196](https://github.com/hnicke/sodalite/issues/196)) ([`d65cef3`](https://github.com/hnicke/sodalite/commit/d65cef396ca84381b48e5fc001e66e33cc189e9f))

## v0.21.4 (2021-08-04)
### Fix
* Remove obsolete make targets ([#195](https://github.com/hnicke/sodalite/issues/195)) ([`83fa7c1`](https://github.com/hnicke/sodalite/commit/83fa7c10e327e93e3376a39e2629760f268c573c))

## v0.21.3 (2021-08-04)
### Fix
* Fix file structure of sdist and wheel ([#193](https://github.com/hnicke/sodalite/issues/193)) ([`06187bf`](https://github.com/hnicke/sodalite/commit/06187bfee2f25f59295d5826c7fd23ca9eaa1e64))

## v0.21.2 (2021-08-02)
### Fix
* Bundle template configuration file next to code ([#189](https://github.com/hnicke/sodalite/issues/189)) ([`3c82cf2`](https://github.com/hnicke/sodalite/commit/3c82cf2be936fdbf67328d5a522df5450919aa39))

## v0.21.1 (2021-08-02)
### Fix
* Bundle assets ([#188](https://github.com/hnicke/sodalite/issues/188)) ([`2423f78`](https://github.com/hnicke/sodalite/commit/2423f78c9409fed3342f05e550804f3795931afe))

## v0.21.0 (2021-08-02)
### Feature
* Drop support for system-wide configuration file ([#187](https://github.com/hnicke/sodalite/issues/187)) ([`4688161`](https://github.com/hnicke/sodalite/commit/46881616d540a8b07a4ac2fc2472f54274e4b8c9))

## v0.20.5 (2021-08-02)
### Fix
* Use absolute instead of relative links in README ([#185](https://github.com/hnicke/sodalite/issues/185)) ([`08ab712`](https://github.com/hnicke/sodalite/commit/08ab71243727daa118497f6cf4b7ae0eb3fc5e55))

## v0.20.4 (2021-08-02)
### Fix
* Fix output of `sodalite --version` ([#183](https://github.com/hnicke/sodalite/issues/183)) ([`37ec478`](https://github.com/hnicke/sodalite/commit/37ec4789f0a46b67591a281a1429c1cbc2daa55b))

## v0.20.3 (2021-08-02)
### Fix
* Fix build in release job ([#182](https://github.com/hnicke/sodalite/issues/182)) ([`9664e91`](https://github.com/hnicke/sodalite/commit/9664e91bc603151ed8195b56276cd3bc5a390f4c))

## v0.20.2 (2021-08-02)
### Fix
* Trigger a patch release to test the semantic release ([#179](https://github.com/hnicke/sodalite/issues/179)) ([`170e175`](https://github.com/hnicke/sodalite/commit/170e1750f315128df32b5f27a2de2df8ba0f5a42))
