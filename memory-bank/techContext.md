# Technical Context

This document outlines the key technologies, development setup, technical constraints, and dependencies used in the Dapper Cluster project.

## Technologies Used

### Core Infrastructure

| Technology | Purpose | Description |
|------------|---------|-------------|
| **Kubernetes** | Container Orchestration | Primary platform for deploying and managing containerized applications |
| **Talos Linux** | Operating System | Minimal, immutable Linux distribution designed specifically for Kubernetes |
| **Proxmox** | Virtualization | Hypervisor platform that hosts the Talos nodes and other VMs |
| **OPNsense** | Network Routing & Firewall | Manages network traffic, security, and segmentation |
| **Aruba S2500-48p** | Network Switch | PoE-capable switch for network connectivity |

### GitOps & Automation

| Technology | Purpose | Description |
|------------|---------|-------------|
| **Flux** | GitOps Controller | Ensures cluster state matches Git repository state |
| **Renovate** | Dependency Management | Automatically updates dependencies and creates PRs |
| **GitHub Actions** | CI/CD | Runs tests and validations on changes |
| **SOPS** | Secret Management | Encrypts secrets for safe storage in Git |
| **External Secrets** | Secret Integration | Syncs secrets from external sources into Kubernetes |
| **Infisical** | Secrets Service | External service for managing secrets |

### Kubernetes Components

| Technology | Purpose | Description |
|------------|---------|-------------|
| **Cilium** | Container Networking | Provides networking and security between pods |
| **cert-manager** | Certificate Management | Automates certificate issuance and renewal |
| **ingress-nginx** | Ingress Controller | Manages external access to services |
| **OpenEBS Mayastor** | Storage | High-performance block storage for stateful workloads |
| **VolSync** | Backup & Replication | Backs up and replicates Persistent Volume Claims |
| **Kyverno** | Policy Engine | Enforces policies and governance |
| **External DNS** | DNS Management | Automatically manages DNS records |

### Observability

| Technology | Purpose | Description |
|------------|---------|-------------|
| **Prometheus** | Metrics Collection | Collects and stores metrics from cluster components |
| **Grafana** | Visualization | Dashboards for metrics visualization |
| **Alertmanager** | Alert Routing | Manages and routes alerts |
| **Loki** | Log Aggregation | Collects and indexes logs |
| **Promtail** | Log Collection | Ships logs to Loki |
| **Gatus** | Health Checks | Service health monitoring and status page |
| **UptimeRobot** | External Monitoring | Monitors external accessibility |

### Application Workloads

| Category | Examples |
|----------|----------|
| **Home Automation** | Home Assistant, ESPHome, Node-RED, Zigbee2MQTT |
| **Media** | Plex, Sonarr, Radarr, Prowlarr, Bazarr |
| **Productivity** | Paperless-ngx, Actual |
| **Security** | Authentik, Vaultwarden |
| **AI** | Ollama, Open WebUI, Wyoming Whisper |
| **Databases** | CloudNative PG, Dragonfly Redis, EMQX |

## Development Setup

### Development Environment

#### mise - Tool Version Manager

The project uses [mise](https://mise.jdx.dev/) (formerly rtx) for managing development tool versions and environment configuration. This creates a consistent development environment across different machines.

Key features used:
- **Tool Version Management**: Ensures all developers use the same versions of tools
- **Environment Variables**: Sets up consistent environment variables (e.g., `KUBERNETES_DIR`, `KUBECONFIG`)
- **Python Virtual Environment**: Automatically creates and manages a Python virtual environment
- **Task Dependencies**: Defines tasks like `deps` for installing dependencies

Configuration is in `.mise.toml` and includes tools like:
```toml
python = "3.13"
uv = "latest"
pre-commit = "latest"
"aqua:budimanjojo/talhelper" = "3.0.18"
"aqua:cloudflare/cloudflared" = "2025.2.0"
"aqua:FiloSottile/age" = "1.2.1"
"aqua:fluxcd/flux2" = "2.4.0"
"aqua:getsops/sops" = "3.9.4"
"aqua:go-task/task" = "3.41.0"
"aqua:helm/helm" = "3.17.0"
"aqua:helmfile/helmfile" = "0.170.1"
# And more...
```

#### Task - Workflow Automation

[Task](https://taskfile.dev/) is used as a task runner/build tool to standardize common operations. It functions similar to Make but with a more modern design.

Key task categories:
- **bootstrap**: Tasks for bootstrapping the cluster
- **kubernetes**: Tasks for interacting with Kubernetes
- **talos**: Tasks for managing Talos Linux
- **volsync**: Tasks for backup and storage operations

Example tasks:
- `task reconcile`: Force Flux to pull changes from Git
- `task kubernetes:apply`: Apply Kubernetes manifests
- `task talos:apply`: Apply Talos configuration

The main `Taskfile.yaml` ties together task files from `.taskfiles/` directory and sets up shared environment variables.

### Code Quality Tools

- **pre-commit**: Runs checks on code before committing
- **yamllint**: Validates YAML syntax
- **kubeconform**: Validates Kubernetes resources
- **SOPS and age**: Manages encrypted secrets

### Required CLI Tools

Specific versions of these tools are managed by mise:

- **kubectl**: Kubernetes command-line tool
- **flux**: Flux CLI for managing Flux resources
- **talosctl**: Talos Linux CLI for cluster management
- **helm/helmfile**: Kubernetes package manager and deployment tool
- **kustomize**: Kubernetes configuration customization tool
- **sops**: Secret management
- **age**: Modern encryption tool used by SOPS
- **talhelper**: Helper tool for Talos Linux configuration
- **jq/yq**: JSON and YAML processing tools
- **cloudflared**: Cloudflare Tunnel client

### Repository Structure

The repository follows a structured organization:

```
.
├── kubernetes/               # Kubernetes resources
│   ├── apps/                 # Application deployments
│   ├── bootstrap/            # Bootstrap configurations
│   ├── flux/                 # Flux system configurations
│   └── components/           # Reusable components
├── docs/                     # Documentation
│   └── src/                  # Source files for documentation
├── .taskfiles/               # Task definitions
├── .github/                  # GitHub workflows
└── memory-bank/              # Cline's memory bank
```

## Technical Constraints

### Hardware Constraints

- **CPU**: Limited to the existing hardware (2x Intel Xeon E5-2697A v4, 64 cores)
- **Memory**: 512GB RAM across all nodes
- **Storage**: 4x 3.84TB SSDs for OpenEBS storage
- **Network**: 1Gbps network connectivity
- **Power**: Limited by household power capacity and UPS capability

### Software Constraints

- **Kubernetes Version**: Must maintain compatibility with current Talos version
- **Talos Version**: Determines compatible Kubernetes versions
- **Helm Chart Compatibility**: Applications depend on compatible Helm charts
- **Container Image Availability**: Some workloads require specific architectures (amd64)
- **GPU Support**: Limited to available hardware (4x Tesla P100 16GB GPUs)

### Networking Constraints

- **IP Addressing**: Fixed subnet allocations for different networks
  - LAN: 192.168.1.1/24
  - SERVERS VLAN: 10.100.0.1/24
- **DNS**: Internal and external DNS management with specific zones
- **Ingress**: All external traffic routed through ingress controllers

### Security Constraints

- **Secret Management**: All sensitive data must be encrypted
- **Network Policies**: Strict network policies for pod communication
- **Authentication**: Centralized authentication through Authentik
- **Certificate Management**: All services must use valid TLS certificates

## Dependencies

### Critical External Dependencies

- **Domain Registrar**: For DNS management
- **Cloudflare**: For DNS and security services
- **Infisical**: For external secrets management
- **GitHub**: For repository hosting and CI/CD
- **Internet Connection**: For external access and updates

### Internal Dependencies

- **Flux**: Core dependency for GitOps workflow
- **cert-manager**: Required for certificate management
- **OpenEBS**: Critical for persistent storage
- **Cilium**: Essential for network connectivity
- **CoreDNS**: Required for Kubernetes DNS resolution
- **External Secrets**: Required for secrets management
- **Authentication**: Required for secure access to services

### Upgrade Dependencies

The system has specific upgrade ordering requirements:

1. Talos must be upgraded before Kubernetes
2. Kubernetes must be upgraded before core components
3. Core components must be upgraded before applications
4. Applications may have specific dependency chains

This technical context provides the foundation for understanding the technical aspects of the Dapper Cluster environment.
