output "postgres_connection" {
  value = "postgres://${var.postgres_user}@localhost:${var.postgres_port}/${var.postgres_db}"
}

output "grafana_url" {
  value = "http://localhost:${var.grafana_port}"
}

output "gateway_url" {
  value = "http://localhost:${var.gateway_port}"
}

output "network_name" {
  value = docker_network.ops.name
}
