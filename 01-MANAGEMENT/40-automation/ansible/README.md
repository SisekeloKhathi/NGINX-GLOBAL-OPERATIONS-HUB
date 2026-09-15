# Ansible — Operations Configuration

Configures containers provisioned by Terraform. Uses the
`community.docker.docker` connection plugin to run tasks inside
running containers.

## Usage

Run from WSL Ubuntu, inside this directory:

    ansible-playbook playbooks/verify.yml
    ansible-playbook playbooks/gateway.yml
    ansible-playbook playbooks/postgres_schema.yml
    ansible-playbook playbooks/site.yml
