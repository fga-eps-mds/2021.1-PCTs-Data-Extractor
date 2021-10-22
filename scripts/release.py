import argparse
import requests
import json
import mimetypes
import pytz

from datetime import datetime

PATCH_RELEASE = "PATCH"
MINOR_RELEASE = "MINOR"
MAJOR_RELEASE = "MAJOR"

RELEASE_TYPES = [
    PATCH_RELEASE,
    MINOR_RELEASE,
    MAJOR_RELEASE
]


def launch_release(repo_owner, reponame, token, release_type,
                   sonar_cloud_filename_prefix, sonar_cloud_metrics_uri):
    check_valid_pr(release_type)

    latest_tag = get_latest_tag(repo_owner, reponame)

    print("Latest tag version:", latest_tag)

    new_tag_version = get_new_version(latest_tag, release_type)

    print("New tag version:", new_tag_version)

    assets_upload_url = create_release(
        repo_owner, reponame, token, new_tag_version)

    print("Assets upload url:", assets_upload_url)
    upload_sonar_metrics_to_release(
        token, sonar_cloud_metrics_uri, sonar_cloud_filename_prefix, assets_upload_url)


def check_valid_pr(release_type):
    if release_type not in RELEASE_TYPES:
        exit(0)


def get_latest_tag(repo_owner, reponame):
    tags = requests.get(
        f"https://api.github.com/repos/{repo_owner}/{reponame}/tags"
    ).json()

    if len(tags):
        return tags[0]['name'][1:]
    else:
        return "0.0.0"


def get_new_version(latest_tag, release_type):
    tag_version_splits = latest_tag.split(".")

    if release_type == "PATCH":
        new_tag = f"v{tag_version_splits[0]}.{tag_version_splits[1]}.{int(tag_version_splits[2]) + 1}"
    elif release_type == "MINOR":
        new_tag = f"v{tag_version_splits[0]}.{int(tag_version_splits[1]) + 1}.0"
    elif release_type == "MAJOR":
        new_tag = f"v{int(tag_version_splits[0]) + 1}.0.0"

    return new_tag


def create_release(repo_owner, reponame, token, new_tag_version):
    headers = {'Authorization': f'token {token}'}
    request_body = {
        "owner": repo_owner,
        "repo": reponame,
        "tag_name": new_tag_version,
        "name": new_tag_version,
    }

    response = requests.post(
        f"https://api.github.com/repos/{repo_owner}/{reponame}/releases",
        headers=headers,
        data=json.dumps(request_body),
    )

    if response.status_code == 201:
        return response.json()["upload_url"]
    else:
        return None


def upload_sonar_metrics_to_release(token, sonar_cloud_metrics_uri, sonar_cloud_filename_prefix, assets_upload_url):
    metrics_filepath = save_sonarcloud_metrics(
        sonar_cloud_metrics_uri, sonar_cloud_filename_prefix
    )

    upload_asset(token, assets_upload_url, metrics_filepath, metrics_filepath)


def save_sonarcloud_metrics(sonar_cloud_metrics_uri, sonar_cloud_filename_prefix):
    metrics = requests.get(sonar_cloud_metrics_uri).json()
    current_date = datetime.now(pytz.timezone("America/Sao_Paulo")).strftime(format="%d-%m-%Y-%H-%M")
    metrics_filepath = f"{sonar_cloud_filename_prefix}-{current_date}.json"

    with open(metrics_filepath, "w") as file:
        json.dump(metrics, file)

    return metrics_filepath


def upload_asset(token, assets_upload_url, filepath, filename):

    assets_upload_url = assets_upload_url.replace(u'{?name,label}', '')
    print("Asset Upload url replaced:", assets_upload_url)

    asset = open(filepath, 'rb').read()
    asset_mimetype = mimetypes.guess_type(filepath)[0]

    headers = {
        'Authorization': f'token {token}',
        'Content-Type': asset_mimetype,
    }

    params = (
        ('name', filename),
    )

    response = requests.post(
        assets_upload_url,
        headers=headers,
        params=params,
        data=asset
    )

    if response.status_code == 201:
        print("=============== Upload Success")
    else:
        print("=============== Upload Fail")
        print(response.json())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--repo-owner",
        type=str,
        required=True
    )

    parser.add_argument(
        "--reponame",
        type=str,
        required=True
    )

    parser.add_argument(
        "--token",
        type=str,
        required=True
    )

    parser.add_argument(
        "--release-type",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--sonar-cloud-filename-prefix",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--sonar-cloud-metrics-uri",
        type=str,
        required=True,
    )

    args, _ = parser.parse_known_args()

    launch_release(
        args.repo_owner,
        args.reponame,
        args.token,
        args.release_type,
        args.sonar_cloud_filename_prefix,
        args.sonar_cloud_metrics_uri,
    )
