resource "docker_network" "ops" {
  name   = var.network_name
  driver = "bridge"
}

resource "docker_volume" "postgres_data" {
  name = "28609796d10c8b51256095bb94bee597f9ec6be009bc13699a619416968231b7"
}

resource "docker_volume" "grafana_data" {
  name = "grafana-storage"
}

resource "docker_image" "postgres" {
  name         = "postgres:15"
  keep_locally = true
}

resource "docker_image" "grafana" {
  name         = "grafana/grafana:latest"
  keep_locally = true
}

resource "docker_image" "nginx_gateway" {
  name         = "nginx:alpine"
  keep_locally = true
}

resource "docker_image" "display_api" {
  name         = "ops-display-api:latest"
  keep_locally = true
}

resource "docker_image" "prometheus" {
  name         = "prom/prometheus:latest"
  keep_locally = true
}

resource "docker_image" "nginx_exporter" {
  name         = "nginx/nginx-prometheus-exporter:latest"
  keep_locally = true
}

resource "docker_container" "postgres" {
  name    = "postgres"
  image   = docker_image.postgres.image_id
  restart = "unless-stopped"
  env = [
    "POSTGRES_USER=${var.postgres_user}",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=${var.postgres_db}",
  ]
  ports {
    internal = 5432
    external = 5432
    ip       = "127.0.0.1"
  }
  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }
  networks_advanced { name = docker_network.ops.name }
}

resource "docker_container" "grafana" {
  name    = "grafana"
  image   = docker_image.grafana.image_id
  restart = "unless-stopped"
  volumes {
    volume_name    = docker_volume.grafana_data.name
    container_path = "/var/lib/grafana"
  }
  networks_advanced { name = docker_network.ops.name }
  depends_on = [docker_container.postgres]
}

resource "docker_container" "display_api" {
  name    = "display-api"
  image   = docker_image.display_api.image_id
  restart = "unless-stopped"
  env = [
    "DB_HOST=postgres",
    "DB_PORT=5432",
    "DB_NAME=${var.postgres_db}",
    "DB_USER=${var.postgres_user}",
    "DB_PASSWORD=${var.postgres_password}",
  ]
  networks_advanced { name = docker_network.ops.name }
  depends_on = [docker_container.postgres]
}

resource "docker_container" "prometheus" {
  name    = "prometheus"
  image   = docker_image.prometheus.image_id
  restart = "unless-stopped"
  mounts {
    target    = "/etc/prometheus/prometheus.yml"
    source    = abspath("../../../17-DASHBOARD/02-prometheus/prometheus.yml")
    type      = "bind"
    read_only = true
  }
  networks_advanced { name = docker_network.ops.name }
}

resource "docker_container" "nginx_exporter" {
  name    = "nginx-exporter"
  image   = docker_image.nginx_exporter.image_id
  restart = "unless-stopped"
  command = ["-nginx.scrape-uri=http://nginx-public-data-gateway:80/nginx_status"]
  networks_advanced { name = docker_network.ops.name }
  depends_on = [docker_container.nginx_gateway]
}

resource "docker_container" "nginx_gateway" {
  name    = "nginx-public-data-gateway"
  image   = docker_image.nginx_gateway.image_id
  restart = "unless-stopped"
  ports {
    internal = 80
    external = var.gateway_port
  }
  ports {
    internal = 443
    external = 8443
  }
  mounts {
    target    = "/etc/nginx/nginx.conf"
    source    = abspath(var.gateway_config_path)
    type      = "bind"
    read_only = true
  }
  mounts {
    target    = "/etc/nginx/.htpasswd"
    source    = abspath("../../37-public-data-gateway/nginx/.htpasswd")
    type      = "bind"
    read_only = true
  }
  mounts {
    target    = "/etc/nginx/certs"
    source    = abspath("../../37-public-data-gateway/certs")
    type      = "bind"
    read_only = true
  }
  mounts {
    target    = "/var/www/screen"
    source    = abspath("../../../../17-DASHBOARD/06-operations-center/screens")
    type      = "bind"
    read_only = true
  }
  networks_advanced { name = docker_network.ops.name }
}
