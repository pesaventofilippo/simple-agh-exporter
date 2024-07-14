# simple-agh-exporter
A very basic AdGuard Home Prometheus Exporter

### Description
This is a very basic Prometheus exporter for [AdGuard Home](https://github.com/AdguardTeam/AdGuardHome).  
Very few metrics are exported: I selected only the ones I was interested in.

## Usage
The exporter is configured using environment variables.  
Some variables have a default value, so you can leave them undefined, if you want.

| Variable            | Description                                        | Default       |
|---------------------|----------------------------------------------------|---------------|
| `PROMETHEUS_PORT`   | The port the exporter listens on                   | `8000`        |
| `PROMETHEUS_PREFIX` | The prefix for the Prometheus metrics              | `"agh"`       |
| `ADGUARD_SERVER`    | Address (with protocol and port) of the AGH server | `"localhost"` |
| `ADGUARD_USERNAME`  | The username for the AGH server                    | -             |
| `ADGUARD_PASSWORD`  | The password for the AGH server                    | -             |

## Docker
The exporter is available as a Docker image on the [GitHub Container Registry](https://ghcr.io/pesaventofilippo/simple-agh-exporter).

To run the exporter using Docker, you can use the following command:
```bash
docker run -d -p 8000:8000 \
    -e ADGUARD_USERNAME=your-username \
    -e ADGUARD_PASSWORD=your-password \
    ghcr.io/pesaventofilippo/simple-agh-exporter
```

### docker-compose
You can also use `docker-compose` to run the exporter.
Here is an example `docker-compose.yml` file:
```yaml
services:
  simple-agh-exporter:
    image: ghcr.io/pesaventofilippo/simple-agh-exporter
    ports:
      - 8000:8000
    environment:
      ADGUARD_USERNAME: your-username
      ADGUARD_PASSWORD: your-password
```
