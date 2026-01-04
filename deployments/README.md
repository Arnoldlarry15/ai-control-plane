# AI Control Plane - Deployments

This directory contains deployment configurations for production environments.

## Contents

### Kubernetes
- **kubernetes/**: Raw Kubernetes manifests
  - `deployment.yaml` - Deployment with 3 replicas, health checks, resource limits
  - `ingress.yaml` - Ingress configuration with TLS support
  - `configmap.yaml` - Configuration and secrets
  - `hpa.yaml` - Horizontal Pod Autoscaler (3-10 pods)

### Helm
- **helm/ai-control-plane/**: Helm chart for easy deployment
  - Parameterized values
  - Production-ready defaults
  - Easy upgrades and rollbacks

## Quick Start

### Using Kubernetes Manifests

```bash
# Create namespace
kubectl create namespace ai-governance

# Apply all manifests
kubectl apply -f kubernetes/

# Verify deployment
kubectl get pods -n ai-governance
kubectl get svc -n ai-governance
kubectl get ingress -n ai-governance
```

### Using Helm

```bash
# Install
helm install ai-control-plane helm/ai-control-plane \
  --namespace ai-governance \
  --create-namespace

# Upgrade
helm upgrade ai-control-plane helm/ai-control-plane \
  --namespace ai-governance

# Uninstall
helm uninstall ai-control-plane -n ai-governance
```

## Configuration

### Environment Variables

Set in `kubernetes/configmap.yaml` or Helm `values.yaml`:

- `ENVIRONMENT` - Deployment environment (default: production)
- `LOG_LEVEL` - Logging level (default: INFO)
- `POLICY_ENFORCEMENT` - Policy mode (default: strict)

### Secrets

Update `kubernetes/configmap.yaml` or use external secret management:

```bash
kubectl create secret generic ai-control-plane-secrets \
  --from-literal=admin-api-key=$(python -c "import secrets; print(secrets.token_urlsafe(32))") \
  -n ai-governance
```

### Ingress

Update `kubernetes/ingress.yaml` with your domain:

```yaml
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: ai-control-plane-tls
  rules:
  - host: your-domain.com
```

## Scaling

### Manual Scaling

```bash
kubectl scale deployment ai-control-plane \
  --replicas=5 \
  -n ai-governance
```

### Auto-scaling

HPA is configured by default:
- Min: 3 replicas
- Max: 10 replicas
- Target CPU: 70%
- Target Memory: 80%

```bash
kubectl get hpa -n ai-governance
```

## Monitoring

### Health Checks

```bash
# Check pod health
kubectl get pods -n ai-governance

# View logs
kubectl logs -f deployment/ai-control-plane -n ai-governance

# Check endpoints
kubectl get endpoints -n ai-governance
```

### Metrics

If you have Prometheus installed:

```bash
kubectl port-forward svc/ai-control-plane 8000:80 -n ai-governance
curl http://localhost:8000/metrics
```

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod <pod-name> -n ai-governance
kubectl logs <pod-name> -n ai-governance
```

### Service not accessible

```bash
kubectl get svc -n ai-governance
kubectl get ingress -n ai-governance
kubectl describe ingress ai-control-plane -n ai-governance
```

### HPA not scaling

```bash
kubectl describe hpa ai-control-plane -n ai-governance
kubectl top pods -n ai-governance
```

## Production Considerations

1. **TLS/SSL**: Configure cert-manager or provide certificates
2. **Secrets**: Use external secret management (Vault, AWS Secrets Manager)
3. **Persistence**: Configure persistent storage for audit logs
4. **Monitoring**: Set up Prometheus/Grafana
5. **Backup**: Regular backups of configurations and data
6. **Network Policies**: Restrict pod-to-pod communication
7. **Resource Limits**: Adjust based on your workload

## See Also

- [Deployment Guide](../docs/deployment-guide.md) - Comprehensive deployment documentation
- [RBAC Guide](../docs/rbac-guide.md) - Role-based access control setup
- [Compliance Guide](../docs/compliance-guide.md) - Compliance policy configuration
