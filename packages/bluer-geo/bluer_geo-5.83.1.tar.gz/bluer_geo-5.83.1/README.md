# 🌐 bluer-geo (`@geo`)

🌐 AI for a Blue Planet.

```bash
pip install bluer-geo
```

```mermaid
graph LR
    catalog_browse["@catalog<br>browse<br>&lt;catalog-name&gt;<br>&lt;resource&gt;"]

    catalog_get["@catalog<br>get &lt;thing&gt;<br>--catalog &lt;catalog&gt;"]

    catalog_list_catalogs["@catalog<br>list catalogs"]

    catalog_list["@catalog<br>list collections|datacube_classes<br>--catalog &lt;catalog&gt;"]

    catalog_query["@catalog<br>query<br>&lt;catalog-name&gt;<br>&lt;collection-name&gt; -<br>&lt;query-object-name&gt;"]

    catalog_query_and_ingest["@catalog<br>query<br>&lt;catalog-name&gt;<br>&lt;collection-name&gt;<br>ingest,scope=&lt;scope&gt;<br>&lt;query-object-name&gt;"]

    catalog_query_read["@catalog<br>query<br>read -<br>&lt;query-object-name&gt;"]

    catalog_query_ingest["@catalog<br>query<br>ingest -<br>&lt;query-object-name&gt;<br>scope=&lt;scope&gt;"]

    datacube_crop["@datacube<br>crop -<br>&lt;object-name&gt;<br>&lt;datacube-id&gt;"]

    datacube_get["@datacube<br>get<br>catalog<br>&lt;datacube-id&gt;"]

    datacube_ingest["@datacube<br>ingest<br>scope=&lt;scope&gt;<br>&lt;datacube-id&gt;"]

    datacube_label["@datacube<br>label -<br>&lt;datacube-id&gt;"]

    datacube_list["@datacube<br>list<br>&lt;datacube-id&gt;<br>--scope &lt;scope&gt;"]

    geo_watch["@geo watch<br>batch<br>&lt;query-object-name&gt;|target=&lt;target&gt; -<br>to=&lt;runner&gt; - -<br>&lt;object-name&gt;"]

    catalog["🌐 catalog"]:::folder
    datacube_1["🧊 datacube"]:::folder
    datacube_2["🧊 datacube"]:::folder
    datacube_3["🧊 datacube"]:::folder
    terminal["💻 terminal"]:::folder
    QGIS["🖼️ QGIS"]:::folder
    query_object["📂 query object"]:::folder
    object["📂 object"]:::folder
    target["🎯 target"]:::folder

    catalog_list_catalogs --> terminal

    catalog --> catalog_browse
    catalog_browse --> terminal

    catalog --> catalog_get
    catalog_get --> terminal

    catalog --> catalog_list
    catalog_list --> terminal

    catalog --> catalog_query
    catalog_query --> query_object

    catalog --> catalog_query_and_ingest
    catalog_query_and_ingest --> query_object
    catalog_query_and_ingest --> datacube_1

    query_object --> catalog_query_read
    catalog_query_read --> datacube_1

    query_object --> catalog_query_ingest
    catalog_query_ingest --> datacube_1
    catalog_query_ingest --> datacube_2
    catalog_query_ingest --> datacube_3

    datacube_1 --> datacube_crop
    target --> datacube_crop
    datacube_crop --> datacube_1

    datacube_1 --> datacube_get
    datacube_get --> terminal

    datacube_1 --> datacube_ingest
    datacube_ingest --> datacube_1

    datacube_1 --> datacube_list
    datacube_list --> terminal

    datacube_1 --> datacube_label
    datacube_label --> QGIS
    datacube_label --> datacube_1

    query_object --> geo_watch
    target --> geo_watch
    geo_watch --> object

    classDef folder fill:#999,stroke:#333,stroke-width:2px;
```

|   |   |   |
| --- | --- | --- |
| [`Maxar Open Data`](./bluer_geo/catalog/maxar_open_data) [![image](https://github.com/kamangir/assets/blob/main/blue-geo/MaxarOpenData.png?raw=true)](./bluer_geo/catalog/maxar_open_data) catalog: [Maxar's Open Data program](https://www.maxar.com/open-data/) | [`copernicus`](./bluer_geo/catalog/copernicus) [![image](https://github.com/kamangir/assets/blob/main/blue-geo/copernicus.jpg?raw=true)](./bluer_geo/catalog/copernicus) catalog: [Copernicus Data Space Ecosystem - Europe's eyes on Earth](https://dataspace.copernicus.eu/) | [`firms-area`](./bluer_geo/catalog/firms) [![image](https://github.com/kamangir/assets/blob/main/blue-geo/datacube-firms_area.jpg?raw=true)](./bluer_geo/catalog/firms) catalog: Fire Information for Resource Management System ([FIRMS](https://firms.modaps.eosdis.nasa.gov)). |
| [`ukraine-timemap`](./bluer_geo/catalog/ukraine_timemap) [![image](https://github.com/kamangir/assets/blob/main/nbs/ukraine-timemap/QGIS.png?raw=true)](./bluer_geo/catalog/ukraine_timemap) catalog: [Bellingcat](https://www.bellingcat.com/) [Civilian Harm in Ukraine TimeMap](https://github.com/bellingcat/ukraine-timemap) dataset, available through [this UI](https://ukraine.bellingcat.com/) and [this API](https://bellingcat-embeds.ams3.cdn.digitaloceanspaces.com/production/ukr/timemap/api.json). | [`QGIS`](./bluer_geo/QGIS/README.md) [![image](https://github.com/kamangir/assets/blob/main/blue-geo/QGIS.jpg?raw=true)](./bluer_geo/QGIS/README.md) An AI terraform for [QGIS](https://www.qgis.org/). | [`global-power-plant-database`](./bluer_geo/objects/md/global_power_plant_database.md) [![image](https://github.com/kamangir/assets/blob/main/blue-geo/global_power_plant_database-cover.png?raw=true)](./bluer_geo/objects/md/global_power_plant_database.md) The Global Power Plant Database is a comprehensive, open source database of power plants around the world [datasets.wri.org](https://datasets.wri.org/datasets/global-power-plant-database). |
| [`geo-watch`](./bluer_geo/watch) [![image](https://github.com/kamangir/assets/blob/main/blue-geo/blue-geo-watch.png?raw=true)](./bluer_geo/watch) Watch the planet's story unfold. | [`catalog`](./bluer_geo/catalog) [![image](https://github.com/kamangir/assets/raw/main/blue-plugin/marquee.png?raw=true)](./bluer_geo/catalog) Generalized STAC Catalogs. | [`datacube`](./bluer_geo/datacube) [![image](https://github.com/kamangir/assets/raw/main/blue-plugin/marquee.png?raw=true)](./bluer_geo/datacube) Generalized STAC Items. |

---

> 🌀 [`blue-geo`](https://github.com/kamangir/blue-geo) for the [Global South](https://github.com/kamangir/bluer-south).


[![pylint](https://github.com/kamangir/bluer-geo/actions/workflows/pylint.yml/badge.svg)](https://github.com/kamangir/bluer-geo/actions/workflows/pylint.yml) [![pytest](https://github.com/kamangir/bluer-geo/actions/workflows/pytest.yml/badge.svg)](https://github.com/kamangir/bluer-geo/actions/workflows/pytest.yml) [![bashtest](https://github.com/kamangir/bluer-geo/actions/workflows/bashtest.yml/badge.svg)](https://github.com/kamangir/bluer-geo/actions/workflows/bashtest.yml) [![PyPI version](https://img.shields.io/pypi/v/bluer-geo.svg)](https://pypi.org/project/bluer-geo/) [![PyPI - Downloads](https://img.shields.io/pypi/dd/bluer-geo)](https://pypistats.org/packages/bluer-geo)

built by 🌀 [`bluer README`](https://github.com/kamangir/bluer-objects/tree/main/bluer_objects/README), based on 🌐 [`bluer_geo-5.83.1`](https://github.com/kamangir/bluer-geo).
