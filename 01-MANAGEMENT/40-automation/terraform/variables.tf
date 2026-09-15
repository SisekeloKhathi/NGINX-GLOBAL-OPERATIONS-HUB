variable "network_name" {
  type    = string
  default = "ops-network"
}

variable "postgres_user" {
  type    = string
  default = "admin"
}

variable "postgres_password" {
  type      = string
  sensitive = true
}

variable "postgres_db" {
  type    = string
  default = "ops_db"
}

variable "postgres_port" {
  type    = number
  default = 5432
}

variable "grafana_port" {
  type    = number
  default = 3000
}

variable "gateway_port" {
  type    = number
  default = 8118
}

variable "gateway_config_path" {
  type    = string
  default = "../../37-public-data-gateway/nginx/nginx.conf"
}
