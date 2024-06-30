import os
import yaml
import subprocess
from flask import Flask, request, jsonify
import jwt
import requests
from datetime import datetime, timedelta
from github import Github

app = Flask(__name__)

# GitHub App credentials
APP_ID = 'your_app_id'
INSTALLATION_ID = 'your_installation_id'
PRIVATE_KEY = open('private-key.pem', 'r').read()

# Define the folder structure and required files
folders = {
    "validation": ["00-test-runner-secret.yaml", "test-runner-job.yaml"],
    "promotion": ["00-deployment-promoter-secret.yaml", "deployment-promoter-job.yaml"],
    "change-request-creation": ["00-change-request-creator-secret.yaml", "change-request-creator-job.yaml"]
}

# Define the mandatory parameters to check first
github_params = [
    "GITHUB_TOKEN",
    "GITHUB_REPO",
    "GITHUB_BRANCH",
    "GITHUB_COMMITTER",
    "GITHUB_ORG"
]

git_params = [
    "GIT_TOKEN",
    "GIT_REPO",
    "GIT_BRANCH",
    "GIT_COMMITTER",
    "GIT_ORG"
]

# Define compulsory parameters
compulsory_params = [
    "PROMOTION_ENV",
    "PROMOTION_ENV_APP_SET",
    "PULL_REQUEST_ASSIGNEES"
]

required_annotations = [
    "argocd.argoproj.io/hook",
    "argocd.argoproj.io/hook-delete-policy",
    "argocd.argoproj.io/sync-wave"
]

job_files = {
    "test-runner-job.yaml": "validation",
    "deployment-promoter-job.yaml": "promotion",
    "change-request-creator-job.yaml": "change-request-creation"
}

expected_images = {
    "change-request-creator-job.yaml": "icr.io/automation-saas-platform/cicd/sf-change-request-creator:",
    "deployment-promoter-job.yaml": "icr.io/automation-saas-platform/cicd/deployment-promoter:",
    "test-runner-job.yaml": "icr.io/automation-saas-platform/cicd/test-runner:"
}

def get_jwt():
    # Create a JWT token
    payload = {
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=10),
        'iss': APP_ID
    }
    jwt_token = jwt.encode(payload, PRIVATE_KEY, algorithm='RS256')
    return jwt_token

def get_installation_access_token():
    jwt_token = get_jwt()
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    url = f'https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens'
    response = requests.post(url, headers=headers)
    response_data = response.json()
    return response_data['token']

def render_helm_templates(chart_dir, output_dir):
    cmd = ["helm", "template", "mychart", chart_dir, "--output-dir", output_dir]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False, f"Error rendering Helm templates: {result.stderr}"
    return True, f"Helm templates rendered successfully in {output_dir}"

def check_file_exists(base_dir, folder, file):
    file_path = os.path.join(base_dir, folder, file)
    if not os.path.exists(file_path):
        return False, file_path
    return True, file_path

def validate_yaml_file(file_path):
    try:
        with open(file_path, 'r') as f:
            yaml.safe_load(f)
        return True, None
    except yaml.YAMLError as exc:
        return False, str(exc)

def check_mandatory_params(file_path):
    missing_params = []
    github_present = False
    git_present = False
    with open(file_path, 'r') as stream:
        try:
            content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            return False, [str(exc)]

    # Merge 'data' and 'stringData' sections for easier checking
    all_params = {**content.get('data', {}), **content.get('stringData', {})}

    # Check for github parameters
    for param in github_params:
        if param in all_params and all_params[param]:
            github_present = True
            break

    # If no github parameters, check for git parameters
    if not github_present:
        for param in git_params:
            if param in all_params and all_params[param]:
                git_present = True
                break

    if not github_present and not git_present:
        missing_params.append(f"None of the GITHUB_ or GIT_ parameters are present")

    # Check for compulsory parameters and their values if any github or git parameter is present
    if github_present or git_present:
        for param in compulsory_params:
            if param not in all_params or not all_params[param]:
                missing_params.append(param)

    if missing_params:
        return False, missing_params
    return True, None

def check_annotations(file_path):
    missing_annotations = []
    with open(file_path, 'r') as stream:
        try:
            content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            return False, [str(exc)]

    annotations = content.get("metadata", {}).get("annotations", {})
    for annotation in required_annotations:
        if annotation not in annotations:
            missing_annotations.append(annotation)

    if missing_annotations:
        return False, missing_annotations
    return True, None

def check_image_value(file_path, expected_image):
    with open(file_path, 'r') as stream:
        try:
            content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            return False, str(exc)

    containers = content.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
    for container in containers:
        if "image" in container and expected_image in container["image"]:
            return True, None

    return False, f"Image key does not contain the expected substring {expected_image}"

def get_application_path(values_file):
    with open(values_file, 'r') as stream:
        try:
            values = yaml.safe_load(stream)
            return values.get('application', 'application')
        except yaml.YAMLError as exc:
            return None, f"Error parsing values.yaml: {exc}"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data.get("action") == "opened" or data.get("action") == "synchronize":
        pull_request = data["pull_request"]
        repo_full_name = pull_request["base"]["repo"]["full_name"]
        branch_name = pull_request["head"]["ref"]
        sha = pull_request["head"]["sha"]
        
        token = get_installation_access_token()
        repo = Github(token).get_repo(repo_full_name)
        base_dir = f'/tmp/{repo_full_name.split("/")[1]}'
        
        repo.clone_url()
        os.makedirs(base_dir, exist_ok=True)
        repo.clone_to_directory(base_dir, branch=branch_name)
        
        chart_dir = os.path.join(base_dir, "resources")
        values_file = os.path.join(chart_dir, "values.yaml")
        application_path, error = get_application_path(values_file)
        if error:
            return jsonify({"error": error})
        
        rendered_dir = os.path.join(chart_dir, "rendered", application_path, application_path, "templates")
        success, message = render_helm_templates(chart_dir, os.path.join(chart_dir, "rendered", application_path))
        if not success:
            return jsonify({"error": message})
        
        all_files_exist = True
        yaml_files = []
        missing_files = []
        report = {
            "stage_1": [],
            "stage_2": [],
            "stage_3": [],
            "stage_4": []
        }

        for folder, files in folders.items():
            for file in files:
                rendered_file_path = os.path.join(rendered_dir, folder, file)
                exists, file_path = check_file_exists(rendered_dir, folder, file)
                if not exists:
                    all_files_exist = False
                    missing_files.append(file_path)
                else:
                    yaml_files.append(rendered_file_path)

        if all_files_exist:
            for yaml_file in yaml_files:
                valid, error = validate_yaml_file(yaml_file)
                if not valid:
                    report["stage_1"].append((yaml_file, error))

            for file in folders["promotion"]:
                if "secret" in file:
                    rendered_file_path = os.path.join(rendered_dir, "promotion", file)
                    valid, errors = check_mandatory_params(rendered_file_path)
                    if not valid:
                        report["stage_2"].append((rendered_file_path, errors))

            for job_file, folder in job_files.items():
                job_file_path = os.path.join(rendered_dir, folder, job_file)
                valid, errors = check_annotations(job_file_path)
                if not valid:
                    report["stage_3"].append((job_file_path, errors))

            for job_file, expected_image in expected_images.items():
                job_file_path = os.path.join(rendered_dir, job_files[job_file], job_file)
                valid, error = check_image_value(job_file_path, expected_image)
                if not valid:
                    report["stage_4"].append((job_file_path, error))

            status_state = "success"
            status_description = "All checks passed successfully."
            if report["stage_1"] or report["stage_2"] or report["stage_3"] or report["stage_4"]:
                status_state = "failure"
                status_description = "Some checks failed. Please review the report."

            status = {
                "state": status_state,
                "description": status_description,
                "context": "folder-check"
            }
            status_url = f'https://api.github.com/repos/{repo_full_name}/statuses/{sha}'
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            response = requests.post(status_url, headers=headers, json=status)
            return jsonify(response.json())

        else:
            return jsonify({"error": "Some files are missing", "missing_files": missing_files})

    return "OK"

if __name__ == "__main__":
    app.run(debug=True, port=5000)
