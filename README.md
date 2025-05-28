## What?

This repository contains multiple files, here is a overview:

File | Purpose | Documentation
-- | -- | --
`.devcontainer.json` | Used for development/testing with Visual Studio Code. | [Documentation](https://code.visualstudio.com/docs/remote/containers)
`.github/ISSUE_TEMPLATE/*.yml` | Templates for the issue tracker | [Documentation](https://help.github.com/en/github/building-a-strong-community/configuring-issue-templates-for-your-repository)
`custom_components/pulson_alarm/*` | Integration files, this is where everything happens. | [Documentation](https://developers.home-assistant.io/docs/creating_component_index)
`CONTRIBUTING.md` | Guidelines on how to contribute. | [Documentation](https://help.github.com/en/github/building-a-strong-community/setting-guidelines-for-repository-contributors)
`LICENSE` | The license file for the project. | [Documentation](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/licensing-a-repository)
`README.md` | The file you are reading now, should contain info about the integration, installation and configuration instructions. | [Documentation](https://help.github.com/en/github/writing-on-github/basic-writing-and-formatting-syntax)
`requirements.txt` | Python packages used for development/lint/testing this integration. | [Documentation](https://pip.pypa.io/en/stable/user_guide/#requirements-files)

## How?

1. Create a new repository in GitHub, using this repository as a template by clicking the "Use this template" button in the GitHub UI.
2. Open your new repository in Visual Studio Code devcontainer (Preferably with the "`Dev Containers: Clone Repository in Named Container Volume...`" option) (use `Dev Containers: Open Folder in Container...` if you want to use your local Windows path, not fully isolated WSL location).
3. Rename all instances of the `pulson_alarm` to `custom_components/<your_integration_domain>` (e.g. `custom_components/awesome_integration`).
4. Rename all instances of the `Pulson Alarm` to `<Your Integration Name>` (e.g. `Awesome Integration`).
5. Run the `scripts/develop` to start HA and test out your new integration.

## Debug
Tools for debugging are automatically installed
1. Start your system in docker.
2. The program will hang out on function debugpy.wait_for_client.
3. Go to tab Run & Debug in VSC.
4. Select "Attach to Home Assistant" configuration (if you added it earlier in .vscode/launch.json)
5. Click ▶️ Start debugging and now you are able to use breakpoints in your code

## Configure Frontend of panel
1. cd pulson_frontend
2. npm install
3. npm run dev
4. npm run build
5. cp -r dist/* ../custom_components/pulson_alarm/www/panel/
Instrunction 3rd allow to test site separated from HA (not sure if it's possible). The site is integrated with HA and may by tested as menu panel. You can skip 3rd step.

## Next steps

These are some next steps you may want to look into:
- Add tests to your integration, [`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component) can help you get started.
- Add brand images (logo/icon) to https://github.com/home-assistant/brands.
- Create your first release.
- Share your integration on the [Home Assistant Forum](https://community.home-assistant.io/).
- Submit your integration to [HACS](https://hacs.xyz/docs/publish/start).
