#!/usr/bin/env python3

import argparse
import inspect
import importlib.util
import json
import os
import signal
import sys


def load_module(file_name, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pyfile_with_workflow")
    parser.add_argument("task_name")
    parser.add_argument("--base-layer")

    args = parser.parse_args()

    module = load_module(args.pyfile_with_workflow, "workflow")

    task_func = None
    for key, obj in module.__dict__.items():
        if getattr(obj, "is_task", False) and obj.__name__ == args.task_name:
            task_func = obj
            break
    else:
        raise Exception(f"Task {args.task_name} found")

    for key, value in os.environ.items():
        if key.startswith("YT_SECURE_VAULT_"):
            os.environ[key.removeprefix("YT_SECURE_VAULT_")] = value

    processed_args = []
    processed_kwargs = {}
    func_signature = inspect.signature(task_func)

    step_args = json.loads(os.environ["ORC_STEP_ARGS"])

    for key, val in func_signature.parameters.items():
        if key in step_args:
            processed_kwargs[key] = step_args[key]
        elif val.default != inspect.Parameter.empty:
            processed_kwargs[key] = val.default
        else:
            raise ValueError(f"Parameter {key} is not provided")

    func_step = task_func(*processed_args, **processed_kwargs)

    returned_values = func_step.func(*processed_args, **processed_kwargs)

    if len(func_step.retval_names) > 0:
        if not isinstance(returned_values, tuple):
            returned_values = (returned_values,)

        ret_dict = {}
        for idx, value in enumerate(returned_values):
            ret_dict[func_step.retval_names[idx]] = value

        print(json.dumps(ret_dict))


if __name__ == "__main__":
    main()
