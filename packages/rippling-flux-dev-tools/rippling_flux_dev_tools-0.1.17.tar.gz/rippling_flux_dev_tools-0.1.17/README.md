# rippling-flux-dev-tools

A Python package with modules useful for local Flux app development.

## Modules (flux_dev_tools)

The **distribution name** for this project is `rippling-flux-dev-tools`, which is how it is listed in PyPI. Once added
as a  dependency though, use the name `flux_dev_tools` as the **import name**.

### server.flask

This contains a `flask` module which exports a [Flask][flask] app that will make your `flux_apps/` code available to
[Rippling][rippling] servers for live debugging sessions.

The easiest way to use this is via the [Flask CLI][flask-cli], which is likely to have integration with your IDE. With
`rippling.flux-sdk` installed as a dependency, you can use `--app flux_sdk.server.flask`, which uses this  flask app as
the "app target".

```shell
python -m flask --app flux_dev_tools.server.flask run
```

[flask]: https://flask.palleprtsprojects.com/en/2.3.x/
[flask-cli]: https://flask.palletsprojects.com/en/2.3.x/cli/
[rippling]: https://www.rippling.com/