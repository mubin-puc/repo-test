# cloudrock-cicd-poc

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

```