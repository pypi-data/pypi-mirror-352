# PDKMaster integration with KLayout

This is PDKMaster module to provide interoperation with klayout.
This is WIP version with just the red tape setup for the project.

## Release history

* [v0.1.7.post1](https://gitlab.com/Chips4Makers/pdkmaster-io-klayout/-/commits/v0.1.7.post1):
  * Mark incompatible with klayout version >= 0.30
* [v0.1.7](https://gitlab.com/Chips4Makers/pdkmaster-io-klayout/-/commits/v0.1.7):
  * Fix pcell computation in klayout ([!1](https://gitlab.com/Chips4Makers/pdkmaster-io-klayout/-/merge_requests/1))
  * Update for split off pdkmaster.io modules and API update for PDKMaster v0.12.0
* [v0.1.6](https://gitlab.com/Chips4Makers/pdkmaster-io-klayout/-/commits/v0.1.6):
  * regular clean-up and code factoring
  * make some of the internal function public functions
  * support generating text
  * some smaller improvements changes, see commit log for details
  * improvements to the doit support
* [v0.1.5](https://gitlab.com/Chips4Makers/pdkmaster-io-klayout/-/commits/v0.1.5):
  * factor out common doit support code from PDK subprojects
  * signoff related fixes
* [v0.1.4](https://gitlab.com/Chips4Makers/pdkmaster-io-klayout/-/commits/v0.1.4):
  Sync with PDKMaster and signoff improvements
* [v0.1.3](https://gitlab.com/Chips4Makers/pdkmaster-io-klayout/-/commits/v0.1.3):
  * Update for allowing abutting for MinSpace rule primitive.
* [v0.1.2](https://gitlab.com/Chips4Makers/pdkmaster-io-klayout/-/commits/v0.1.2):
  * Subproject of project Arrakeen
  * Support for external layer properties for klayout technology
* v0.1.1: Some clean-up and implementation of klayout pcell library support for MOSFET and Via primitives.
* v0.1.0: First version with split-off code from PDKMaster as is.

## Project Arrakeen subproject

This project is part of Chips4Makers' [project Arrakeen](https://gitlab.com/Chips4Makers/c4m-arrakeen). It shares some common guide lines and regulations:

* [Contributing.md](https://gitlab.com/Chips4Makers/c4m-arrakeen/-/blob/redtape_v1/Contributing.md)
* [LICENSE.md](https://gitlab.com/Chips4Makers/c4m-arrakeen/-/blob/redtape_v1/LICENSE.md): license of release code
* [LICENSE_rationale.md](https://gitlab.com/Chips4Makers/c4m-arrakeen/-/blob/redtape_v1/LICENSE_rationale.md)
