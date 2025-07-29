# MyVaillant

[![PyPI](https://img.shields.io/pypi/v/MyVaillant)](https://pypi.org/project/MyVaillant/)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/rmalbrecht/MyVaillant/build.yml)

A Python library to interact with the API behind the myVAILLANT app ((and branded versions of it, such as the MiGo app from Saunier Duval). Needs at least Python 3.10.

> [!WARNING]  
> If you're using sensoAPP or the multiMATIC app, this library won't work for you. Try the [pymultiMATIC](https://github.com/thomasgermain/pymultiMATIC) library instead and check Vaillant's website for more information.

> [!WARNING]  
> This integration is not affiliated with Vaillant, the developers take no responsibility for anything that happens to your devices because of this library.

![MyVaillant](https://raw.githubusercontent.com/rmalbrecht/MyVaillant/main/logo.png)

# Install and Test

> [!WARNING]  
> 
> You need at least Python 3.10

```shell
pip install MyVaillant
```

or use Docker, if you just want to use it as a CLI tool:

```shell
docker run -ti ghcr.io/rmalbrecht/myvaillant:latest python3 -m MyVaillant.export user password brand --country country
```

# Usage

## Exporting Data about your System

```bash
python3 -m MyVaillant.export user password brand --country country
# See python3 -m MyVaillant.export -h for more options and a list of countries
```

The `--data` argument exports historical data of the devices in your system.
Without this keyword, information about your system will be exported as JSON.

## Exporting Energy Reports

```bash
python3 -m MyVaillant.report user password brand --country country
# Wrote 2023 report to energy_data_2023_ArothermPlus_XYZ.csv
# Wrote 2023 report to energy_data_2023_HydraulicStation_XYZ.csv
```

Writes a report for each heat generator, by default for the current year. You can provide `--year` to select
a different year.

## Using the API in Python

```python
#!/usr/bin/env python3

import argparse
import asyncio
import logging
from datetime import datetime, timedelta

from myVaillant.api import MyVaillantAPI
from myVaillant.const import ALL_COUNTRIES, BRANDS, DEFAULT_BRAND

parser = argparse.ArgumentParser(description="Export data from myVaillant API   .")
parser.add_argument("user", help="Username (email address) for the myVaillant app")
parser.add_argument("password", help="Password for the myVaillant app")
parser.add_argument(
    "brand",
    help="Brand your account is registered in, i.e. 'vaillant'",
    default=DEFAULT_BRAND,
    choices=BRANDS.keys(),
)
parser.add_argument(
    "--country",
    help="Country your account is registered in, i.e. 'germany'",
    choices=ALL_COUNTRIES.keys(),
    required=False,
)
parser.add_argument(
    "-v", "--verbose", help="increase output verbosity", action="store_true"
)


async def main(user, password, brand, country):
    async with MyVaillantAPI(user, password, brand, country) as api:
        async for system in api.get_systems():
            print(await api.set_set_back_temperature(system.zones[0], 18))
            print(await api.quick_veto_zone_temperature(system.zones[0], 21, 5))
            print(await api.cancel_quick_veto_zone_temperature(system.zones[0]))
            setpoint = 10.0 if system.control_identifier.is_vrc700 else None
            print(
                await api.set_holiday(
                    system,
                    datetime.now(system.timezone),
                    datetime.now(system.timezone) + timedelta(days=7),
                    setpoint,  # Setpoint is only required for VRC700 systems
                )
            )
            print(await api.cancel_holiday(system))
            if system.domestic_hot_water:
                print(await api.boost_domestic_hot_water(system.domestic_hot_water[0]))
                print(await api.cancel_hot_water_boost(system.domestic_hot_water[0]))
                print(
                    await api.set_domestic_hot_water_temperature(
                        system.domestic_hot_water[0], 46
                    )
                )


if __name__ == "__main__":
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(args.user, args.password, args.brand, args.country))

```

# Contributing

I'm happy to accept pull requests, if you run the pre-commit checks and test your changes:

## Supporting new Countries

The myVAILLANT app uses Keycloak and OIDC for authentication, with a realm for each country and brand.
There is a script to check which countries are supported:

```shell
python3 -m MyVaillant.tests.find_countries
```

Copy the resulting dictionary into src/MyVaillant/const.py

## Contributing Test Data

Because the myVAILLANT API isn't documented, you can help the development of this library by contributing test data:

```shell
python3 -m MyVaillant.tests.generate_test_data -h
python3 -m MyVaillant.tests.generate_test_data username password brand --country country
```

or use Docker:

```shell
docker run -v $(pwd)/test_data:/build/src/myvaillant/tests/json -ti ghcr.io/rmalbrecht/MyVaillant:latest python3 -m MyVaillant.tests.generate_test_data username password brand --country country
```

With docker, the results will be put into `test_data/`.

Please create a pull request with the created folder.

# Acknowledgements

* Auth is loosely based on [ioBroker.vaillant](https://github.com/TA2k/ioBroker.vaillant)
* Most API endpoints are reverse-engineered from the myVaillant app, using [mitmproxy](https://github.com/mitmproxy/mitmproxy)
