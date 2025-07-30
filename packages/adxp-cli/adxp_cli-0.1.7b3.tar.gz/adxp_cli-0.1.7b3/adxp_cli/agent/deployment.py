import click
import time
import requests
from requests_toolbelt import MultipartEncoder
from adxp_cli.auth.service import get_credential
from adxp_cli.agent.validation import get_file_path
from tabulate import tabulate
from typing import Optional

AGENT_PREFIX = "/api/v1/agent"


def get_agent_app_list(page: int, size: int, search: Optional[str], all: bool):
    """Get List of Agents"""
    headers, config = get_credential()
    url = f"{config.base_url}{AGENT_PREFIX}/agents/apps"

    params = {"page": str(page), "size": str(size), "target_type": "external_graph"}
    if search:
        params["search"] = search

    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 401:
        raise click.ClickException(
            "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
        )
    if res.status_code == 200:
        data = res.json().get("data")
        if data:
            # 테이블로 정제해서 출력
            table = []
            if all:
                headers_ = [
                    "id",
                    "name",
                    "description",
                    "created_at",
                    "updated_at",
                    "versions",
                ]
                for item in data:
                    versions = ", ".join(
                        str(d.get("version"))
                        for d in item.get("deployments", [])
                        if d.get("version") is not None
                    )
                    row = [
                        item.get("id", ""),
                        item.get("name", ""),
                        item.get("description", ""),
                        item.get("created_at", ""),
                        item.get("updated_at", ""),
                        versions,
                    ]
                    table.append(row)
            else:
                headers_ = ["id", "name", "versions"]
                for item in data:
                    versions = ", ".join(
                        str(d.get("version"))
                        for d in item.get("deployments", [])
                        if d.get("version") is not None
                    )
                    row = [
                        item.get("id", ""),
                        item.get("name", ""),
                        versions,
                    ]
                    table.append(row)
            click.secho("✅ Deployed Custom Agent APPs:", fg="green")
            click.echo(
                tabulate(table, headers=headers_, tablefmt="github", showindex=True)
            )
        else:
            click.secho("⚠️ No deployed custom agent apps found.", fg="yellow")
    else:
        raise click.ClickException(
            f"❌ Failed to get deployed custom agent apps: {res.status_code}\n{res.text}"
        )


def get_agent_app_detail(app_id: str, dev: bool):
    """Get Detail of Deployed Agent"""
    headers, config = get_credential()
    url = f"{config.base_url}{AGENT_PREFIX}/agents/apps/{app_id}"
    res = requests.get(url, headers=headers)
    if res.status_code == 401:
        raise click.ClickException(
            "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
        )
    elif res.status_code != 200:
        raise click.ClickException(
            f"❌ Failed to get app detail: {res.status_code}\n{res.text}"
        )

    data = res.json().get("data")
    if not data:
        click.secho("⚠️ No app detail found.", fg="yellow")
        return

    # 1. APP

    click.secho("[APP Information]", fg="green")
    app_info = {
        "id": data.get("id", ""),
        "name": data.get("name", ""),
        "description": data.get("description", ""),
        "deployment_version": data.get("deployment_version", ""),
        "deployment_status": data.get("deployment_status", ""),
        "serving_type": data.get("serving_type", ""),
        "endpoint": f"{config.base_url}/api/v1/agent_gateway/{data.get('id', '')}",
    }
    for k, v in app_info.items():
        click.echo(f"{k}: {v}")

    # 2. APIKEY
    apikey_url = f"{config.base_url}{AGENT_PREFIX}/agents/apps/{app_id}/apikeys"
    apikey_res = requests.get(apikey_url, headers=headers)
    click.secho("\n[API Key List]", fg="green")
    if apikey_res.status_code == 200:
        apikeys = apikey_res.json().get("data", [])
        if apikeys:
            for idx, key in enumerate(apikeys, 1):
                click.echo(f"{idx}. {key}")
        else:
            click.secho("No API Key found.", fg="yellow")
    else:
        click.secho(f"Failed to get API Key: {apikey_res.status_code}", fg="red")

    time.sleep(1)

    # 3. Deployment
    deployments = data.get("deployments", [])

    click.secho("\n[Versions(Deployments) List]", fg="green")
    table = []
    if dev:
        headers_ = [
            "id",
            "description",
            "serving_type",
            "version",
            "image_tag",
            "status",
            "deployed_at",
            "serving_id",
        ]
        for d in deployments:
            row = [
                d.get("id", ""),
                d.get("serving_type", ""),
                d.get("version", ""),
                d.get("image_tag", ""),
                d.get("status", ""),
                d.get("deployed_dt", ""),
                d.get("serving_id", ""),
            ]
            table.append(row)
    else:
        headers_ = ["id", "version", "image_tag", "status"]
        for d in deployments:
            row = [
                d.get("id", ""),
                d.get("version", ""),
                d.get("image_tag", ""),
                d.get("status", ""),
            ]
            table.append(row)
    if table:
        click.echo(tabulate(table, headers=headers_, tablefmt="github", showindex=True))
    else:
        click.secho("No deployment information found.", fg="yellow")

    time.sleep(1)
    # Request Example
    if not dev:
        click.secho("\n[Request Example]", fg="green")
        example_apikey = (
            apikeys[0]
            if apikey_res.status_code == 200 and apikeys
            else "<YOUR_API_KEY>"
        )
        curl_example = f"""curl -X POST "{config.base_url}/api/v1/agent_gateway/{data.get('id', '')}/invoke" \\
    -H "accept: application/json" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer {example_apikey}" \\
    -d '{{\n    "config": {{}},\n    "input": {{\n        ... User Custom...\n      }}\n  }}' """
        click.secho("\n# Curl Example:", fg="yellow")
        click.echo(curl_example)

        python_example = f"""from langserve import RemoteRunnable\n\nheaders = {{\n    "aip-user": "<your user name>",\n    "Authorization": "Bearer {example_apikey}",\n}}\n\nagent = RemoteRunnable(\n    "{config.base_url}/api/v1/agent_gateway/{data.get('id', '')}",\n    headers=headers,\n)\nresponse = agent.invoke(\n    {{...User Custom...}}\n)\n\nprint(response)\n"""
        click.secho("\n# Python Example:", fg="yellow")
        click.echo(python_example)


def create_new_apikey(app_id: str):
    """Create Additional Api Key for Deployed Agent"""
    headers, config = get_credential()
    url = f"{config.base_url}{AGENT_PREFIX}/agents/apps/{app_id}/apikeys"
    res = requests.post(url, headers=headers)
    if res.status_code == 200:
        click.secho("✅ Successfully created API Key.", fg="green")
        click.secho(
            f"API Key: {res.json().get('data', {}).get('api_key', '')}", fg="yellow"
        )
    else:
        click.secho(f"❌ Failed to create API Key: {res.status_code}", fg="red")
        click.echo(res.text)


def get_target_apikey_by_number(config, app_id, number, headers):
    """Get Target Api Key by Number"""
    apikey_url = f"{config.base_url}/api/v1/agent/agents/apps/{app_id}/apikeys"
    apikey_res = requests.get(apikey_url, headers=headers)
    if apikey_res.status_code == 401:
        raise click.ClickException(
            "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
        )
    elif apikey_res.status_code != 200:
        raise click.ClickException(
            f"❌ Failed to get API Key: {apikey_res.status_code}\n{apikey_res.text}"
        )
    apikeys = apikey_res.json().get("data", [])
    return apikeys[number - 1]


def regenerate_apikey(app_id: str, number: int):
    """Regenerate Api Key for Deployed Agent"""
    headers, config = get_credential()
    # 1. get target apikey
    target_apikey = get_target_apikey_by_number(config, app_id, number, headers)

    # regenerate
    url = f"{config.base_url}{AGENT_PREFIX}/agents/apps/{app_id}/apikeys/{target_apikey}/regenerate"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        click.secho("✅ Successfully regenerated API Key.", fg="green")
        click.secho(
            f"API Key: {res.json().get('data', {}).get('api_key', '')}", fg="yellow"
        )
    else:
        click.secho(f"❌ Failed to regenerate API Key: {res.status_code}", fg="red")


def delete_apikey_by_number(app_id: str, number: int):
    """Delete Api Key for Deployed Agent"""
    headers, config = get_credential()
    target_apikey = get_target_apikey_by_number(config, app_id, number, headers)

    url = (
        f"{config.base_url}{AGENT_PREFIX}/agents/apps/{app_id}/apikeys/{target_apikey}"
    )
    res = requests.delete(url, headers=headers)
    if res.status_code == 204:
        click.secho("✅ Successfully deleted API Key.", fg="green")
    else:
        click.secho(f"❌ Failed to delete API Key: {res.status_code}", fg="red")
        click.echo(res.text)


def deploy_agent_app(
    image: str, model: list[str], name: str, description: str, env_path: str
):
    """Deploy Agent App to A.X Platform"""
    headers, config = get_credential()
    url = f"{config.base_url}{AGENT_PREFIX}/agents/apps/custom"

    # image 형식 검증
    if not ":" in image:
        raise click.ClickException(
            "Invalid image format. Please use the format: <registry_url>:<image_tag>"
        )
    # 이미지에서 harbor_repository와 tag를 추출합니다.
    # harbor_repository: 마지막 '/' 앞까지
    # tag: 마지막 '/' 뒤의 이미지명:태그
    image_url, image_tag = image.rsplit(":", 1)
    last_slash = image_url.rfind("/")
    harbor_repository = image_url[:last_slash] if last_slash != -1 else image_url
    image_name = image_url[last_slash + 1 :] if last_slash != -1 else image_url
    tag = f"{image_name}:{image_tag}"

    data = {
        "version_description": description,
        "target_type": "external_graph",
        "serving_type": "standalone",
        "registry_url": harbor_repository,
        "image_tag": tag,
        "name": name,
        "description": description,
    }

    model_list_str = ", ".join(model) if len(model) > 0 else None
    if model_list_str:
        data["model_list"] = model_list_str
    else:
        data["model_list"] = None

    if env_path:
        config_path = get_file_path(env_path)
        with open(config_path, "rb") as f:
            data["env_file"] = (env_path, f, "text/plain")
            m = MultipartEncoder(fields=data)
            headers["Content-Type"] = m.content_type
            res = requests.post(url, data=m, headers=headers)
    else:
        m = MultipartEncoder(fields=data)
        headers["Content-Type"] = m.content_type
        res = requests.post(url, data=m, headers=headers)

    if res.status_code == 200:
        click.secho("✅ Successfully deployed agent app.", fg="green")
        print_deploy_response(res.json())
        app_id = res.json().get("data", {}).get("app_id", "")
        apikey = get_target_apikey_by_number(config, app_id, 1, headers)
        click.echo()
        click.secho("🔑 API Key", fg="green")
        click.secho(f"API Key: {apikey}", fg="green")
    else:
        click.secho(f"❌ Failed to deploy agent app: {res.status_code}", fg="red")
        click.echo(res.text)


def add_agent_deployment(
    image: str,
    model: list[str],
    name: str,
    description: str,
    env_path: str,
    app_id: str,
):
    """Deploy Agent App to A.X Platform"""
    headers, config = get_credential()
    url = f"{config.base_url}{AGENT_PREFIX}/agents/apps/deployments/custom?app_id={app_id}"

    # image 형식 검증
    if not ":" in image:
        raise click.ClickException(
            "Invalid image format. Please use the format: <registry_url>:<image_tag>"
        )
    # 이미지에서 harbor_repository와 tag를 추출합니다.
    # harbor_repository: 마지막 '/' 앞까지
    # tag: 마지막 '/' 뒤의 이미지명:태그
    image_url, image_tag = image.rsplit(":", 1)
    last_slash = image_url.rfind("/")
    harbor_repository = image_url[:last_slash] if last_slash != -1 else image_url
    image_name = image_url[last_slash + 1 :] if last_slash != -1 else image_url
    tag = f"{image_name}:{image_tag}"

    data = {
        "version_description": description,
        "target_type": "external_graph",
        "serving_type": "standalone",
        "registry_url": harbor_repository,
        "image_tag": tag,
        "name": name,
        "description": description,
    }

    model_list_str = ", ".join(model) if len(model) > 0 else None
    if model_list_str:
        data["model_list"] = model_list_str
    else:
        data["model_list"] = None

    if env_path:
        config_path = get_file_path(env_path)
        with open(config_path, "rb") as f:
            data["env_file"] = (env_path, f, "text/plain")
            m = MultipartEncoder(fields=data)
            headers["Content-Type"] = m.content_type
            res = requests.post(url, data=m, headers=headers)
    else:
        m = MultipartEncoder(fields=data)
        headers["Content-Type"] = m.content_type
        res = requests.post(url, data=m, headers=headers)

    if res.status_code == 200:
        click.secho("✅ Successfully deployed agent app.", fg="green")
        print_deploy_response(res.json())
        app_id = res.json().get("data", {}).get("app_id", "")
        apikey = get_target_apikey_by_number(config, app_id, 1, headers)
        click.echo()
        click.secho("🔑 API Key", fg="green")
        click.secho(f"API Key: {apikey}", fg="green")
    else:
        click.secho(f"❌ Failed to deploy agent app: {res.status_code}", fg="red")
        click.echo(res.text)


def print_deploy_response(response):
    """에이전트 배포 결과를 보기 좋게 출력합니다."""
    data = response.get("data", {})
    agent_params = data.get("agent_params", {})

    click.secho("🚀 에이전트 배포 결과", fg="green", bold=True)
    click.echo()

    # 주요 정보
    main_info = [
        ["Status", data.get("status", "")],
        ["App ID", data.get("app_id", "")],
        ["Version", data.get("app_version", "")],
        ["Deployment Id", data.get("deployment_id", "")],
        ["Endpoint", data.get("endpoint", "")],
        ["Description", data.get("description", "")],
        ["Created By", data.get("created_by", "")],
        ["Created At", data.get("created_at", "")],
    ]
    click.echo(tabulate(main_info, tablefmt="github"))

    click.echo()
    click.secho("🧩 리소스 정보", fg="green")
    resource_info = [
        [
            "CPU",
            f"{data.get('cpu_request', '')} (Request) / {data.get('cpu_limit', '')} (Limit)",
        ],
        [
            "Memory",
            f"{data.get('mem_request', '')}Gi (Request) / {data.get('mem_limit', '')}Gi (Limit)",
        ],
    ]
    click.echo(tabulate(resource_info, tablefmt="github"))

    click.echo()
    click.secho("🔑 모델 리스트", fg="green")
    for m in data.get("model_list", []):
        click.echo(f" - {m}")

    click.echo()
    click.secho("⚙️ Agent ENV", fg="yellow")
    env_table = [[k, v] for k, v in agent_params.items()]
    click.echo(tabulate(env_table, headers=["이름", "값"], tablefmt="github"))

    click.echo()
    click.secho("✅ Deployment started successfully.", fg="green", bold=True)
    click.echo(f"Deployment Status: {data.get('status', '')}")
    click.echo(f"Endpoint: {data.get('endpoint', '')}")


def stop_deployment(deployment_id: str):
    """Stop Deployment"""
    headers, config = get_credential()

    url = (
        f"{config.base_url}{AGENT_PREFIX}/agents/apps/deployments/stop/{deployment_id}"
    )
    res = requests.post(url, headers=headers)

    if res.status_code == 200:
        click.secho("✅ Successfully stopped deployment.", fg="green")
    else:
        click.secho(f"❌ Failed to stop deployment: {res.status_code}", fg="red")
        click.echo(res.text)


def restart_deployment(deployment_id: str):
    """Restart Deployment"""
    headers, config = get_credential()
    url = f"{config.base_url}{AGENT_PREFIX}/agents/apps/deployments/restart/{deployment_id}"
    res = requests.post(url, headers=headers)

    if res.status_code == 200:
        click.secho("✅ Successfully restarted deployment.", fg="green")
    else:
        click.secho(f"❌ Failed to restart deployment: {res.status_code}", fg="red")
        click.echo(res.text)


def delete_app(deployment_id: Optional[str], app_id: Optional[str]):
    """Delete App"""
    headers, config = get_credential()
    if app_id:
        url = f"{config.base_url}{AGENT_PREFIX}/agents/apps/{app_id}"
    elif deployment_id:
        url = f"{config.base_url}{AGENT_PREFIX}/agents/apps/deployments/{deployment_id}"
    else:
        raise click.ClickException("App ID or Deployment ID must be provided")

    res = requests.delete(url, headers=headers)
    target = f"app : {app_id}" if app_id else f"deployment : {deployment_id}"
    if res.status_code == 204:
        click.secho(f"✅ Successfully deleted {target}.", fg="green")
    else:
        click.secho(f"❌ Failed to delete {target}: {res.status_code}", fg="red")
        click.echo(res.text)


def update_app(app_id: str, name: Optional[str], description: Optional[str]):
    """Update App"""
    headers, config = get_credential()
    url = f"{config.base_url}{AGENT_PREFIX}/agents/apps/{app_id}"
    res = requests.put(
        url, headers=headers, json={"name": name, "description": description}
    )

    if res.status_code == 200:
        data = res.json().get("data", {})
        click.secho("✅ App info updated successfully.", fg="green")
        app_info = {
            "id": data.get("id", ""),
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "deployment_version": data.get("deployment_version", ""),
            "deployment_status": data.get("deployment_status", ""),
            "serving_type": data.get("serving_type", ""),
            "endpoint": f"{config.base_url}/api/v1/agent_gateway/{data.get('id', '')}",
        }
        for k, v in app_info.items():
            click.echo(f"{k}: {v}")
    else:
        click.secho(f"❌ Failed to update app info: {res.status_code}", fg="red")
        click.echo(res.text)
