# cloudrock-cicd-poc

## Development
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cloudrock-cicd-dev
spec:
  destination:
    name: ''
    namespace: argocd
    server: 'https://kubernetes.default.svc'
  source:
    path: application-sets/aws-dev
    repoURL: 'https://github.ibm.com/automation-paas-cd-pipeline/cloudrock-cicd-poc.git'
    targetRevision: HEAD
  project: application-sets
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

## Staging
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cloudrock-cicd-stg
spec:
  destination:
    name: ''
    namespace: argocd
    server: 'https://kubernetes.default.svc'
  source:
    path: application-sets/aws-stg
    repoURL: 'https://github.ibm.com/automation-paas-cd-pipeline/cloudrock-cicd-poc.git'
    targetRevision: HEAD
  project: application-sets
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

## Pre-Production
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cloudrock-cicd-preprod
spec:
  destination:
    name: ''
    namespace: argocd
    server: 'https://kubernetes.default.svc'
  source:
    path: application-sets/aws-preprod
    repoURL: 'https://github.ibm.com/automation-paas-cd-pipeline/cloudrock-cicd-poc.git'
    targetRevision: HEAD
  project: application-sets

```

## Production 
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cloudrock-cicd-prod
spec:
  destination:
    name: ''
    namespace: argocd
    server: 'https://kubernetes.default.svc'
  source:
    path: application-sets/aws-prod
    repoURL: 'https://github.ibm.com/automation-paas-cd-pipeline/cloudrock-cicd-poc.git'
    targetRevision: HEAD
  project: application-sets
```