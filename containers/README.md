# Docker Swarm Lab

A single-node educational lab for container delivery without AWS. The small JSON
API uses Python's standard HTTP server with no third-party dependencies. It is a
demo server, not an authenticated or production-ready application server.

## Included

- `GET /health` for container health checks.
- `GET /` with service name, application version, and replica hostname.
- Python base image pinned by OCI digest, numeric non-root user, and no pip in
  the resulting runtime image.
- Two replicas, overlay networking, read-only root filesystem, dropped Linux
  capabilities, and explicit CPU/memory limits.
- One-at-a-time start-first updates and automatic rollback configuration.

The application requires no writable mount and does not mount the Docker socket.
Swarm ingress publishes port 8081 on host interfaces; use an isolated lab machine
and do not expose this unauthenticated HTTP demo to the internet.

## Requirements

Use a recent Docker Engine (24 or newer) with Linux containers and Docker CLI
support for Swarm. On Windows, Docker Desktop must be running in Linux-container
mode. A single manager node is enough; it does not demonstrate multi-node high
availability. Git, Python 3.10+, and internet access are needed for local tests
and the initial base-image pull. No registry credentials or AWS account are used.

## Test the API Without Docker

From the repository root:

```powershell
python -m unittest discover -s containers/tests -v
```

The tests start a loopback HTTP server on a dynamically assigned port and stop it
when complete.

## Build and Deploy Locally

From the repository root, with Docker running:

```powershell
docker build --pull --tag devsecops-swarm:local containers
docker stack config --compose-file containers/stack.yml
docker info --format '{{.Swarm.LocalNodeState}}'
```

If Swarm is inactive, initialize your lab engine with `docker swarm init`. Do not
replace or leave a pre-existing Swarm. If Docker requests an address, select the
lab host's reachable local IP with `--advertise-addr`.

```powershell
docker stack deploy --resolve-image never --compose-file containers/stack.yml devsecops-demo
docker stack services devsecops-demo
docker service ps devsecops-demo_api
```

Wait until the service reports `2/2`, then open http://localhost:8081/health and
http://localhost:8081/. The local image is suitable for this single-node lab;
multi-node deployment would require distributing the image through a registry.
`--resolve-image never` avoids looking for the local image tag in a registry.

## Scale and Update

```powershell
docker service scale devsecops-demo_api=3
docker service update --env-add APP_VERSION=2.0.0 devsecops-demo_api
docker service ps devsecops-demo_api
docker service rollback devsecops-demo_api
docker service scale devsecops-demo_api=2
```

Wait for each update to finish before starting another. The update changes an
environment variable to demonstrate replacement tasks without a second image.
Automatic rollback is configured; the CI smoke test does not inject a broken
image or prove automatic rollback under failure.

## CI Lifecycle

The `Docker Build, Scan and Swarm Lab` job runs after the security guardrails:

1. Run the API tests and validate the stack with the native Docker CLI.
2. Build the image locally on the ephemeral Linux runner.
3. Scan the Dockerfile and image with Trivy, failing on HIGH or CRITICAL findings,
   including unfixed ones. Vulnerability-database or scanner errors also fail CI.
4. Initialize a temporary single-node Swarm and deploy the image just scanned.
5. Verify two healthy replicas and HTTP responses, scale to three replicas,
   perform a rolling restart, and scale back to two.
6. Print diagnostics on failure and attempt to remove the stack and temporary
   Swarm even if a previous step failed.

The CI-only Bash smoke test requires GNU `timeout`, curl, Python, and all tasks
on the same node. A 180-second timeout bounds the rolling restart. The final
`CI Gate` also requires this container job to succeed.

This is an ephemeral deployment test, not a persistent hosted application. The
job does not publish an image or connect to a local/remote personal Docker daemon.
The Docker socket used in CI belongs to the disposable GitHub runner.

## Cleanup Your Local Lab

```powershell
docker stack rm devsecops-demo
```

After the stack has disappeared, `docker swarm leave --force` is optional only
for a disposable single-node Swarm you created specifically for this lab. Do not
run it against a shared or previously existing Swarm.

## Validation Status

No Docker Engine is available in the implementation environment. API tests and
static checks are recorded separately in `docs/validation.md`. The actual image
build, image vulnerability scan, and Swarm operations must be confirmed by the
new GitHub Actions run after publishing. No successful deployment is claimed yet.

## References

- [Deploy a stack](https://docs.docker.com/engine/swarm/stack-deploy/)
- [Rolling updates](https://docs.docker.com/engine/swarm/swarm-tutorial/rolling-update/)
- [Python HTTP server limitations](https://docs.python.org/3.13/library/http.server.html)
