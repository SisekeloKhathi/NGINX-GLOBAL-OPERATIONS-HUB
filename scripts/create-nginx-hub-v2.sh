#!/usr/bin/env bash

set -e

ROOT="$HOME/NGINX-GLOBAL-OPERATIONS-HUB"

echo "=============================================="
echo " NGINX GLOBAL OPERATIONS HUB"
echo " EXPANDING EXISTING BLUEPRINT"
echo "=============================================="
echo

mkdir -p "$ROOT"/01-MANAGEMENT/{01-web-server,02-reverse-proxy,03-load-balancer,04-caching,05-api-gateway,06-config-structure,07-user-permissions,08-shared-memory,09-upstreams,10-variables,11-modules}

mkdir -p "$ROOT"/02-CONFIGURATION-KNOWLEDGE/{01-load-balancing,02-security,03-memory-zones,04-mirroring,05-layer4,06-api-gateway,07-cache,08-web-server,09-reverse-proxy,10-upstreams,11-variables,12-directives,13-http,14-stream,15-events}

mkdir -p "$ROOT"/03-CONFIGURATION-DEMONSTRATE/{01-connections,02-bandwidth,03-access-control,04-logging,05-certificates,06-https-tls,07-http2,08-http3,09-compression,10-buffering,11-timeouts,12-keepalive,13-websockets,14-grpc}

mkdir -p "$ROOT"/04-TROUBLESHOOTING/{01-start-stop-reload,02-config-test,03-http-errors,04-virtual-hosts,05-location-precedence,06-client-server,07-selinux,08-tls-errors,09-dns,10-network,11-tcp,12-upstream-failures,13-timeouts,14-performance,15-502-bad-gateway,16-503-service-unavailable,17-504-gateway-timeout,18-debugging}

mkdir -p "$ROOT"/05-SECURITY/{01-authentication,02-authorization,03-rate-limiting,04-ip-filtering,05-security-headers,06-waf,07-ddos-protection,08-tls-security,09-secrets,10-access-logs,11-security-testing,12-oidc,13-jwt}

mkdir -p "$ROOT"/06-OBSERVABILITY/{01-access-logs,02-error-logs,03-metrics,04-prometheus,05-grafana,06-alerting,07-opentelemetry,08-log-analysis,09-health-checks,10-tracing}

mkdir -p "$ROOT"/07-HIGH-AVAILABILITY/{01-active-active,02-active-passive,03-failover,04-health-checks,05-backend-failure,06-load-balancer-failure,07-disaster-recovery,08-capacity,09-zero-downtime}

mkdir -p "$ROOT"/08-PERFORMANCE/{01-benchmarking,02-worker-processes,03-worker-connections,04-connection-tuning,05-keepalive,06-compression,07-buffering,08-caching,09-capacity-planning,10-load-testing,11-performance-analysis}

mkdir -p "$ROOT"/09-AUTOMATION/{01-bash,02-python,03-ansible,04-terraform,05-github-actions,06-ci-cd,07-config-validation,08-deployment-automation,09-gitops}

mkdir -p "$ROOT"/10-KUBERNETES/{01-nginx-ingress,02-services,03-ingress-routing,04-tls,05-load-balancing,06-configmaps,07-secrets,08-health-checks,09-observability,10-troubleshooting,11-helm,12-gitops}

mkdir -p "$ROOT"/11-APPLICATION-INTEGRATION/{01-rest-api,02-fastapi,03-nodejs,04-python,05-postgresql,06-redis,07-kafka,08-microservices,09-websockets,10-grpc,11-background-workers}

for domain in market vessels aviation weather fx economics; do
    mkdir -p "$ROOT"/12-DATA-SOURCES/01-$domain/{collectors,api,database,dashboard}
done

mkdir -p "$ROOT"/12-DATA-SOURCES/{07-public-apis,08-data-pipelines}

mkdir -p "$ROOT"/13-PRODUCTION-SCENARIOS/{01-service-outage,02-backend-failure,03-traffic-spike,04-certificate-expiry,05-dns-failure,06-database-failure,07-slow-application,08-memory-pressure,09-cpu-pressure,10-network-failure,11-security-incident,12-deployment-failure,13-cache-failure,14-kafka-failure,15-redis-failure}

mkdir -p "$ROOT"/14-INCIDENT-RESPONSE/{01-detection,02-triage,03-investigation,04-root-cause,05-remediation,06-work-notes,07-post-incident-review,08-runbooks}

mkdir -p "$ROOT"/15-DOCUMENTATION/{01-architecture,02-network-diagrams,03-runbooks,04-standard-operating-procedures,05-troubleshooting-guides,06-configuration-reference,07-lab-notes,08-certification-notes,09-data-source-reference,10-portfolio}

mkdir -p "$ROOT"/apps/{market,vessels,aviation,weather,fx,economics}

mkdir -p "$ROOT"/infrastructure/{01-docker,02-docker-compose,03-terraform,04-ansible,05-kubernetes,06-vagrant,07-networking,08-cloud}

mkdir -p "$ROOT"/dashboard/{01-grafana,02-prometheus,03-opensearch,04-dashboards,05-alerts,06-operations-center}

mkdir -p "$ROOT"/labs/{01-beginner,02-intermediate,03-advanced,04-production,05-disaster-recovery,06-certification}

mkdir -p "$ROOT"/scripts/{01-installation,02-validation,03-health-checks,04-testing,05-failure-injection,06-backup,07-recovery}

mkdir -p "$ROOT"/testing/{01-smoke-tests,02-http-tests,03-tcp-tests,04-load-tests,05-security-tests,06-failure-tests,07-integration-tests}

echo
echo "=============================================="
echo " BLUEPRINT EXPANSION COMPLETE"
echo "=============================================="
echo
echo "Project: $ROOT"
echo
echo "Top-level structure:"
find "$ROOT" -maxdepth 1 -type d | sort
