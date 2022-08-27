# Third Party Dependencies

<!--[[[fill sbom_sha256()]]]-->
The [SBOM in CycloneDX v1.4 JSON format](https://github.com/sthagen/pilli/blob/default/sbom.json) with SHA256 checksum ([0ca311db ...](https://raw.githubusercontent.com/sthagen/pilli/default/sbom.json.sha256 "sha256:0ca311db09fa9b1134f7f8402e1e669850e642ae938bd5d081cb73d407262bf9")).
<!--[[[end]]] (checksum: a49b13e122a2b30c801514ef62c0792c)-->
## Licenses 

JSON files with complete license info of: [direct dependencies](direct-dependency-licenses.json) | [all dependencies](all-dependency-licenses.json)

### Direct Dependencies

<!--[[[fill direct_dependencies_table()]]]-->
| Name                                                                          | Version                                                         | License                 | Author           | Description (from packaging data)                                                        |
|:------------------------------------------------------------------------------|:----------------------------------------------------------------|:------------------------|:-----------------|:-----------------------------------------------------------------------------------------|
| [atlassian-python-api](https://github.com/atlassian-api/atlassian-python-api) | [3.27.0](https://pypi.org/project/atlassian-python-api/3.27.0/) | Apache Software License | Matt Harasymczuk | Python Atlassian REST API Wrapper                                                        |
| [robotframework](https://robotframework.org/)                                 | [5.0.1](https://pypi.org/project/robotframework/5.0.1/)         | Apache Software License | Pekka Klärck     | Generic automation framework for acceptance testing and robotic process automation (RPA) |
| [wrapt](https://github.com/GrahamDumpleton/wrapt)                             | [1.14.1](https://pypi.org/project/wrapt/1.14.1/)                | BSD License             | Graham Dumpleton | Module for decorators, wrappers and monkey patching.                                     |
<!--[[[end]]] (checksum: 8f739e576a464fd7b4dcce887eff4066)-->

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
robotframework==5.0.1
````
<!--[[[end]]] (checksum: 455bbc1f74ac203859575b5141846234)-->
