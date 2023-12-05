# Standalone Spark on Docker

This configuration sets up a standalone Spark instance running on Docker.

## Build and Run

1. Build the Docker image: `docker-compose build`
2. Start the Spark master and worker: `docker-compose up`

The Spark web UI will be available at `http://localhost:8080`.

## Connect to Spark

To connect to the Spark instance, use the Spark master URL `spark://localhost:7077`.