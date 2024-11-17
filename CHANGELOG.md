#### [2.0.1](https://github.com/julianneswinoga/flightgear-python/compare/2.0.0...2.0.1)

> 17 November 2024

- Fix readthedocs poetry config [`f4842e0`](https://github.com/julianneswinoga/flightgear-python/commit/f4842e08d00e5912964ea54b4d7f416415cc2da9)
- Add linux 3.13, windows 3.12.7 to CI matrix [`6cf4122`](https://github.com/julianneswinoga/flightgear-python/commit/6cf4122c5deee75a8a07d0658bf6a55e980510af)

### [2.0.0](https://github.com/julianneswinoga/flightgear-python/compare/1.7.0...2.0.0)

> 17 November 2024

- Drop support for python 3.6, 3.8 is minimum now [`65ca345`](https://github.com/julianneswinoga/flightgear-python/commit/65ca345521532370dee0ab61251a585390bf8ec6)
- Check for telnet `BrokenPipeError`, better match on bad telnet cmd [`dd28aad`](https://github.com/julianneswinoga/flightgear-python/commit/dd28aad375225126533e87ddd8836fddfa412a08)
- Fix `version.parse()` in `do_release.py` [`0a65f24`](https://github.com/julianneswinoga/flightgear-python/commit/0a65f24c90f7fc132744a4701ea22d908ba6a4ba)
- Add `coverage[toml]` now that coverage settings are in `pyproject.toml` [`58bd492`](https://github.com/julianneswinoga/flightgear-python/commit/58bd492804d93c7bf2df56982e79b1506ca9357a)
- Pre-check for required programs in `fg_full_integration_test.sh` [`c96de5c`](https://github.com/julianneswinoga/flightgear-python/commit/c96de5c70697c1a131eb0ff73cf187ac7f0be9ac)
- Explicitly search for jsbsim root dir [`491feea`](https://github.com/julianneswinoga/flightgear-python/commit/491feea5aa3c1523aefff2f00e5cd1f3557b952c)
- Don't explicitly specify 3.6 in `run_tests.sh` [`a046635`](https://github.com/julianneswinoga/flightgear-python/commit/a04663514468baf9cb9eacc6310bd863d4f6d633)
- Minor comment for `do_release.py` [`2991aa4`](https://github.com/julianneswinoga/flightgear-python/commit/2991aa4e8d3adcaaabbc27d4ed3f3d45f37c3331)

#### [1.7.0](https://github.com/julianneswinoga/flightgear-python/compare/1.6.0...1.7.0)

> 19 May 2024

- Implement auto-version parsing for the `FGConnection` classes (`FDMConnection`, `CtrlsConnection`, `GuiConnection`) [`9e51476`](https://github.com/julianneswinoga/flightgear-python/commit/9e514762660b74352a6b088beb8f8c93b1ce1a23)
- Add integration test to run all example code, enable rx_proc.daemon [`b537012`](https://github.com/julianneswinoga/flightgear-python/commit/b53701278193906e0005721c2663e8861fec7cc1)
- Update docs/examples to use auto versioning [`0f814e5`](https://github.com/julianneswinoga/flightgear-python/commit/0f814e59618cd9c8a08b74ee557ada761034ef25)

#### [1.6.0](https://github.com/julianneswinoga/flightgear-python/compare/1.5.0...1.6.0)

> 21 January 2024

- Create `Struct` directly in interface files, rather than using a `dict` and creating the `Struct` in `fg_if.py` [`091519b`](https://github.com/julianneswinoga/flightgear-python/commit/091519b21a4b8e02e6002ac053400a49d156a153)
- Expose `rx_timeout_s` to the `FGConnection` classes (`FDMConnection`, `CtrlsConnection`, `GuiConnection`) [`9682f9a`](https://github.com/julianneswinoga/flightgear-python/commit/9682f9af298eb2740604e304b116fe9818bae75e)
- Fix `rx_timeout_s`, add RX timeout tests [`f7981b1`](https://github.com/julianneswinoga/flightgear-python/commit/f7981b180f5791d4d489956417c359db7662807c)
- Fix running `black` in CI (it wasn't actually being enforced) [`484c36b`](https://github.com/julianneswinoga/flightgear-python/commit/484c36b93f9956c295e6f3ec684447764b0b1586)
- Update copyright year in license, docs [`8bf1c29`](https://github.com/julianneswinoga/flightgear-python/commit/8bf1c2913bf9bfb6caf6b6fda31cdc368bf69abb)

#### [1.5.0](https://github.com/julianneswinoga/flightgear-python/compare/1.4.1...1.5.0)

> 2 January 2024

- User-wise, renamed `PropsConnection` to `TelnetConnection`
  - Add deprecation test for `PropsConnection`->`TelnetConnection`, filter out annoying `DeprecationWarning: the imp module is deprecated` from `import jsbsim` [`5d02496`](https://github.com/julianneswinoga/flightgear-python/commit/5d024964bcaa9d68b530778cd576302dc4680474)
  - Refactor Telnet and HTTP classes to have the same base class [`fb7b392`](https://github.com/julianneswinoga/flightgear-python/commit/fb7b392b2881e36230e5400d0dc1ab9d4be0b1a3)
- Property-tree-things documentation cleanup, change intersphinx python to point at 3.6 [`5556f77`](https://github.com/julianneswinoga/flightgear-python/commit/5556f7740a005e5548f8e3c6b5c965a4596356a6)
- Add `timeout_s` param to `HTTPConnection` [`b9aa576`](https://github.com/julianneswinoga/flightgear-python/commit/b9aa576dea440a1c99caa72f6ac42fdaa21bafae)
- Compare value types in http vs telnet test, parameterize to reduce duplicate code [`b4f1a9f`](https://github.com/julianneswinoga/flightgear-python/commit/b4f1a9f24432c075030e3e900f92c9e1ad674385)
- Move telnet `sock.settimeout()` from `_send_cmd_get_resp()` to `connect()` [`620bb28`](https://github.com/julianneswinoga/flightgear-python/commit/620bb28e62473a2b3d0675eade6f181a85f06dd6)
- Minor docs changes [`aedb32a`](https://github.com/julianneswinoga/flightgear-python/commit/aedb32a80954942899a27cb3c982d1dff472ff22)

#### [1.4.1](https://github.com/julianneswinoga/flightgear-python/compare/1.4.0...1.4.1)

> 1 January 2024

- Much better testing infrastructure (Full integration testing happening in CI!)
  - Add black to poetry [`c6bbc98`](https://github.com/julianneswinoga/flightgear-python/commit/c6bbc98832fff03a7ba91550bd2989a6a0d8631f)
  - Headless FlightGear script [`95ed5e0`](https://github.com/julianneswinoga/flightgear-python/commit/95ed5e0dcfeac8846cebdaf8931ecd4aaa192258)
  - Add integration test script to CircleCI [`76e7043`](https://github.com/julianneswinoga/flightgear-python/commit/76e7043870f8a42ffb66f8fa51eb9c7c417656b4)
  - Changed a lot of CI stuff, added http FG integration testing [`23b3e15`](https://github.com/julianneswinoga/flightgear-python/commit/23b3e15f4554478931b1a885d218213b726bfaf3)
  - Add lots more tests to cover expected errors [`4f80df4`](https://github.com/julianneswinoga/flightgear-python/commit/4f80df4f1c9bcf8bb9095b75d0ed939f3de061ff)
  - Add flake8 dependency, needed to downgrade sphinx [`a73cf48`](https://github.com/julianneswinoga/flightgear-python/commit/a73cf48d9d0a6b5fcc792e64f212b7e21dffe707)
  - Add HTTPConnection unit tests [`d3a5812`](https://github.com/julianneswinoga/flightgear-python/commit/d3a581226c93750f139bf7f881c45bc9454a22c7)
  - Add Gui integration tests [`bbdf925`](https://github.com/julianneswinoga/flightgear-python/commit/bbdf9257f15c564e6313f2761d2e1e549283ffb8)
  - Add Ctrls integration tests [`0f3049c`](https://github.com/julianneswinoga/flightgear-python/commit/0f3049cd9df633f360f0021dc7aff6dbe0e5ca13)
  - Add FDM integration tests [`639d211`](https://github.com/julianneswinoga/flightgear-python/commit/639d211289c1f85cfd1c72207a0c1281b7209326)
  - Close sockets after running unit tests [`3406060`](https://github.com/julianneswinoga/flightgear-python/commit/34060606be82a193591369341d17c42c582c39a8)
  - Allow arguments to be passed to pytest in run_tests.sh [`c099bc8`](https://github.com/julianneswinoga/flightgear-python/commit/c099bc8ca62338a00a15c2eabdd515aa72f5b9cd)
  - Change from localhost to 127.0.0.1 for nc connection in integration script (doesn't work on some computers?) [`205f696`](https://github.com/julianneswinoga/flightgear-python/commit/205f6960513acd98b76172ca8eb2aee40f72b8dc)
  - Add requests-mock dev dependency [`3e28f9a`](https://github.com/julianneswinoga/flightgear-python/commit/3e28f9a52177fd5b124959b973267ca9b771784d)
  - Rename integration tests [`66bcfc9`](https://github.com/julianneswinoga/flightgear-python/commit/66bcfc9ed505f9af10a56c6ae07171db92c098d4)
  - Add telnet integration tests [`9b949e0`](https://github.com/julianneswinoga/flightgear-python/commit/9b949e0c71b208a22b2aaf97913524c273de11c0)
  - Add HTTP vs Telnet comparison integration tests [`1513145`](https://github.com/julianneswinoga/flightgear-python/commit/15131454f3117b6d49272c9ad5f68942d5428608)
- Fixed broken dev dependencies in pyproject.toml (rather than sketchy CI) [`5d95a67`](https://github.com/julianneswinoga/flightgear-python/commit/5d95a67ca479458da4bb175706ccbf0ede4f93e0)
- Code format using black [`cea008f`](https://github.com/julianneswinoga/flightgear-python/commit/cea008fd415173f9a19f0787d871ac30eb2aafee)
- Abstract out cache templates in yaml, tried just poetry for Windows [`daf927d`](https://github.com/julianneswinoga/flightgear-python/commit/daf927dc6555aef5dc61e3ff09169eece31f237d)
- Add lint job to circleci, run black [`548d9dd`](https://github.com/julianneswinoga/flightgear-python/commit/548d9ddc38276b3ce547aee3253316ff3bac8129)
- Add flake8 configuration, run flake8: [`de9aecb`](https://github.com/julianneswinoga/flightgear-python/commit/de9aecb81afd6f9a83d4bcb6b2cf0cb25931334a)
- Add poetry linux cache [`ea78a13`](https://github.com/julianneswinoga/flightgear-python/commit/ea78a1311c8dac80517c305e31a13252018d5246)
- Windows cache working, but doesn't seem to save any time :/ [`d7ef95b`](https://github.com/julianneswinoga/flightgear-python/commit/d7ef95b0a5cea1eb983bfb985e4481314bea10b4)
- Add `fgdata` cache [`87183a7`](https://github.com/julianneswinoga/flightgear-python/commit/87183a727d2f0a5244c29d3bc2d7e0f339578240)
- Check coveralls token before running [`274dd03`](https://github.com/julianneswinoga/flightgear-python/commit/274dd03d242374928f62921aebf1d72acc029832)
- Add flake8 to circleci lint job [`0f7c9a3`](https://github.com/julianneswinoga/flightgear-python/commit/0f7c9a3338465c5d9ff587130531fe7c76570feb)
- Move `fg_rx_sock.settimeout` from `_rx_process()` to `connect_rx()` [`7e5a47b`](https://github.com/julianneswinoga/flightgear-python/commit/7e5a47bcf06c14afb2ed8b8faa0820280575c8cc)
- Add link to pypistats.org in downloads badge [`75aa9c0`](https://github.com/julianneswinoga/flightgear-python/commit/75aa9c0796b1abf3b24ae98dae955b041a92674c)
- Make socket blocking? Fix weird Windows error: [`c5b8a80`](https://github.com/julianneswinoga/flightgear-python/commit/c5b8a80d8213c0ba2ac03458ce02bc2f83714e53)
- Add `.xml` coverage output to `.gitignore` [`c657fbb`](https://github.com/julianneswinoga/flightgear-python/commit/c657fbb3a29380703b80bb447180be07d560b186)

#### [1.4.0](https://github.com/julianneswinoga/flightgear-python/compare/1.3.0...1.4.0)

> 19 November 2023

- Add HTTP client [`110561a`](https://github.com/julianneswinoga/flightgear-python/commit/110561aaa108d713e8348e0583e74e72c3fb96e6) (thanks @juhannc !)
- Fix poetry.lock to support old poetry version [`39874a5`](https://github.com/julianneswinoga/flightgear-python/commit/39874a58ca3909e25d45bfadd7fcd5e86d8c146c)
- Add simple_http to examples and check README [`0932606`](https://github.com/julianneswinoga/flightgear-python/commit/09326066585f640b1dbc52d899afd599ba2e0db4)
- Require Windows build to succeed to publish packages [`7c1d344`](https://github.com/julianneswinoga/flightgear-python/commit/7c1d344f967a96c2350582c3fe371c43e2418106)

#### [1.3.0](https://github.com/julianneswinoga/flightgear-python/compare/1.2.2...1.3.0)

> 4 June 2023

- Add GUI interface
- Add basic GUI documentation [`75f352b`](https://github.com/julianneswinoga/flightgear-python/commit/75f352b60800e5a0c639367cb4b284f9529a5bff)
- Add `simple_wing_level.py` example [`#7`](https://github.com/julianneswinoga/flightgear-python/pull/7)
- Add GUI pickling test, update poetry.lock [`cd0ed18`](https://github.com/julianneswinoga/flightgear-python/commit/cd0ed185ddf6e76118d8cb212d1983e29031b30d)

#### [1.2.2](https://github.com/julianneswinoga/flightgear-python/compare/1.2.1...1.2.2)

> 13 March 2023

- Fix Windows build again [`3e9c7d4`](https://github.com/julianneswinoga/flightgear-python/commit/3e9c7d461f24d2ccdf566fea95de6f97ad85309c)
  - explicitly specify localhost for `fgfs`
  - add `if __name__=='__main__'` (needed for multiprocessing on Windows)
  - change from `Flag` to `Bit`, switch from `multiprocessing` to `multiprocess` (`pickle` to `dill`)
- Add `Bytes` to doc handler, specify `Bits` in docs [`8e50e3f`](https://github.com/julianneswinoga/flightgear-python/commit/8e50e3f202135a73e976361db0714fb4dd4968ab)

#### [1.2.1](https://github.com/julianneswinoga/flightgear-python/compare/1.2.0...1.2.1)

> 12 March 2023

- Add support for Windows [`#5`](https://github.com/julianneswinoga/flightgear-python/pull/5)
- Add Windows executor to CircleCI [`227e8f5`](https://github.com/julianneswinoga/flightgear-python/commit/227e8f563807aa57dedf8fe09f98f91603b95afc)
- Change `jsbsim_wrapper.py` test to close files before JSB inits [`57e13b0`](https://github.com/julianneswinoga/flightgear-python/commit/57e13b0ce6072744a3dea7aa40aa3d106d05443e)
- Convert `Padding` to `Bytes` [`ab13cc7`](https://github.com/julianneswinoga/flightgear-python/commit/ab13cc75cb0debeb7f2dedc77d532436cf9f8bdc)
- Add SO_REUSEADDR to fg_rx_sock [`7d8f649`](https://github.com/julianneswinoga/flightgear-python/commit/7d8f649b7cb3e06128fa86b27fbdd01449f90a58)

#### [1.2.0](https://github.com/julianneswinoga/flightgear-python/compare/1.1.1...1.2.0)

> 12 February 2023

- Add Controls interface (v27) and simple_ctrls.py example [`31328ea`](https://github.com/julianneswinoga/flightgear-python/commit/31328eacea1f5a3eb4307fdeea8c9bd488acc91b)
- Add basic docs for ctrls interface, fix up represent_object() to handle all the new types [`300787f`](https://github.com/julianneswinoga/flightgear-python/commit/300787f63fd88929541d2065c5663656afe41f8f)
- Add poll to simple_fdm example [`951c1e6`](https://github.com/julianneswinoga/flightgear-python/commit/951c1e6b8168be75e2f06631d8f451f02ef0138a)
- Change RX callback type from Struct to Container [`7d38efd`](https://github.com/julianneswinoga/flightgear-python/commit/7d38efd7c6444a4203e5caf1884b2318434b5567)

#### [1.1.1](https://github.com/julianneswinoga/flightgear-python/compare/1.1.0...1.1.1)

> 6 December 2022

- Add JSBSim integration test (only for FDMv24 for now) [`988ca66`](https://github.com/julianneswinoga/flightgear-python/commit/988ca66ca2572fa10078595c418500c231e568d5)
- Removed build_and_upload.sh [`62bba22`](https://github.com/julianneswinoga/flightgear-python/commit/62bba22a01d98cd634f6e24ffba63e238c2f5fe3)
- Add minor FDM check to wait for child process to be started [`757ca6b`](https://github.com/julianneswinoga/flightgear-python/commit/757ca6b6a9e0b95c41e20e79f3af37510ff4f7d4)

#### [1.1.0](https://github.com/julianneswinoga/flightgear-python/compare/1.0.4...1.1.0)

> 26 October 2022

- Allow a RX-only FDM loop (i.e. you just want to receive FDM data from FlightGear)

#### [1.0.4](https://github.com/julianneswinoga/flightgear-python/compare/1.0.3...1.0.4)

> 31 August 2022

- Update pip/poetry when publishing [`498026a`](https://github.com/julianneswinoga/flightgear-python/commit/498026a180577dd6aef09b2ab195415ad2242a00)
- readthedocs poetry 1.1.15 [`9af4947`](https://github.com/julianneswinoga/flightgear-python/commit/9af4947943691c43aa8930d04df2989ba4c4784b)

#### [1.0.3](https://github.com/julianneswinoga/flightgear-python/compare/1.0.2...1.0.3)

> 31 August 2022

- Add more fdm unit tests [`d195247`](https://github.com/julianneswinoga/flightgear-python/commit/d19524757e6bbc943e0f1b9b69464fb8207e39cf)
- Add initial props unit tests [`fb133a6`](https://github.com/julianneswinoga/flightgear-python/commit/fb133a606b2fc478afa885ee51fe090a7536d920)
- CircleCI: update poetry version, store artifacts [`8a71fb2`](https://github.com/julianneswinoga/flightgear-python/commit/8a71fb29acf1b37140e9c9e759b4a21071aca0d0)
- Fix readthedocs.io config [`dda5410`](https://github.com/julianneswinoga/flightgear-python/commit/dda5410bf8269ea7c8ea209f6b282a83b43c4480)
- Minor do_release.py fix [`b0ed48b`](https://github.com/julianneswinoga/flightgear-python/commit/b0ed48b83cf945c41bf6cf45ff8619e253c50a2f)

#### [1.0.2](https://github.com/julianneswinoga/flightgear-python/compare/1.0.1...1.0.2)

> 30 August 2022

- Add changelog into rst documentation [`7922cd3`](https://github.com/julianneswinoga/flightgear-python/commit/7922cd30943cdf9c7148cf913737a6c1ac3b36fc)
- Fix up README.md [`0f8d2f4`](https://github.com/julianneswinoga/flightgear-python/commit/0f8d2f4a5d07592bfe216d7b48c292a0cd226a0d)
- Fix dependencies [`f1d32f6`](https://github.com/julianneswinoga/flightgear-python/commit/f1d32f6643dacc75725752118d86507eefa029f8)
- Fix ghr again [`e01e9d4`](https://github.com/julianneswinoga/flightgear-python/commit/e01e9d4fa97b581644a14b09008e3f5b631d27dc)

#### [1.0.1](https://github.com/julianneswinoga/flightgear-python/compare/1.0.0...1.0.1)

> 29 August 2022

- No public changes

#### 1.0.0

> 29 August 2022

- Initial release
