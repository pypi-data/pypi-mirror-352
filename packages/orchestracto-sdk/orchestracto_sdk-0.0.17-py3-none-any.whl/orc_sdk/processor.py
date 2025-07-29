import argparse
import dataclasses
import importlib.util
import inspect
import os
import os.path
import sys
from typing import Any
from collections.abc import Iterable

import requests

from orc_client.client import OrcClient
from orc_sdk.docker import DockerImageBuildRequest, DockerImageBuilderLocal

from orc_sdk.workflow import WorkflowRuntimeObject, WfArgWrapper
from orc_sdk.step import FuncStep, RawStep
from orc_sdk.step_chain import RetValWrapper, each
from orc_sdk.utils import catchtime, catchtime_deco


@dataclasses.dataclass
class EnvConfig:
    yt_proxy: str
    yt_token: str = dataclasses.field(repr=False)
    orc_url: str
    registry_url: str

    @classmethod
    def from_env(cls) -> "EnvConfig":
        yt_host = None

        default_proto = "http"

        if yt_proxy := os.environ.get("YT_PROXY"):
            yt_host = yt_proxy.removeprefix("http://").removeprefix("https://")
            if not yt_proxy.startswith(("http://", "https://")):
                yt_proxy = f"{default_proto}://{yt_proxy}"

        if orc_url := os.environ.get("ORC_URL"):
            yt_host = orc_url.removeprefix("http://").removeprefix("https://").removeprefix("orc.")
            if not orc_url.startswith(("http://", "https://")):
                orc_url = f"{default_proto}://{orc_url}"

        assert yt_host is not None, "YT_PROXY or ORC_URL environment variable must be set"
        if yt_proxy is None:
            yt_proxy = f"{default_proto}://{yt_host}"
        if orc_url is None:
            orc_url = f"{default_proto}://orc.{yt_host}"

        if (registry_url := os.environ.get("REGISTRY_URL")) is None:
            registry_url = f"cr.{yt_host}"

        assert yt_proxy is not None
        assert orc_url is not None
        assert registry_url is not None

        return cls(
            yt_proxy=yt_proxy,
            yt_token=os.environ["YT_TOKEN"],
            orc_url=orc_url,
            registry_url=registry_url,
        )


def load_module(file_name, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def compile_wf_config(wfro: WorkflowRuntimeObject) -> dict[str, Any]:
    wf_config = {
        "triggers": [],
        "steps": [],
        "workflow_params": [{"name": wfp.name, "default_value": wfp.default_value} for wfp in wfro.wf_parameters],
    }

    steps = wfro.get_steps()
    each_arg_names = dict()
    for step_id, sci_info in steps.items():
        if isinstance(sci_info.sci, FuncStep):
            func_signature = inspect.signature(sci_info.sci.func)

            passed_args = {}
            for i, arg in enumerate(sci_info.sci.func_args):
                arg_name = list(func_signature.parameters.keys())[i]  # FIXME??
                passed_args[arg_name] = arg

            for name, value in sci_info.sci.func_kwargs.items():
                passed_args[name] = value

            step_args = []
            for i, name in enumerate(func_signature.parameters):
                if name in passed_args:
                    if isinstance(passed_args[name], RetValWrapper):
                        src_type = "step_output"
                        src_ref = f"{passed_args[name].sci.step_id}.{passed_args[name].name}"
                    elif isinstance(passed_args[name], WfArgWrapper):
                        src_type = "workflow_param"
                        src_ref = passed_args[name].name
                    else:
                        src_type = "constant"
                        src_ref = passed_args[name]
                else:
                    src_type = "constant"
                    src_ref = func_signature.parameters[name].default

                if src_ref is each:
                    each_arg_names[step_id] = name
                    continue

                step_args.append({
                    "name": name,
                    "src_type": src_type,
                    "src_ref": src_ref,
                })

            task_type = "docker"

            task_params = {
                "docker_image": "TODO",
                "command": sci_info.sci.func.__name__,
            }

            if sci_info.sci.memory_limit_bytes is not None:
                task_params["memory_limit"] = sci_info.sci.memory_limit_bytes

            if sci_info.sci.disk_request is not None:
                task_params["disk_request"] = sci_info.sci.disk_request

            outputs = [{
                "name": name,
            } for name in sci_info.sci.retval_names]


        elif isinstance(sci_info.sci, RawStep):
            task_type = sci_info.sci.task_type
            task_params = sci_info.sci.task_params

            step_args = []
            for arg in sci_info.sci.args:
                step_args.append({
                    "name": arg["name"],
                    "src_type": arg["src_type"],
                    "src_ref": arg["src_ref"],
                })

            outputs = []
            for output_name in sci_info.sci.outputs:
                outputs.append({
                    "name": output_name,
                })

            for key, value in task_params.items():
                if isinstance(value, RetValWrapper):
                    task_params[key] = f"{{{{ args.{value.name} }}}}"  # TODO: randomize value.name?
                    step_args.append({
                        "name": value.name,
                        "src_type": "step_output",
                        "src_ref": f"{value.sci.step_id}.{value.name}",
                    })

        else:
            raise NotImplementedError

        secrets = []
        for secret in sci_info.sci.secrets:
            secrets.append({
                "key": secret.key,
                "value_ref": secret.value_ref,
                "value_src_type": secret.value_src_type,
            })

        for_each = None
        if sci_info.sci._for_each is not None:
            iterable = sci_info.sci._for_each
            if isinstance(iterable, Iterable):
                arg_val = list(iterable)
                step_args.append({
                    "name": each_arg_names[step_id],
                    "src_type": "constant",
                    "src_ref": arg_val,
                })
                for_each = {
                    "loop_arg_name": each_arg_names[step_id],
                }
            elif isinstance(iterable, RetValWrapper):
                step_args.append({
                    "name": each_arg_names[step_id],
                    "src_type": "step_output",
                    "src_ref": f"{iterable.sci.step_id}.{iterable.name}",
                })
                for_each = {
                    "loop_arg_name": each_arg_names[step_id],
                }
            else:
                raise ValueError(f"Invalid for_each iterable: {iterable}")

        wf_config["steps"].append({
            "step_id": step_id,
            "task_type": task_type,
            "task_params": task_params,
            "args": step_args,
            "secrets": secrets,
            "outputs": outputs,
            "depends_on": list(sci_info.depends_on),
            "for_each": for_each,
            "cache": {
                "enable": sci_info.sci.cache.enable,
            },
            "max_retries": sci_info.sci.max_retries,
            "min_retry_interval_seconds": sci_info.sci.min_retry_interval_seconds,
        })

    wf_config["triggers"] = wfro.triggers

    return wf_config


def get_wfro_from_file(filename: str) -> WorkflowRuntimeObject:
    module = load_module(filename, "user_code")
    for key, obj in module.__dict__.items():
        if getattr(obj, "is_workflow", False):
            wfro = obj()  # TODO: args?
            return wfro
    else:
        raise Exception("No workflow found")


def get_file_module_root(filename: str) -> str:
    dirname = os.path.dirname(os.path.abspath(filename))
    if not os.path.exists(os.path.join(dirname, "__init__.py")):
        return filename
    return get_file_module_root(dirname)


BASE_IMAGE = "cr.eu-north1.nebius.cloud/e00faee7vas5hpsh3s/orchestracto/sdk-simple-runtime:34"


def get_docker_image_build_request(
        workflow_path: str,
        image_name: str,
        wf_file_module: str,
        additional_requirements: list[str],
        registry_url: str,
        tenant_dir_tag: str,
        base_image: str = BASE_IMAGE,
) -> DockerImageBuildRequest:
    py_packages_installation = f"""
            RUN pip install -U {" ".join(additional_requirements)}
            """ if additional_requirements else ""

    dockerfile = f"""
        FROM {BASE_IMAGE} AS sdk_runtime
        FROM {base_image}
        USER root
        {py_packages_installation}
        RUN mkdir /orc
        COPY --from=sdk_runtime /usr/local/lib/python3.12/site-packages/orc_sdk /orc/lib/orc_sdk
        COPY --from=sdk_runtime /usr/local/bin/orc_run_step /usr/local/bin/orc_run_step
        RUN new_shebang='#!/usr/bin/env python3' && sed -i "1s|.*|$new_shebang|" /usr/local/bin/orc_run_step
        RUN chmod +x /usr/local/bin/orc_run_step
        COPY {os.path.basename(wf_file_module)} /orc/lib/{os.path.basename(wf_file_module)}
    """

    image_rel_path = workflow_path.removeprefix("//") + "/" + image_name
    docker_tag = f"{registry_url}/{tenant_dir_tag}/public_registry/{image_rel_path}:latest"

    return DockerImageBuildRequest(dockerfile=dockerfile, image_tag=docker_tag)


@dataclasses.dataclass
class WorkflowInfo:
    workflow_path: str
    workflow_config: dict[str, Any]


@dataclasses.dataclass
class UserInfo:
    tenant_group: str
    account_name: str
    available_pool_trees: list[str]
    pool_tree_name: str
    pool_name: str
    home_path: str

    @classmethod
    def from_api_response(cls, response: dict[str, Any]) -> "UserInfo":
        return cls(
            tenant_group=response["tenant_group"],
            account_name=response["account_name"],
            available_pool_trees=response["available_pool_trees"],
            pool_tree_name=response["pool_tree_name"],
            pool_name=response["pool_name"],
            home_path=response["home_path"],
        )


def get_user_info(env_config: EnvConfig) -> UserInfo | None:
    resp = requests.get(
        f"{env_config.yt_proxy}/auth/whoami",
        headers={"Authorization": f"OAuth {env_config.yt_token}"},
    )
    resp.raise_for_status()

    login = resp.json()["login"]
    resp = requests.post(
        f"{env_config.yt_proxy}/api/v4/get",
        json={"path": f"//sys/users/{login}/@user_info"},
        headers={"Authorization": f"OAuth {env_config.yt_token}"},
    )
    if resp.status_code == 400 and resp.json().get("code") == 500:
        return None
    resp.raise_for_status()
    user_info = resp.json()
    return UserInfo.from_api_response(user_info["value"])


@catchtime_deco
def build_wf_info_from_file(filename: str, env_config: EnvConfig, debug_docker_build: bool = False) -> WorkflowInfo:
    with catchtime("get_wfro_from_file"):
        wfro = get_wfro_from_file(filename)
    with catchtime("compile_wf_config"):
        wf_config = compile_wf_config(wfro)

    wf_file_module = get_file_module_root(filename)

    if os.path.abspath(wf_file_module) != os.path.abspath(filename):
        wf_file_module_dir = os.path.dirname(wf_file_module)  # FIXME
        rel_file_path = os.path.abspath(filename).removeprefix(wf_file_module_dir + "/")
    else:
        rel_file_path = os.path.basename(filename)  # TODO FIXME
    path_in_container = f"/orc/lib/{rel_file_path}"

    default_docker_tag = None

    wfro_steps = wfro.get_steps()

    docker_build_requests: list[DockerImageBuildRequest] = []

    user_info = get_user_info(env_config=env_config)
    if user_info is None:
        tenant_dir_tag = "home/orchestracto"
    else:
        tenant_dir_tag = f"sys/orchestracto/tenants/{user_info.account_name}"  # TODO: switch to tenant name

    print("Preparing workflow config")
    for step in wf_config["steps"]:
        step_id = step["step_id"]
        sci = wfro_steps[step_id].sci
        if not isinstance(sci, FuncStep):
            continue

        if sci.additional_requirements or sci.base_image:
            dbr = get_docker_image_build_request(
                wfro.workflow_path, step_id,
                wf_file_module,
                wfro.additional_requirements + sci.additional_requirements,
                registry_url=env_config.registry_url,
                base_image=sci.base_image or BASE_IMAGE,
                tenant_dir_tag=tenant_dir_tag,
            )
            docker_build_requests.append(dbr)
            step["task_params"]["docker_image"] = dbr.image_tag
        else:
            if default_docker_tag is None:
                dbr = get_docker_image_build_request(
                    wfro.workflow_path, "default",
                    wf_file_module,
                    wfro.additional_requirements,
                    registry_url=env_config.registry_url,
                    tenant_dir_tag=tenant_dir_tag,
                )
                default_docker_tag = dbr.image_tag
                docker_build_requests.append(dbr)
            step["task_params"]["docker_image"] = default_docker_tag

        step["task_params"]["env"] = {"PYTHONPATH": "/orc/lib", "YT_BASE_LAYER": step["task_params"]["docker_image"]}
        step["task_params"]["command"] = f"exec orc_run_step {path_in_container} {sci.func.__name__} >&2"
        step["task_params"]["func_code_hash"] = sci.func_code_hash

    print("Building and pushing images")
    builder = DockerImageBuilderLocal(
        os.path.dirname(wf_file_module),
        debug_docker_build=debug_docker_build,
        registry_url=env_config.registry_url,
    )
    builder.login_in_registry(env_config.yt_token)

    with catchtime("build_and_push_docker_images"):
        build_errors = builder.build_batch(docker_build_requests)

    if build_errors:
        print("BUILD FAILED")
        for error in build_errors:
            print("=== stderr ===")
            print(error.stderr)
        sys.exit(1)

    print("Images are built and pushed")

    return WorkflowInfo(workflow_path=wfro.workflow_path, workflow_config=wf_config)


def process_python_file(filename: str, debug_docker_build: bool = False):
    env_config = EnvConfig.from_env()

    print("Preparing workflow config...")
    with catchtime("prepare_workflow_config"):
        wf_info = build_wf_info_from_file(filename, env_config=env_config, debug_docker_build=debug_docker_build)
    print("Workflow config is ready, pushing it to orchestracto")

    orc_client = OrcClient(orc_url=env_config.orc_url, yt_token=env_config.yt_token)
    with catchtime("update_workflow_config_on_yt"):
        orc_client.update_workflow(wf_info.workflow_path, wf_info.workflow_config)
    print("Workflow is updated")


def configure_arg_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    subparsers = parser.add_subparsers(dest="command")

    get_config = subparsers.add_parser("get-config")
    get_config.add_argument("filename", type=str)

    process_parser = subparsers.add_parser("process")
    process_parser.add_argument("filename", type=str)
    process_parser.add_argument("--debug-docker-build", action="store_true")

    return parser


def process_args(args: argparse.Namespace):
    match args.command:
        case "process":
            process_python_file(args.filename, debug_docker_build=args.debug_docker_build)
