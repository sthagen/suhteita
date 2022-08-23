# Third Party Dependencies

<!--[[[fill sbom_sha256()]]]-->
The [SBOM in CycloneDX v1.4 JSON format](https://github.com/sthagen/pilli/blob/default/sbom.json) with SHA256 checksum ([d479052d ...](https://raw.githubusercontent.com/sthagen/pilli/default/sbom.json.sha256 "sha256:d479052d2404d75da15c96896d115c27837a8206a3d206bce48d2b2f1cf4f3ee")).
<!--[[[end]]] (checksum: 78f2bced6ebeaeb11ff1f436bceeb6b7)-->
## Licenses 

JSON files with complete license info of: [direct dependencies](direct-dependency-licenses.json) | [all dependencies](all-dependency-licenses.json)

### Direct Dependencies

<!--[[[fill direct_dependencies_table()]]]-->
| Name                                                                          | Version                                                         | License                 | Author           | Description (from packaging data) |
|:------------------------------------------------------------------------------|:----------------------------------------------------------------|:------------------------|:-----------------|:----------------------------------|
| [atlassian-python-api](https://github.com/atlassian-api/atlassian-python-api) | [3.27.0](https://pypi.org/project/atlassian-python-api/3.27.0/) | Apache Software License | Matt Harasymczuk | Python Atlassian REST API Wrapper |
<!--[[[end]]] (checksum: dbdc0d190500d5e5e9dae02bea8382de)-->

### Indirect Dependencies

<!--[[[fill indirect_dependencies_table()]]]-->
| Name                                          | Version                                        | License     | Author         | Description (from packaging data)         |
|:----------------------------------------------|:-----------------------------------------------|:------------|:---------------|:------------------------------------------|
| [click](https://palletsprojects.com/p/click/) | [8.1.3](https://pypi.org/project/click/8.1.3/) | BSD License | Armin Ronacher | Composable command line interface toolkit |
<!--[[[end]]] (checksum: dc3a866a7aa3332404bde3da87727cb9)-->

## Dependency Tree(s)

JSON file with the complete package dependency tree info of: [the full dependency tree](package-dependency-tree.json)

### Rendered SVG

Base graphviz file in dot format: [Trees of the direct dependencies](package-dependency-tree.dot.txt)

<img src="https://raw.githubusercontent.com/sthagen/pilli/default/docs/third-party/package-dependency-tree.svg" alt="Trees of the direct dependencies" title="Trees of the direct dependencies"/>

### Console Representation

<!--[[[fill dependency_tree_console_text()]]]-->
````console
atlassian-python-api==3.27.0
  - deprecated [required: Any, installed: 1.2.13]
    - wrapt [required: >=1.10,<2, installed: 1.14.1]
  - oauthlib [required: Any, installed: 3.2.0]
  - requests [required: Any, installed: 2.28.1]
    - certifi [required: >=2017.4.17, installed: 2022.6.15]
    - charset-normalizer [required: >=2,<3, installed: 2.1.0]
    - idna [required: >=2.5,<4, installed: 3.3]
    - urllib3 [required: >=1.21.1,<1.27, installed: 1.26.11]
  - requests-oauthlib [required: Any, installed: 1.3.1]
    - oauthlib [required: >=3.0.0, installed: 3.2.0]
    - requests [required: >=2.0.0, installed: 2.28.1]
      - certifi [required: >=2017.4.17, installed: 2022.6.15]
      - charset-normalizer [required: >=2,<3, installed: 2.1.0]
      - idna [required: >=2.5,<4, installed: 3.3]
      - urllib3 [required: >=1.21.1,<1.27, installed: 1.26.11]
  - six [required: Any, installed: 1.16.0]
````
<!--[[[end]]] (checksum: 3de0f59ffe6dde9798a66c75113c6882)-->
