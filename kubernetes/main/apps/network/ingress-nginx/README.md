# NGINX Ingress Controller Configuration

This directory contains the configuration for NGINX Ingress Controllers in our Kubernetes cluster, managed by Flux CD.

## Directory Structure

- `certificates/`: Contains configurations for TLS certificates used by the Ingress controllers.
  - `staging.yaml`: Configurations for staging certificates.
  - `production.yaml`: Configurations for production certificates.
- `external/`: Configurations for the external-facing Ingress controller.
- `internal/`: Configurations for the internal-facing Ingress controller.
- `ks.yaml`: Kustomization file that defines how Flux CD should deploy the Ingress controllers and certificates.

## Key Components

1. **Certificates**: Managed by cert-manager, these are used to secure the Ingress routes with HTTPS.
2. **Internal Ingress Controller**: Handles traffic within the cluster or internal network.
3. **External Ingress Controller**: Manages traffic coming from outside the cluster.

## Adding a New Route

To add a new route to either the internal or external Ingress controller:

1. Determine whether your route should be internal or external.
2. Navigate to the appropriate directory (`internal/` or `external/`).
3. Create or edit the Ingress resource YAML file. For example:

   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: my-new-route
     namespace: my-namespace
     annotations:
       kubernetes.io/ingress.class: nginx
       # Add any necessary annotations here
   spec:
     rules:
     - host: my-new-route.example.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: my-service
               port:
                 number: 80
   ```

4. If you're creating a new file, make sure to add it to the `kustomization.yaml` file in the same directory.
5. Commit and push your changes. Flux CD will automatically apply the new configuration.

## Adding a New Domain with cert-manager

When adding a new domain, you'll need to set up a TLS certificate using cert-manager. Here's how to do it:

1. **Understanding certificate configuration**:
   The certificate configurations are located in the `kubernetes/main/apps/network/ingress-nginx/certificates/` directory. This directory contains:
   - `staging.yaml`: Configurations for staging certificates.
   - `production.yaml`: Configurations for production certificates.

2. **Creating a new certificate**:
   To create a certificate for your new domain, you'll need to add a new Certificate resource to either `staging.yaml` or `production.yaml`, depending on your needs. Here's an example:

   ```yaml
   ---
   apiVersion: cert-manager.io/v1
   kind: Certificate
   metadata:
     name: my-new-domain-tls
     namespace: network
   spec:
     secretName: my-new-domain-tls
     issuerRef:
       name: letsencrypt-production  # or letsencrypt-staging for staging
       kind: ClusterIssuer
     commonName: my-new-domain.example.com
     dnsNames:
     - my-new-domain.example.com
   ```

   Add this to the appropriate file (`staging.yaml` or `production.yaml`) in the `kubernetes/main/apps/network/ingress-nginx/certificates/` directory.

3. **Update Ingress resource**:
   In your Ingress resource (created in the "Adding a New Route" section), add TLS configuration:

   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: my-new-route
     namespace: my-namespace
     annotations:
       kubernetes.io/ingress.class: nginx
       cert-manager.io/cluster-issuer: "letsencrypt-production"  # or "letsencrypt-staging" for staging
   spec:
     tls:
     - hosts:
       - my-new-domain.example.com
       secretName: my-new-domain-tls
     rules:
     - host: my-new-domain.example.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: my-service
               port:
                 number: 80
   ```

4. Commit and push your changes. Flux CD will apply the new configuration, and cert-manager will automatically obtain and manage the TLS certificate for your new domain.

## Best Practices and Considerations

- Always use HTTPS for external routes. Ensure your TLS certificates are properly configured.
- Use appropriate annotations to customize the behavior of your Ingress routes (e.g., rate limiting, authentication).
- Consider using path-based routing to minimize the number of Ingress resources and simplify management.
- Regularly review and update your Ingress configurations to ensure they align with current security best practices.
- Test your new routes thoroughly in a non-production environment before deploying to production.

## Troubleshooting

If you encounter issues with your new route:
1. Check the Ingress controller logs for any error messages.
2. Verify that the backend service is running and accessible.
3. Ensure that the Ingress resource is correctly configured and applied to the cluster.
4. Check that any required annotations are correctly set.
5. For certificate issues, check the cert-manager logs and ensure the Certificate resource is correctly defined in the appropriate certificates file (staging.yaml or production.yaml).

For more detailed information on NGINX Ingress Controller configuration, refer to the [official documentation](https://kubernetes.github.io/ingress-nginx/).

For cert-manager documentation, visit the [cert-manager official documentation](https://cert-manager.io/docs/).
