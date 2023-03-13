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
