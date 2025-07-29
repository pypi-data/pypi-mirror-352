import abc
import concurrent.futures
import dataclasses
import os
import subprocess
import sys

from orc_sdk.utils import catchtime_deco

DEFAULT_DOCKER_COMMAND = "docker"


@dataclasses.dataclass
class DockerImageBuildRequest:
    dockerfile: str
    image_tag: str


@dataclasses.dataclass
class DockerImageBuildErrorInfo:
    stderr: str | None


@dataclasses.dataclass
class DockerImageBuilderBase:
    build_root: str
    registry_url: str
    debug_docker_build: bool = False

    @abc.abstractmethod
    def login_in_registry(self, token: str) -> None:
        pass

    @abc.abstractmethod
    def build_image(self, build_request: DockerImageBuildRequest) -> DockerImageBuildErrorInfo | None:
        pass

    @abc.abstractmethod
    def build_batch(self, build_requests: list[DockerImageBuildRequest]) -> list[DockerImageBuildErrorInfo]:
        pass


@dataclasses.dataclass
class DockerImageBuilderLocal(DockerImageBuilderBase):
    max_parallel: int = 4
    docker_command: str = dataclasses.dataclass(init=False)

    def __post_init__(self):
        self.docker_command = os.environ.get("DOCKER_COMMAND", DEFAULT_DOCKER_COMMAND)

    def _supports_push_on_build(self) -> bool:
        return self.docker_command.split("/")[-1] != "buildah"  # TODO: check `--version`

    @catchtime_deco
    def login_in_registry(self, token: str) -> None:
        proc = subprocess.Popen(
            [self.docker_command, "login", "--password-stdin", "-u", "user", self.registry_url],
            stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr
        )
        proc.communicate(token.encode())
        if proc.wait() != 0:
            raise Exception("Login failed")

    def build_image(self, build_request: DockerImageBuildRequest) -> DockerImageBuildErrorInfo | None:
        stdout = sys.stdout if self.debug_docker_build else subprocess.PIPE
        stderr = sys.stderr if self.debug_docker_build else subprocess.PIPE

        build_command = [
            self.docker_command, "build",
            "--platform", "linux/amd64",
            "-t", build_request.image_tag,
            "-f", "-",
            self.build_root,
        ]

        if self._supports_push_on_build():
            build_command.append("--push")

        run_res = subprocess.run(
            build_command,
            input=build_request.dockerfile.encode(),
            env={"BUILDKIT_PROGRESS": "plain", **os.environ},
            stdout=stdout, stderr=stderr,
        )
        if run_res.returncode != 0:
            provided_stderr = run_res.stderr.decode() if not self.debug_docker_build else None
            return DockerImageBuildErrorInfo(stderr=provided_stderr)

        if not self._supports_push_on_build():
            run_res = subprocess.run([self.docker_command, "push", build_request.image_tag], stdout=stdout, stderr=stderr)
            if run_res.returncode != 0:
                provided_stderr = run_res.stderr.decode() if not self.debug_docker_build else None
                return DockerImageBuildErrorInfo(stderr=provided_stderr)

    def build_batch(self, build_requests: list[DockerImageBuildRequest]) -> list[DockerImageBuildErrorInfo]:
        errors = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
            future_to_build_request = {
                executor.submit(self.build_image, build_request): build_request
                for build_request in build_requests
            }
            for idx, future in enumerate(concurrent.futures.as_completed(future_to_build_request)):
                error_data = future.result()
                if error_data is not None:
                    errors.append(error_data)
                print("Build", idx + 1, "of", len(build_requests), "is done")

        return errors
