# Honeybee-ref:
### A Honeybee extension for tracking reference information and source data related to Honeybee-Objects.

Honeybee-Ref is a free plugin for [Ladybug Tools](https://www.ladybug.tools/) which enables users to add source and reference data such as URLs to Honeybee-Energy objects.

This plugin is designed as a plugin for Honeybee v1.8. It can also be utilized by the Ladybug toolkit for building up models within [Rhino 3D v8+](https://www.rhino3d.com/).


<details>
<summary><strong>Packages:</strong></summary>

- **honeybee_energy_ref:** Extend the Honeybee-Energy package with new 'ref' property slot.

</details>

<details>
<summary><strong>Installation:</strong></summary>

This package is [hosted on PyPi](https://pypi.org/project/honeybee-ref/). To install the latests version of the package:

```python
>>> pip install honeybee-ref
```
</details>

<details>
<summary><strong>Development:</strong></summary>

### Development [Local]:
honeybee-ref is free and open-source. We welcome any and all thoughts, opinions, and contributions! To get setup for local development:
1. **Fork** this GitHub repository to your own GitHub account.
1. **Clone** the new repository-fork onto your own computer.
![Screenshot 2024-10-01 at 3 48 51 PM](https://github.com/user-attachments/assets/6b7e0853-4b90-4b05-9344-8ced9ff04de9)
1. Setup a **virtual environment** on your own computer.
1. Install the required **dependencies**: `>>> pip install '.[dev]'`
1. *Recommended* Create a new **Branch** for all your changes.
1. Make the changes to the code.
1. Add tests to cover your new changes.
1. Submit a **Pull-Request** to merge your new Branch and its changes into the main branch.

### Development [Tests]:
Note that Honeybee-ref uses [`pytest`](https://docs.pytest.org/en/stable/#) to run all of the automated testing. Please be sure to include tests for any contributions or edits.

### Development [Deployment]:
This package is [published on PyPi](https://pypi.org/project/honeybee-ref/). To deploy a new version:
1. Update the [pyproject.toml version number](https://github.com/PH-Tools/honeybee_ref/blob/04039ea13f699cd81a76f036c44af628b9dba946/pyproject.toml#L3)
1. Publish a new release through the GitHub repository page:
![Screenshot 2024-09-26 at 10 05 14 AM](https://github.com/user-attachments/assets/8e831f39-03ee-4704-8a78-f3353960b3ea)
1. This is will trigger the [ci.yaml](https://github.com/PH-Tools/honeybee_ref/blob/main/.github/workflows/ci.yaml) GitHub Action, build, and deploy the package.
</details>

<details>
<summary><strong>More Information:</strong></summary>

For more information on the use of these tools, check out the the Passive House Tools website:
[https://www.PassiveHouseTools.com](https://www.PassiveHouseTools.com)

### Contact:
For questions about `honeybee-ref`, feel free to reach out at: PHTools@bldgtyp.com

You can also post questions or comment to the Ladybug-Tools use forum at: [https://discourse.ladybug.tools/](https://discourse.ladybug.tools/)
</details>

![Tests](https://github.com/PH-Tools/honeybee_ref/actions/workflows/ci.yaml/badge.svg)
