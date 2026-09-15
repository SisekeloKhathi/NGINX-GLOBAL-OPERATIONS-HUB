resource "docker_network" "ops" {
  name   = var.network_name
  driver = "bridge"
}

resource "docker_volume" "postgres_data" {
  name = "28609796d10c8b51256095bb94bee597f9ec6be009bc13699a619416968231b7"
}

resource "docker_volume" "grafana_data" {
  name = "ops-grafana-data"
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
    external = var.postgres_port
  }

  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }

  networks_advanced {
    name = docker_network.ops.name
  }
}

resource "docker_container" "grafana" {
  name    = "grafana"
  image   = docker_image.grafana.image_id
  restart = "unless-stopped"

  ports {
    internal = 3000
    external = var.grafana_port
  }

  volumes {
    volume_name    = docker_volume.grafana_data.name
    container_path = "/var/lib/grafana"
  }

  networks_advanced {
    name = docker_network.ops.name
  }

  depends_on = [docker_container.postgres]
}

resource "docker_container" "nginx_gateway" {
  name    = "nginx-public-data-gateway"
  image   = docker_image.nginx_gateway.image_id
  restart = "unless-stopped"

  ports {
    internal = 80
    external = var.gateway_port
  }

  mounts {
    target    = "/etc/nginx/nginx.conf"
    source    = abspath(var.gateway_config_path)
    type      = "bind"
    read_only = true
  }

  networks_advanced {
    name = docker_network.ops.name
  }
}
