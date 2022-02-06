# cloudrock-cicd-poc

## Development
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cloudrock-cicd-poc
spec:
  destination:
    name: ''
    namespace: argocd
    server: 'https://kubernetes.default.svc'
  source:
    path: application-sets/aws-dev
    repoURL: 'https://github.ibm.com/sujeily-fonseca/cloudrock-cicd-poc.git'
    targetRevision: HEAD
  project: application-sets
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Staging
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cloudrock-cicd-poc
spec:
  destination:
    name: ''
    namespace: argocd
    server: 'https://kubernetes.default.svc'
  source:
    path: application-sets/aws-stg
    repoURL: 'https://github.ibm.com/sujeily-fonseca/cloudrock-cicd-poc.git'
    targetRevision: HEAD
  project: application-sets
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Pre-Production
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cloudrock-cicd-poc
spec:
  destination:
    name: ''
    namespace: argocd
    server: 'https://kubernetes.default.svc'
  source:
    path: application-sets/aws-preprod
    repoURL: 'https://github.ibm.com/sujeily-fonseca/cloudrock-cicd-poc.git'
    targetRevision: HEAD
  project: application-sets

```

## Production 
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cloudrock-cicd-poc
spec:
  destination:
    name: ''
    namespace: argocd
    server: 'https://kubernetes.default.svc'
  source:
    path: application-sets/aws-prod
    repoURL: 'https://github.ibm.com/sujeily-fonseca/cloudrock-cicd-poc.git'
    targetRevision: HEAD
  project: application-sets

```