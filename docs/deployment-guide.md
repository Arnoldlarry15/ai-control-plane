# Deployment Guide

## Overview

This guide covers deploying AI Control Plane to production environments using Kubernetes and Helm.

## Prerequisites

- Kubernetes cluster (v1.24+)
- Helm 3.x
- kubectl configured
- Docker registry access
- SSL/TLS certificates (optional but recommended)

---

## Quick Start with Helm

### 1. Add Helm Repository (if published)

```bash
helm repo add ai-control-plane https://arnoldlarry15.github.io/ai-control-plane
helm repo update
```

### 2. Install with Default Values

```bash
helm install ai-control-plane ai-control-plane/ai-control-plane \
  --namespace ai-governance \
  --create-namespace
```

### 3. Customize Installation

```bash
helm install ai-control-plane ai-control-plane/ai-control-plane \
  --namespace ai-governance \
  --create-namespace \
  --set replicaCount=5 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=ai-control.example.com
```

---

## Manual Kubernetes Deployment

### 1. Build Docker Image

```bash
docker build -t ai-control-plane:latest .
docker tag ai-control-plane:latest your-registry/ai-control-plane:latest
docker push your-registry/ai-control-plane:latest
```

### 2. Create Namespace

```bash
kubectl create namespace ai-governance
```

### 3. Apply Kubernetes Manifests

```bash
kubectl apply -f deployments/kubernetes/configmap.yaml
kubectl apply -f deployments/kubernetes/deployment.yaml
kubectl apply -f deployments/kubernetes/ingress.yaml
kubectl apply -f deployments/kubernetes/hpa.yaml
```

### 4. Verify Deployment

```bash
kubectl get pods -n ai-governance
kubectl get svc -n ai-governance
kubectl logs -f deployment/ai-control-plane -n ai-governance
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `POLICY_ENFORCEMENT` | Policy enforcement mode | `strict` |
| `DEFAULT_ACTION` | Default policy action | `block` |

### Helm Values

Edit `values.yaml` to customize:

```yaml
replicaCount: 3

image:
  repository: your-registry/ai-control-plane
  tag: "v0.1.0"

ingress:
  enabled: true
  hosts:
    - host: ai-control.example.com

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

---

## Security Configuration

### 1. API Keys

Generate secure API keys:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Update secrets:

```bash
kubectl create secret generic ai-control-plane-secrets \
  --from-literal=admin-api-key=YOUR_SECURE_KEY \
  -n ai-governance
```

### 2. TLS/SSL Certificates

Using cert-manager:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@company.test
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 3. Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-control-plane
  namespace: ai-governance
spec:
  podSelector:
    matchLabels:
      app: ai-control-plane
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
```

---

## Monitoring and Observability

### 1. Prometheus Metrics

Add ServiceMonitor:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ai-control-plane
  namespace: ai-governance
spec:
  selector:
    matchLabels:
      app: ai-control-plane
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### 2. Grafana Dashboards

Import dashboard from `deployments/grafana/dashboard.json`

### 3. Log Aggregation

Configure logging to your log aggregation system:

```yaml
# Fluentd/Fluent Bit configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: ai-governance
data:
  fluent-bit.conf: |
    [INPUT]
        Name tail
        Path /var/log/containers/*ai-control-plane*.log
        Parser docker
        Tag ai-control-plane.*
    [OUTPUT]
        Name es
        Match ai-control-plane.*
        Host elasticsearch.logging.svc.cluster.local
        Port 9200
```

---

## High Availability

### 1. Multiple Replicas

```yaml
replicaCount: 5

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - ai-control-plane
        topologyKey: kubernetes.io/hostname
```

### 2. Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ai-control-plane
  namespace: ai-governance
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: ai-control-plane
```

---

## Backup and Disaster Recovery

### 1. Backup Strategy

- **Audit Logs**: Export to object storage (S3/GCS) daily
- **Policy Configurations**: Version controlled in Git
- **Agent Registry**: Export database regularly

### 2. Recovery Procedure

```bash
# Restore from backup
kubectl apply -f backup/agent-registry.yaml
kubectl apply -f backup/policies/

# Verify
kubectl get agents -n ai-governance
kubectl get policies -n ai-governance
```

---

## Scaling

### Horizontal Scaling

Auto-scaling is configured by default:

```yaml
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

### Vertical Scaling

Adjust resource limits:

```bash
helm upgrade ai-control-plane ai-control-plane/ai-control-plane \
  --set resources.limits.cpu=2000m \
  --set resources.limits.memory=2Gi
```

---

## Troubleshooting

### Pod Crashes

```bash
kubectl describe pod <pod-name> -n ai-governance
kubectl logs <pod-name> -n ai-governance --previous
```

### Network Issues

```bash
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -n ai-governance
# Inside pod:
curl http://ai-control-plane/health
```

### Performance Issues

```bash
kubectl top pods -n ai-governance
kubectl get hpa -n ai-governance
```

---

## Upgrade Procedure

### 1. Backup Current State

```bash
helm get values ai-control-plane > backup-values.yaml
kubectl get all -n ai-governance -o yaml > backup-resources.yaml
```

### 2. Upgrade

```bash
helm upgrade ai-control-plane ai-control-plane/ai-control-plane \
  --namespace ai-governance \
  --values backup-values.yaml
```

### 3. Rollback (if needed)

```bash
helm rollback ai-control-plane -n ai-governance
```

---

## Production Checklist

- [ ] SSL/TLS certificates configured
- [ ] API keys rotated and secured
- [ ] Resource limits set appropriately
- [ ] Monitoring and alerting configured
- [ ] Log aggregation set up
- [ ] Backup strategy implemented
- [ ] Network policies applied
- [ ] High availability configured
- [ ] Pod disruption budget set
- [ ] Ingress rate limiting enabled
- [ ] Security scanning integrated
- [ ] Disaster recovery plan documented

---

## Support

For deployment issues:
- Check logs: `kubectl logs -f deployment/ai-control-plane -n ai-governance`
- Review events: `kubectl get events -n ai-governance`
- Open issue: https://github.com/Arnoldlarry15/ai-control-plane/issues
