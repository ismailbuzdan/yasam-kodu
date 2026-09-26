# Third-party notices

## google-genai 2.25.0 (Stage 11B)

Official Google Gen AI Python SDK, Apache-2.0. Verified 2026-09-26 against
[pinned upstream license](https://github.com/googleapis/python-genai/blob/v2.25.0/LICENSE)
and [PyPI metadata](https://pypi.org/project/google-genai/2.25.0/).
Requires Python >=3.10; project Docker uses Python 3.11. Its httpx >=0.28.1/<1 and
pydantic >=2.12.5/<3 requirements admit the existing project pins. No legacy google-generativeai.
Apache-2.0 is compatible with this project's AGPL-3.0 distribution (see
[GNU compatibility guidance](https://www.gnu.org/licenses/license-compatibility.en.html)); preserve dependency license
and notice files. SDK copyright licensing does not replace Gemini API service/data-processing terms.

Newly resolved dependency license metadata was inspected in the rebuilt Docker environment:
google-auth 2.58.1, requests 2.34.2, tenacity 9.1.4 and distro 1.9.0: Apache-2.0;
websockets 16.1.1: BSD-3-Clause; sniffio 1.3.1: MIT OR Apache-2.0;
cryptography 50.0.1: Apache-2.0 OR BSD-3-Clause; pyasn1 0.6.4: BSD-2-Clause;
pyasn1-modules 0.4.2: BSD; urllib3 2.8.0 and charset-normalizer 3.5.1: MIT.
These permissive license families introduce no AGPL-3.0 conflict. No SDK extras installed.
This records the tested resolution, not a new full transitive lockfile; existing shared dependencies
retain their upstream notices. Recheck licenses when dependency versions change.

## pyswisseph 2.10.3.2

Source: [PyPI source distribution](https://pypi.org/project/pyswisseph/2.10.3.2/#files),
`pyswisseph.c` header and `LICENSE.txt`, verified 2026-09-17.

Copyright (c) 2007-2023 Stanislas Marquis <stan@astrorigin.com>

The wrapper is licensed under GNU AGPL version 3 or (at your option) any later version.
The project uses AGPL-3.0; see [LICENSE](LICENSE). Preserve upstream license files when redistributing dependencies.

## Swiss Ephemeris 2.10.03

The AGPL route is selected; the Professional License is not used.
The following notice is copied from `libswe/LICENSE` in the same pinned source distribution.

```text
/* Copyright (C) 1997 - 2021 Astrodienst AG, Switzerland.  All rights reserved.

  License conditions
  ------------------

  This file is part of Swiss Ephemeris.

  Swiss Ephemeris is distributed with NO WARRANTY OF ANY KIND.  No author
  or distributor accepts any responsibility for the consequences of using it,
  or for whether it serves any particular purpose or works at all, unless he
  or she says so in writing.

  Swiss Ephemeris is made available by its authors under a dual licensing
  system. The software developer, who uses any part of Swiss Ephemeris
  in his or her software, must choose between one of the two license models,
  which are
  a) GNU Affero General Public License (AGPL)
  b) Swiss Ephemeris Professional License

  The choice must be made before the software developer distributes software
  containing parts of Swiss Ephemeris to others, and before any public
  service using the developed software is activated.

  If the developer choses the AGPL software license, he or she must fulfill
  the conditions of that license, which includes the obligation to place his
  or her whole software project under the AGPL or a compatible license.
  See https://www.gnu.org/licenses/agpl-3.0.html

  If the developer choses the Swiss Ephemeris Professional license,
  he must follow the instructions as found in http://www.astro.com/swisseph/
  and purchase the Swiss Ephemeris Professional Edition from Astrodienst
  and sign the corresponding license contract.

  The License grants you the right to use, copy, modify and redistribute
  Swiss Ephemeris, but only under certain conditions described in the License.
  Among other things, the License requires that the copyright notices and
  this notice be preserved on all copies.

  Authors of the Swiss Ephemeris: Dieter Koch and Alois Treindl

  The authors of Swiss Ephemeris have no control or influence over any of
  the derived works, i.e. over software or services created by other
  programmers which use Swiss Ephemeris functions.

  The names of the authors or of the copyright holder (Astrodienst) must not
  be used for promoting any software, product or service which uses or contains
  the Swiss Ephemeris. This copyright notice is the ONLY place where the
  names of the authors can legally appear, except in cases where they have
  given special permission in writing.
*/
```
