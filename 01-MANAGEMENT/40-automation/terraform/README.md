# Terraform — Operations Stack

Provisions Postgres, Grafana, and the NGINX gateway plus the shared
Docker network.

## First time

    cp terraform.tfvars.example terraform.tfvars
    # edit terraform.tfvars and set postgres_password = "secret"
    terraform init
    terraform plan
    terraform apply
