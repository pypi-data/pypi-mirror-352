# Connector Development Kit (CDK)

<!-- TOC -->

- [Warnings](#warnings)
- [CDK Development](#cdk-development)
  - [TL;DR](#tldr)
  - [Python](#python)
  - [Virtual Environment](#virtual-environment)
  - [Project Dependencies](#project-dependencies)
  - [Docker Compose](#docker-compose)
  - [Tests](#tests)
  - [Release](#release)
- [Connector Development](#connector-development)
  - [Execution Environment](#execution-environment)
  - [Conventions](#conventions)
  - [Connectors Factory](#connectors-factory)
  - [Configuration](#configuration)
    - [Tinybird](#tinybird)
    - [Pass-Through Driver Environment Variables](#pass-through-driver-environment-variables)
    - [Method Arguments are not Configuration](#method-arguments-are-not-configuration)
    - [Accessing Configuration](#accessing-configuration)
  - [Logging](#logging)
  - [Connectors are Context Managers](#connectors-are-context-managers)
  - [Tinybird Client](#tinybird-client)
  - [Executing Queries from Ingestion Scripts](#executing-queries-from-ingestion-scripts)
    - [Executing Queries against Tinybird](#executing-queries-against-tinybird)
    - [Executing Queries against Databases](#executing-queries-against-databases)
  - [Cloud Storage Clients](#cloud-storage-clients)
  - [Formats](#formats)
  - [Connector Types](#connector-types)
    - [Common API for All Connectors](#common-api-for-all-connectors)
    - [SQL Databases](#sql-databases)
      - [Scopes](#scopes)
      - [Querying the Original Database](#querying-the-original-database)
      - [Exports](#exports)
      - [Utilities](#utilities)
      - [Model SQL Connector](#model-sql-connector)
    - [Cloud Storage Services](#cloud-storage-services)
    - [Streaming Sources](#streaming-sources)
  - [Support for GitHub Actions](#support-for-github-actions)
    - [Cloning](#cloning)
    - [The `setup` Action](#the-setup-action)
    - [The `query_tb` Action](#the-query_tb-action)
    - [The `query_db` Action](#the-query_db-action)
    - [The `replace` Action](#the-replace-action)
  - [Testing](#testing)
    - [Test Data](#test-data)
    - [BigQuery](#bigquery)
    - [Snowflake](#snowflake)

<!-- /TOC -->

<a id="markdown-warnings" name="warnings"></a>
## Warnings

* **The CDK is in active development and things will change.**

* **By now, we keep everything in one repo to be able to evolve the CDK, the
  connectors, docs, and tests as needed in self-contained patches.**

<a id="markdown-cdk-development" name="cdk-development"></a>
## CDK Development

<a id="markdown-tldr" name="tldr"></a>
### TL;DR

Everything is detailed later, but this is the gist of it:

1. Install Python >= 3.11
1. Install Docker Compose
1. Setup and activate a virtual environment
1. Set the environment variable `TB_CDK_TEST_SUITE_TOKEN` (ask for its value)
1. Run `pip install -e .["dev"]`
1. Run `bin/test`

You should see the test suite passing.

<a id="markdown-python" name="python"></a>
### Python

The CDK is tested with Python 3.11 to match Analytics.

However, the CDK uses pretty standard Python, nothing fancy. Upgrading when
Analytics does should be routine.

<a id="markdown-virtual-environment" name="virtual-environment"></a>
### Virtual Environment

Once Python is installed, create a virtual environment by running

```
% python3 -m venv .venv
% source .venv/bin/activate
```

in the project root directory.

Run `deactivate` to deactivate the virtual environment.

<a id="markdown-project-dependencies" name="project-dependencies"></a>
### Project Dependencies

In order to install project dependencies execute

```
% pip install -r requirements.txt -r requirements-dev.txt
```

in the project root directory.

<a id="markdown-docker-compose" name="docker-compose"></a>
### Docker Compose

The test suite uses some services provided by Docker Compose. You don't need to
worry about launching them manually, `bin/test` does it for you if needed.

<a id="markdown-tests" name="tests"></a>
### Tests

The test suite requires the environment variable `TB_CDK_TEST_SUITE_TOKEN` to be
set to the `CDK_TEST_SUITE` token defined in the `cdk_test_suite` workspace in
production. It also requires the `TB_CDK_TEST_SUITE_TB_WORKSPACE_ID` variable with
that workspace id.

To run the tests of the core of the CDK, just execute:

```
bin/test
```

These are located under `tests/core` and provide coverage for the CDK itself.

There are separate tests for connectors under `tests/connectors`. These are not
run by `bin/test` unless you pass them as arguments. For instance:

```
bin/test tests/connectors/sql/snowflake
```

However, you need more environment setup to run these ones. Please check the
details down below.

Arguments to `bin/test` are passed down. For example, to get standard output echoed pass `-s` as additional argument:

```
% bin/test -s
```

To execute the tests in one particular file:

```
% bin/test tests/core/test_config.py
```

To execute the tests in one particular class:

```
% bin/test -k TestExportLocalFile
```

To execute one particular test:

```
% bin/test -k test_append_url
```

You can also pass multiple options as in

```
% bin/test -s -k TestCloudS3
```

<a id="markdown-release" name="release"></a>
### Release

To release a new version, you'll need to bump the version number by running

```
% bumpversion patch # or minor, or major
```

This will update the version number in `pyproject.toml`, `tinybird_cdk/__init__.py` and `.bumpversion.cfg`, and create a new commit.  
Then, push the changes to the repository.

When the PR is merged to `main`, the CI will run release steps:
* A new tag will be created by the CI.
* The CI will build the package and upload it to PyPI.
* A docker image will be built and pushed to the registry with two tags: `vX.Y.Z` and `vX.Y`.

<a id="markdown-connector-development" name="connector-development"></a>
## Connector Development

<a id="markdown-execution-environment" name="execution-environment"></a>
### Execution Environment

Connectors should be able to run in client infraestructure and therefore can
only speak with Tinybird using the public API.

<a id="markdown-conventions" name="conventions"></a>
### Conventions

* The connector for `Foo` should be implemented in the module `tinybird_cdk/connectors/foo.py`
* That module should define a class `Connector`.
* The `Connector` class has to inherit from one of the base classes defined in
  the `tinybird_cdk.connector` module: `SQLConnector`, `CloudConnector`, or
  `StreamingConnector`. More about them later.
* The constructor of `Connector` has to receive no arguments. Configuration goes
  via the environment always. See next section.

The [existing
connectors](https://github.com/tinybirdco/cdk/tree/main/tinybird_cdk/connectors)
may serve as a model.

<a id="markdown-connectors-factory" name="connectors-factory"></a>
### Connectors Factory

Scripts using concrete connectors may import them directly:

```python
from tinybird_cdk.connectors import snowflake

with snowflake.Connector() as connector:
    ...
```

However, the factory `tinybird_cdk.connector_for()` leverages the conventions
explained above to ease dynamic instantiation:

```python
import tinybird_cdk

with tinybird_cdk.connector_for('snowflake') as connector:
    ...
```

If the name is unknown, `tinybird_cdk.errors.UnknownConnectorError` is raised.

<a id="markdown-configuration" name="configuration"></a>
### Configuration

<a id="markdown-tinybird" name="tinybird"></a>
#### Tinybird

All connectors understand these environment variables:

* `TB_CDK_TOKEN`: Required. The token of the user.
* `TB_CDK_TAG`: Required. An arbitrary string that identifies the running
  script. Helpful to identify who is logging what in aggregated logs.
* `TB_CDK_ENDPOINT`: Optional. The endpoint used to perform API calls. Defaults to
  `https://api.tinybird.co`.

<a id="markdown-pass-through-driver-environment-variables" name="pass-through-driver-environment-variables"></a>
#### Pass-Through Driver Environment Variables

Connectors should be configured using environment variables only.

If the library to access the original data already understands environment
  variables, link to their documentation. For example, PostgreSQL supports
[these ones](https://www.postgresql.org/docs/9.3/libpq-envars.html). Instead of
duplicating them all in method or script arguments, just document that the
connector supports the same environment variables PostgreSQL supports, and link
to them.

Then, instantiate the driver passing no parameters:

```python
with psycopg2.connect().cursor() as cursor:
    ...
```

<a id="markdown-method-arguments-are-not-configuration" name="method-arguments-are-not-configuration"></a>
#### Method Arguments are not Configuration

Consider this ingestion script:

```python
from tinybird_cdk import formats
from tinybird_cdk.connectors import snowflake

with snowflake.Connector() as connector:
    connector.replace(
        query='SELECT date, event, extra_data, product_id, user_id FROM test.events',
        data_source='ndjson_events',
        fmt=formats.NDJSON
    )
```

The constructor of the connector does not receive arguments. As explained above,
configuration is assumed to be available via its documented environment
variables.

However, the connector should not ask users to pass the replace query, target
data source, or format via environment variables, they are expected as method
arguments and may vary in between calls.

Ingestion scripts are responsible for these values, they may be hard-coded, read
from a configuration file, or from their process environment. No matter their
origin, the ingestion script has to pass them as regular method arguments.

<a id="markdown-accessing-configuration" name="accessing-configuration"></a>
#### Accessing Configuration

While configuration should go via environment variables, connectors should not
fetch them with `os.getenv()` directly. The module `tinybird_cdk.config`
provides a thin abstraction over them:

Usage:

```python
# Returns os.getenv('FOO'). Raises `tinybird_cdk.errors.MissingConfiguration` if unset.
config.get('FOO')

# Returns os.getenv('FOO'). Returns None if unset.
config.get('FOO', optional=True)

# Returns os.getenv('FOO'). Returns 'foo' if unset.
config.get('FOO', default='foo')
```

<a id="markdown-logging" name="logging"></a>
### Logging

The CDK provides standardarized logging by means of the `tinybird_cdk.logger`
module.

Usage:

```python
logger.debug(...)
logger.info(...)
logger.warning(...)
logger.error(...)
```

These methods print to standard output.

<a id="markdown-connectors-are-context-managers" name="connectors-are-context-managers"></a>
### Connectors are Context Managers

All connectors are context managers and their documentation should reflect this:

```python
from tinybird_cdk.connectors import mysql

with mysql.Connector() as connector:
    ...
```

Thanks to this, if an exception aborts a script, the CDK still has a chance to
log it.

Connectors only throw exceptions of type `tinybird_cdk.errors.Error` or a
subclass of it. Exceptions that are not thrown by the CDK itself, say,  are
wrapped in a `tinybird_cdk.errors.Error` exception, whose `__cause__` is the
original one.

<a id="markdown-tinybird-client" name="tinybird-client"></a>
### Tinybird Client

All connectors have a Tinybird client at `self.tb`:

```python
self.tb.append_data(...)
self.tb.append_file(...)
self.tb.append_url(...)

self.tb.replace_data(...)
self.tb.replace_file(...)
self.tb.replace_url(...)

self.tb.append_event(...)
self.tb.append_events(...)

self.tb.query(...)
```

Please, have a look at the [source code](src/tinybird_cdk/tinybird.py) for details.

Remarks:

* For now, these methods return HTTPX response objects directly.
  ([docs](https://www.python-httpx.org/quickstart/)).
* When importing URLs, the client waits for jobs to complete. If a job fails,
  `tinybird_cdk.errors.JobError` is raised.
* The client retries on 429s and understands the `Retry-After` HTTP header sent
  by Tinybird. This way, the CDK handles rate limiting on behalf of the user.
* The client retries on 408s at most 5 times with exponential backoff. Raises
  `tinybird_cdk.errors.HTTPError` if retries are exhausted. This helps dealing
  with occasional request timeouts.
* The client retries on 502s for `GET` and `HEAD` requests. This happens when
  the communication between NGINX and Analytics has a hiccup.
* The client raises `tinybird_cdk.errors.HTTPError` for any other HTTP status
  code.

For now, the Tinybird client is synchronous. The CDK design emulates `tb` usage
in this regard. If you want to parallelize ingesting from several sources,
please do so launching as many scripts with your shell, cron scheduler, etc.

<a id="markdown-executing-queries-from-ingestion-scripts" name="executing-queries-from-ingestion-scripts"></a>
### Executing Queries from Ingestion Scripts

<a id="markdown-executing-queries-against-tinybird" name="executing-queries-against-tinybird"></a>
#### Executing Queries against Tinybird

The `tb` attribute is private. All connectors have a `query_tb()` method so that
end-users are able to query Tinybird:

```python
from tinybird_cdk.connectors import mysql

with mysql.Connector() as connector:
    max_date = connector.query_tb('SELECT MAX(date) FROM products', scalar=True)
    connector.append(f"SELECT * FROM products WHERE date > '{max_date}'", 'products')
```

The `query_tb()` method returns the Python structure that corresponds to the
JSON response sent by Tinybird. By passing `scalar: True` you get the first
value of the first dictionary, `None` if the result set was empty.

<a id="markdown-executing-queries-against-databases" name="executing-queries-against-databases"></a>
#### Executing Queries against Databases

SQL connectors have a `query_db()` method, so that end-users are able to query
the original database.

`query_db()` is designed to easily fetch values that may help in subsequent
operations. Therefore, it returns entire result sets as a list of dictionaries.
The method supports also the optional flag `scalar`, which behaves like the one
in `query_tb()`, explained above.

<a id="markdown-cloud-storage-clients" name="cloud-storage-clients"></a>
### Cloud Storage Clients

The CDK provides cloud storage clients for AWS and GCS with a standardized API:

```python
from tinybird_cdk.cloud import s3

client = s3.Client()

# Common interface.
client.uri(...)
client.ls(...)
client.public_url(...)
client.rm(...)
client.rmtree(...)
client.cat(...)
```

Please, have a look at the [source code](tinybird_cdk/cloud) for details.

<a id="markdown-formats" name="formats"></a>
### Formats

The module `tinybird_cdk.formats` provides constants for formats:

```python
formats.CSV
formats.NDJSON
formats.PARQUET
```

Connectors should never work with Tinybird formats as string literals, please
pass and compare Tinybird formats using always those constants.

When exporting to CSV, connectors are required to configure the generation so
that it conforms to [RFC 4180](https://www.rfc-editor.org/rfc/rfc4180) except
for the record delimiter, which must be the conventional Unix newline character
(`\n` in Python, ASCII code 10).

In particular, fields that contain field or record delimiters have to be quoted
using double quotes. Within quoted fields, double quotes are escaped by putting
them twice, as in `" a "" b"`. Backslashes have no special meaning.

The CDK passes `dialect_delimiter`, `dialect_new_line` in API calls accordingly,
and sets no `dialect_escapechar`.

<a id="markdown-connector-types" name="connector-types"></a>
### Connector Types

<a id="markdown-common-api-for-all-connectors" name="common-api-for-all-connectors"></a>
#### Common API for All Connectors

All connectors are context managers, and inherit the `query_tb()` method,
covered above.

<a id="markdown-sql-databases" name="sql-databases"></a>
#### SQL Databases

Connectors of SQL databases have to inherit from
`tinybird_cdk.connector.SQLConnector` and implement its abstract interface.

<a id="markdown-scopes" name="scopes"></a>
##### Scopes

SQL connectors provide a generic interface for Analytics to be able to list the
scopes that narrow choices down to a table: `get_scopes()` and `list_scope()`.

<a id="markdown-querying-the-original-database" name="querying-the-original-database"></a>
##### Querying the Original Database

SQL connectors have to implement a `_query()` method that executes a query
against the original database.

The method must return a list of dictionaries with the result set. This is meant
to be used for cheap queries like fetching one or two values that help continue
an incremental replace with condition, for example.

The public interface for this method is the inherited `query_db()`, which
calls it internally.

<a id="markdown-exports" name="exports"></a>
##### Exports

SQL connectors have to implement a `_export()` method which has to export a
query using the given format, and return an [export
object](https://github.com/tinybirdco/cdk/blob/main/tinybird_cdk/export.py). If
the format is not supported, the method should raise
`tinybird_cdk.errors.UnsupportedFormatError`.

Local or cloud files used to export are deleted by the CDK automatically once
the import has been completed, either successfully or unsuccessfully.

The public interface for `_export()` are the inhetited methods `append()` and
`replace()`, which call it internally.

<a id="markdown-utilities" name="utilities"></a>
##### Utilities

SQL connectors also inherit some utilities like `_random_dirname()`,
`_text_tempfile()`, etc.

<a id="markdown-model-sql-connector" name="model-sql-connector"></a>
##### Model SQL Connector

Please, have a look at the source code of the [BigQuery
connector](https://github.com/tinybirdco/cdk/blob/main/tinybird_cdk/connectors/bigquery.py)
as a model.

<a id="markdown-cloud-storage-services" name="cloud-storage-services"></a>
#### Cloud Storage Services

Connectors for cloud storage services have to inherit from `tinybird_cdk.connector.CloudConnector` and instantiate the corresponding standardized cloud client in `__init__()`.

Their inherited public API is:

```python
connector.append(...)
connector.replace(...)
```

<a id="markdown-streaming-sources" name="streaming-sources"></a>
#### Streaming Sources

Streaming connectors inherit from `tinybird_cdk.connector.StreamingConnector`
and implement a `stream()` method. That typically entails some sort of infinite
loop:

```ruby
class Connector(connector.StreamingConnector):
    def stream(self, stream_name, data_source):
        for message in read(stream_name=stream_name):
            self.tb.append_event(message, data_source=data_source)
```

That is only an example to get the idea, you may want to buffer messages. In any
case, `self.tb.append_event()` and `self.tb.append_events()` is your interface
to speak to HFI.

<a id="markdown-support-for-github-actions" name="support-for-github-actions"></a>
### Support for GitHub Actions

The project directory `ext/github/actions` has actions which are useful for
projects doing ingestion via GitHub Actions.

<a id="markdown-cloning" name="cloning"></a>
#### Cloning

Parent projects need to clone this repository under `$GITHUB_WORKSPACE/cdk`. For
example:

```yaml
steps:
  - uses: actions/checkout@v3
    with:
      repository: 'tinybirdco/cdk'
      ssh-key: ${{ secrets.CDK_DEPLOY_KEY }}
      path: 'cdk'
```

The CDK has defined a deploy key that you need to find out.

<a id="markdown-the-setup-action" name="the-setup-action"></a>
#### The `setup` Action

The `setup` action installs Python and project dependencies. The purpose of this
action is to encapsulate what setting up the CDK entails. Requires the parent
project to clone the repository in `$GITHUB_WORKSPACE/cdk`, as shown in the
previous section.

Usage from a parent project could be something like:

```yaml
steps:
  - uses: ./cdk/ext/github/actions/setup
```

<a id="markdown-the-query_tb-action" name="the-query_tb-action"></a>
#### The `query_tb` Action

This action provides a way to query Tinybird:

```yaml
- id: count-as-json
  uses: ./cdk/ext/github/actions/query_tb
  with:
    sql: SELECT COUNT(*) AS c, MAX(n) AS m FROM numbers
```

The result set is stored in the `result` output. Since the ID of the step above
is `count-as-json`, said output is available as

```
${{ steps.count-as-json.outputs.result }}
```

You can access different elements of the result set with
[`fromJSON`](https://docs.github.com/en/actions/learn-github-actions/expressions#fromjson)
and
[operators](https://docs.github.com/en/actions/learn-github-actions/expressions#operators).
For example:

```yaml
${{ fromJSON(steps.count-as-json.outputs.result)[0].m }}
```

yields the `m` property of the first object in the parsed array. That is, `MAX(n)`.

Often, queries are issued to retrieve one single value, the `scalar` flag allows
you to get it directly:

```yaml
- id: count-value
  uses: ./cdk/ext/github/actions/query_tb
  with:
    sql: SELECT COUNT(*) AS c FROM numbers
    scalar: true
- run: |
    test ${{ steps.count-value.outputs.result }} -eq 10
```

As shown in the example above, the value is stored in the `result` output. Since
the ID of the step above is `count-value`, said output is available as

```
${{ steps.count-value.outputs.result }}
```

There is no need to use `fromJSON` in this case, since you have the scalar right
there. String values do not have surrounding quotes.

Empty result sets return `null`.

<a id="markdown-the-query_db-action" name="the-query_db-action"></a>
#### The `query_db` Action

This action provides a way to query SQL connectors' databases:

```yaml
- id: count-as-json
  uses: ./cdk/ext/github/actions/sql/query_db
  with:
    connector: snowflake
    sql: SELECT COUNT(*) AS c, MAX(n) AS m FROM numbers
```

The result set is stored in the `result` output. Since the ID of the step above
is `count-as-json`, said output is available as

```
${{ steps.count-as-json.outputs.result }}
```

You can access different elements of the result set with
[`fromJSON`](https://docs.github.com/en/actions/learn-github-actions/expressions#fromjson)
and
[operators](https://docs.github.com/en/actions/learn-github-actions/expressions#operators).
For example:

```yaml
${{ fromJSON(steps.count-as-json.outputs.result)[0].m }}
```

yields the `m` property of the first object in the parsed array. That is, `MAX(n)`.

Often, queries are issued to retrieve one single value, the `scalar` flag allows
you to get it directly:

This action provides a way to query the connector's database for one value:

```yaml
- id: ncountries
  uses: ./cdk/ext/github/actions/sql/query_db
  with:
    connector: snowflake
    sql: SELECT COUNT(*) AS c FROM countries
    scalar: true
- run: echo ${{ steps.ncountries.outputs.result }}
```

As shown in the example above, the value is stored in the `result` output. Since
the ID of the step above is `ncountries`, said output is available as

```
${{ steps.ncountries.outputs.result }}
```

There is no need to use `fromJSON` in this case, since you have the scalar right
there. String values do not have surrounding quotes.

Empty result sets return `null`.

<a id="markdown-the-replace-action" name="the-replace-action"></a>
#### The `replace` Action

The CDK has a generic `replace` action that works with any SQL connector.

Usage from a parent project looks like:

```yaml
steps:
  - uses: ./cdk/ext/github/actions/sql/replace
    with:
      connector: snowflake
      data_source: ${{ inputs.data_source }}
      query: ${{ inputs.query }}
      format: csv
      replace_condition: ${{ inputs.replace_condition }}
```

<a id="markdown-testing" name="testing"></a>
### Testing

To execute the test suite of a connector, you need to pass the file name as an
argument to `bin/test`:

```
bin/test tests/connectors/sql/bigquery
```

Each connectors has their own data sources in Tinybird. The pattern is:

* `bigquery_export_csv`: A CSV data source with columns for the data types
  supported in Tinybird. Used to verify that `export` does what it is supposed
  to do, assuming the query is correct.
* `bigquery_export_ndjson`: Same for NDJSON.
* `bigquery_ingest_query`: A data source with as many columns as BigQuery data
  types are supported. The ClickHouse types of the columns must be the ones the
  connector map them to.

The first two data sources are the same one for each SQL connector, but they
have their own prefix to allow CI to run connector test suites in parallel.

The third data source depends on the connector.

These data source are generated by the scripts in
[`tests/scripts`](tests/scripts) and you can take the ones for BigQuery as a
model. Permission have to be granted for newly generated data sources.

Similarly, have a look at the [test suite of the BigQuery
connector](tests/connectors/sql/bigquery) for a model.

<a id="markdown-test-data" name="test-data"></a>
#### Test Data

The helper module [`tests/helpers/data.py`](tests/helpers/data.py) has functions to generate random
values of different kinds. Notably, `text()` generates strings with newlines and
no single quotes, so they can be interpolated in SQL.

<a id="markdown-bigquery" name="bigquery"></a>
#### BigQuery

In order to be able to run the test suite of the BigQuery connector, you need the environment variable

* `TB_CDK_TEST_SUITE_GOOGLE_APPLICATION_CREDENTIALS`

set to the path of the file with the credentials of the service account used by
the CDK test suite. Please ask around for it.

<a id="markdown-snowflake" name="snowflake"></a>
#### Snowflake

In order to be able to run the test suite of the Snowflake connector, you need
the following environment variables set:

* `TB_CDK_TEST_SUITE_SF_ACCOUNT`
* `TB_CDK_TEST_SUITE_SF_USER`
* `TB_CDK_TEST_SUITE_SF_PWD`
* `TB_CDK_TEST_SUITE_SF_WAREHOUSE`
* `TB_CDK_TEST_SUITE_SF_DATABASE`
* `TB_CDK_TEST_SUITE_SF_SCHEMA`
* `TB_CDK_TEST_SUITE_SF_STAGE`
* `TB_CDK_TEST_SUITE_SF_ROLE`
* `TB_CDK_TEST_SUITE_SF_GOOGLE_APPLICATION_CREDENTIALS`
* `TB_CDK_TEST_SUITE_TB_WORKSPACE_ID`
