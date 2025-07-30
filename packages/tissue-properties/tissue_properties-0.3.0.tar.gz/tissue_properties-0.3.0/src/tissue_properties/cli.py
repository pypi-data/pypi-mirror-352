import fnmatch
import importlib
import inspect
import os
import pathlib
import pkgutil
import sys

import typer
from typing_extensions import Annotated, List

import tissue_properties

try:
    from thefuzz import process

    def get_matching_models(model_name, model_candidates):
        if model_name in model_candidates:
            return [model_name]
        return list(
            map(
                lambda item: item[0],
                process.extract(model_name, model_candidates, limit=3),
            )
        )

except:

    def get_matching_models(model_name, model_candidates):
        if model_name in model_candidates:
            return [model_name]
        return []


app = typer.Typer()


def get_module_name_from_file_path(filepath):
    return filepath.replace("/", ".").replace(".py", "")


def get_file_path_from_module_name(modulename):
    root = pathlib.Path(tissue_properties.__path__[0]).absolute().parent
    return root / (modulename.replace(".", "/") + ".py")


def get_list_of_models():
    models = []
    for d in filter(
        lambda item: item.is_dir() and item.name != "__pycache__",
        pathlib.Path(tissue_properties.__path__[0]).glob("*"),
    ):
        for item in os.walk(d):
            for file in item[2]:
                if file.endswith(".py") and file not in [
                    "__init__.py",
                    "reference.py",
                    "utils.py",
                ]:
                    model_file = item[0] + "/" + file
                    model_name = get_module_name_from_file_path(
                        model_file.replace(str(tissue_properties.__path__[0]) + "/", "")
                    )
                    models.append(model_name)
    return models


def get_model_class(model_name):
    model_module_name = "tissue_properties." + model_name
    model_path = get_file_path_from_module_name(model_module_name)
    spec = importlib.util.spec_from_file_location(model_module_name, model_path)
    model_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model_module)
    model_classes = []
    for name, cls in inspect.getmembers(model_module, inspect.isclass):
        if cls.__module__ == model_module_name:
            model_classes.append(cls)

    if len(model_classes) > 1:
        raise RuntimeError(f"Multiple classes found in {model_module_name}.")

    return model_classes[0]


def get_model_inputs(model_cls):
    inputs = []
    signature = inspect.signature(model_cls.__call__)
    for param in signature.parameters:
        if param == "self":
            continue
        inputs.append(param)
    return inputs


@app.command()
def list_models():
    print("Implemented Models:")
    for model in get_list_of_models():
        print(" ", model)
    pass


@app.command()
def list_model_inputs(
    model: Annotated[
        str,
        typer.Option(
            help="The model name. See a list of models with `list-models` command."
        ),
    ] = "all"
):
    implemented_models = get_list_of_models()
    if model == "all":
        models_to_print = implemented_models
    else:

        matches = get_matching_models(model, implemented_models)
        if len(matches) != 1:
            typer.echo(f"Error: '{model}' is not a model name")
        if len(matches) > 1:
            print("Did you mean one of the following?")
            for m in matches:
                print(f"  {m}")
        if len(matches) != 1:
            raise typer.Exit(1)

        models_to_print = [model]

    for model in models_to_print:
        print(f"Input parameters for '{model}' model")
        cls = get_model_class(model)
        for param in get_model_inputs(cls):
            print(f"  {param}")


@app.command()
def get(
    model: Annotated[
        List[str],
        typer.Option(
            help="The model name. See a list of models with `list-models` command."
        ),
    ] = [],
    _input: Annotated[
        List[str],
        typer.Option(
            "--input",
            help="""Model input(s) given as key=value. i.e. `--input 'wavelength="532 nm"'`""",
        ),
    ] = [],
):

    if len(model) == 0:
        print("One or more model names required.")
        raise typer.Exit(1)

    implemented_models = get_list_of_models()
    models = []
    for m in model:
        if m in implemented_models:
            models.append(m)
        if "*" in m:
            models += list(
                filter(lambda item: fnmatch.fnmatch(item, m), implemented_models)
            )

    if len(models) < 1:
        print("ERROR: No models match given string.")
        raise typer.Exit(1)

    model_inputs = {}
    for inp in _input:
        if "=" not in inp:
            print(f"ERROR: invalid model input format: '{inp}'")
            print(
                "       model inputs must be given as k=v. i.e. `--input wavelength='532 nm'`"
            )
            raise typer.Exit(2)
        inp = inp.strip().strip("'").strip('"').strip()
        k, v = inp.split("=")
        k = k.strip().strip("'").strip('"').strip()
        v = v.strip().strip("'").strip('"').strip()
        model_inputs[k] = v

    for model in models:
        cls = get_model_class(model)
        # get list of model input names
        inputs = get_model_inputs(cls)
        # replace names with values collected from user
        for i in range(len(inputs)):
            inputs[i] = model_inputs[inputs[i]]
        obj = cls()
        val = obj(*inputs)
        print(f"{model}({', '.join(inputs)}) = {val}")
