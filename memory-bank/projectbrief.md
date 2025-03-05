# Dapper Cluster Project Brief

## Overview

Dapper Cluster is a GitOps repository for a production-grade homelab Kubernetes environment. It manages infrastructure using Infrastructure as Code (IaC) principles, with security and reliability as the highest priorities. This repository serves as the central source of truth for all infrastructure configuration and application deployments within the homelab environment.

## Core Objectives

- **Security First**: Implement robust security practices throughout the infrastructure, including secret management, network segmentation, and systematic updates.
- **High Reliability**: Ensure production-level reliability for all deployed applications and services.
- **GitOps Workflow**: Maintain a consistent and auditable deployment process where all changes flow through Git.
- **Infrastructure as Code**: Define and manage all infrastructure components as code for consistency and reproducibility.
- **Automated Operations**: Leverage automation for maintenance, updates, and monitoring to reduce manual intervention.

## Technologies & Tools

### Core Infrastructure
- **Kubernetes**: Container orchestration platform running on virtualized infrastructure
- **Talos Linux**: Secure, immutable Linux distribution designed for Kubernetes
- **Proxmox**: Virtualization platform hosting the Kubernetes nodes
- **OpenEBS Mayastor**: High-performance block storage for persistent workloads
- **OPNsense**: Network router and firewall providing security and segmentation

### GitOps & Automation
- **Flux**: Kubernetes GitOps operator that ensures the cluster state matches the Git repository
- **Renovate**: Automatically updates dependencies and creates pull requests
- **GitHub Actions**: CI/CD pipeline for testing and validation
- **SOPS**: Encrypted secrets management that can be safely committed to Git
- **External Secrets**: Integration with external secret stores (Infisical)

### Networking
- **Cilium**: Internal Kubernetes CNI (Container Network Interface)
- **External-DNS**: Automated DNS record management
- **Cloudflare**: External DNS and security services
- **Ingress-NGINX**: Kubernetes ingress controller for routing external traffic

### Monitoring & Observability
- **Kube-Prometheus-Stack**: Comprehensive monitoring solution
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and notifications
- **Loki**: Log aggregation and analysis
- **Gatus**: Service health monitoring and status page

## Hardware Infrastructure

The cluster runs on enterprise-grade hardware to ensure reliability:

- **Kubernetes Host**: Dual Intel Xeon E5-2697A v4 (64 cores @ 2.60GHz), 512GB RAM, 4x 3.84TB SSD
  - Running 7x virtualized Talos nodes
  - 4x Tesla P100 16GB GPUs (passthrough to Kubernetes)
- **NAS/Storage Host**: Dual Intel Xeon E5-2687W (32 cores @ 3.10GHz), 126GB RAM, Various storage
- **Networking**: OPNsense Router + Aruba S2500-48p PoE Switch

## Network Architecture

The network is segmented for security:
- **LAN (192.168.1.1/24)**: Primary network segment
- **SERVERS VLAN (10.100.0.1/24)**: Dedicated network for server infrastructure
- Private DNS via External-DNS to UniFi controller
- Public DNS via External-DNS to Cloudflare
- Dual-class ingress system (internal/external) for appropriate DNS routing

## Security Practices

- Encrypted secrets management with SOPS and External Secrets
- Network segmentation and dedicated VLANs
- Regular automated updates via Renovate
- Immutable infrastructure with Talos Linux
- Authentication services via Authentik
- Systematic scanning and policy enforcement with Kyverno

## Reliability Measures

- High-performance persistent storage with OpenEBS Mayastor
- Backup and recovery capabilities with VolSync
- Comprehensive monitoring and alerting
- Redundant services where appropriate
- Automated dependency updates to address security vulnerabilities
- Local OCI registry mirror for resilience (Spegel)

## Repository Structure

```
📁 kubernetes
├── 📁 apps           # applications organized by category
├── 📁 bootstrap      # bootstrap procedures
├── 📁 components     # re-useable components
└── 📁 flux           # flux system configuration
```

## Deployment Workflow

The GitOps workflow follows these principles:
1. All changes are committed to the Git repository
2. Flux continuously reconciles the desired state with the cluster state
3. Kustomizations and HelmReleases manage application dependencies
4. Renovate automatically creates PRs for dependency updates
5. GitHub Actions validate changes before they are applied

This repository represents a production environment for critical home services and infrastructure, with a strong emphasis on security, reliability, and GitOps best practices.
