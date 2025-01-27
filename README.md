# mcsp-argocd-poc

## Build/Development
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: asp-cicd-dev
  finalizers:
  - resources-finalizer.argocd.argoproj.io
spec:
  destination:
    name: ''
    namespace: argocd-worker
    server: 'https://kubernetes.default.svc'
  source:
    path: application-sets/aws-dev
    repoURL: 'https://github.ibm.com/automation-paas-cd-pipeline/mcsp-argocd-poc.git'
    targetRevision: HEAD
  project: cloudrock-argoproj-resources
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Test/Staging
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: asp-cicd-stg
  finalizers:
  - resources-finalizer.argocd.argoproj.io
spec:
  destination:
    name: ''
    namespace: argocd-worker
    server: 'https://kubernetes.default.svc'
  source:
    path: application-sets/aws-stg
    repoURL: 'https://github.ibm.com/automation-paas-cd-pipeline/mcsp-argocd-poc.git'
    targetRevision: HEAD
  project: cloudrock-argoproj-resources
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
  name: asp-cicd-preprod
  finalizers:
  - resources-finalizer.argocd.argoproj.io
spec:
  destination:
    name: ''
    namespace: argocd-worker
    server: 'https://kubernetes.default.svc'
  source:
    path: application-sets/aws-preprod
    repoURL: 'https://github.ibm.com/automation-paas-cd-pipeline/mcsp-argocd-poc.git'
    targetRevision: HEAD
  project: cloudrock-argoproj-resources
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

_**Note:** The `ApplicationSet` for the environment uses a manual sync policy._

## Production 
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: asp-cicd-prod
  finalizers:
  - resources-finalizer.argocd.argoproj.io
spec:
  destination:
    name: ''
    namespace: argocd-worker
    server: 'https://kubernetes.default.svc'
  source:
    path: application-sets/aws-prod
    repoURL: 'https://github.ibm.com/automation-paas-cd-pipeline/mcsp-argocd-poc.git'
    targetRevision: HEAD
  project: cloudrock-argoproj-resources
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

_**Note:** The `ApplicationSet` for the environment uses a manual sync policy._