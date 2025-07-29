# Kafka Geo-Replication Demo Orchestrator

## Project Overview

This project provides a Python library and command-line interface (CLI) tool to deploy and orchestrate geo-replicated
Apache Kafka clusters using Apache MirrorMaker 2.

The project is composed of two modules:

- **core**: Exposes Python API to execute operations
- **cli**: Command line interface for core

The goal is to simulate a multi-region or multi-cloud environment in a simplified manner and to demonstrate how data can
be reliably replicated for High Availability (HA), Disaster Recovery (DR), and data
centralization scenarios.

The inspiration for this project comes from a user request to
Aiven [discussing stretched clusters](https://ideas.aiven.io/forums/951277-event-streaming/suggestions/46266718-support-for-stretched-cluster-across-multi-regio) -
highlighting the growing need for resilient and distributed data architectures where data must be accessible and
protected across different failure domains.

This tool aims to demonstrate not only the functionality of Kafka and MirrorMaker 2 but also how automation can simplify
the deployment and management of such configurations—a key concept for companies providing abstraction layers over
complex cloud services.

## Problem Solved / Use Case

In real-world scenarios, companies might need to:

* Maintain a copy of their Kafka data in a separate geographical region for Disaster Recovery.
* Migrate data from an on-premise Kafka cluster to a cloud cluster (or vice-versa, or between different
  clouds).
* Aggregate data from multiple Kafka clusters (e.g., from microservices) into a central cluster for
  analytics or
  monitoring.
* Ensure high availability of critical event streams.

This tool allows for simulating and demonstrating how MirrorMaker 2 addresses these needs.

## Tool Features

* [ ] **Automated Kafka Cluster Deployment:** Spins up two distinct Kafka clusters ("primary" and "secondary") locally
  using
  Docker Compose, simulating separate environments.
* [ ] **MirrorMaker 2 Configuration and Startup:** Dynamically generates the configuration for MirrorMaker 2 and starts
  it
  to replicate data from the primary to the secondary cluster.
* [ ] **Integrated Event Producer:** Allows for easily sending sample messages to the primary cluster to populate
  topics.
* [ ] **Integrated Event Consumer:** Allows for reading messages from the secondary cluster to verify successful
  replication.
* [ ] **Simplified Management:** CLI commands to start the entire stack, produce/consume messages, and clean up
  resources.

## Technologies Used

* **Python 3.x**
* **Apache Kafka** (running in Docker containers)
* **Apache MirrorMaker 2** (running in a Docker container)
* **Docker & Docker Compose**
* Python Libraries:
    * `click` for the CLI interface
    * `python-kafka` for interacting with Kafka (chosen over `confluent-kafka-python` as this project is intended for
      testing and demonstration purposes only, not for production use where direct Kafka interaction is critical)

## Prerequisites

Before you begin, ensure you have installed:

* Python 3.8+
* Docker
* Docker Compose

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dmgiangi/kafka-mirror-kit.git
   cd kafka-mirror-kit
   ```
2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Python dependencies:**
   ```bash
   pip install -e .  # Install in development mode
   # or
   pip install .     # Regular installation
   ```

## Continuous Integration

This project uses GitHub Actions for continuous integration. When a pull request is made to the `main` branch, the
workflow automatically runs all tests to ensure code quality.

### Workflow Details

The workflow performs the following steps:

1. Sets up a Python 3.8 environment
2. Installs all dependencies from pyproject.toml
3. Runs all tests using pytest

You can view the workflow configuration in `.github/workflows/tests.yml`.

## Release Process

This project uses [Google's release-please-action](https://github.com/google-github-actions/release-please-action) to
automate the release process. Release-please creates release PRs when changes are pushed to the main branch, and
automatically updates version numbers and generates changelogs based on conventional commit messages.

### How It Works

1. When commits are pushed to the `main` branch, the release-please action analyzes the commit messages.
2. If there are new features, bug fixes, or other notable changes, release-please creates or updates a release PR.
3. The release PR updates the version in `pyproject.toml`, updates the changelog, and makes any other necessary
   version-related changes.
4. When the release PR is merged, release-please automatically creates a GitHub release with the appropriate tag.

### Commit Message Format

To properly trigger version bumps, commit messages should follow
the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat: add new feature` - Triggers a minor version bump (0.1.0 -> 0.2.0)
- `fix: resolve bug` - Triggers a patch version bump (0.1.0 -> 0.1.1)
- `docs: update documentation` - Included in changelog but doesn't bump version
- `refactor: improve code structure` - Included in changelog but doesn't bump version
- `perf: improve performance` - Included in changelog but doesn't bump version
- `chore: update dependencies` - Not included in changelog
- `test: add tests` - Not included in changelog
- `ci: update CI configuration` - Not included in changelog
- `build: update build process` - Not included in changelog

For breaking changes, add `BREAKING CHANGE:` in the commit message body or append `!` after the type:

```
feat!: add new feature with breaking changes

BREAKING CHANGE: This feature breaks backward compatibility
```

This will trigger a major version bump (1.0.0 -> 2.0.0).

You can view the release workflow configuration in `.github/workflows/release-please.yml`.

## Usage

The tool provides a simple command-line interface. After installing the package with `pip install -e .`, you can use the
`kmk` command directly:

1. **Deploy the infrastructure (Kafka Clusters + MirrorMaker 2):**
   ```bash
   kmk deploy
   ```
   This command will start the Docker containers for the two Kafka clusters and a MirrorMaker 2 instance configured to
   replicate all topics (or specific topics if configured) from the `primary` cluster to the `secondary` cluster.
   Replicated topics on the `secondary` cluster will typically have a prefix (e.g., `primary.topic_name`).

2. **Produce messages to the primary cluster:**
   ```bash
   kmk produce --topic my_topic --messages 10
   ```
   This will send 10 sample messages to the `my_topic` topic on the `primary` cluster.

3. **Consume messages from the secondary cluster (for verification):**
   ```bash
   kmk consume --topic primary.my_topic --cluster secondary --messages 10
   ```
   This will attempt to read 10 messages from the replicated `primary.my_topic` topic on the `secondary` cluster.

4. **Check status (optional, to be implemented):**
   ```bash
   kmk status
   ```

5. **Destroy the infrastructure:**
   ```bash
   kmk destroy
   ```
   This will stop and remove all Docker containers created by the tool.
