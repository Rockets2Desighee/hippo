# import click
# from sat_ingest.core.support_matrix import SupportMatrix
# from sat_ingest.core.adapter_registry import build_adapter

# def run_with_fallback(primary_adapter, func, func_kwargs,
#                       satellite=None, product=None,
#                       fallback_order=None, auto_fallback=False):

#     tried = []
#     errors = []

#     # Build fallback list
#     if not fallback_order:
#         if satellite:
#             choice = SupportMatrix().resolve(satellite, product)
#             fallback_order = [choice.adapter, "stac_generic"]
#         else:
#             fallback_order = ["stac_generic"]

#     if primary_adapter not in fallback_order:
#         fallback_order.insert(0, primary_adapter)

#     while fallback_order:
#         adapter_name = fallback_order.pop(0)
#         tried.append(adapter_name)
#         click.echo(f"[adapter] {adapter_name}")

#         try:
#             adapter = build_adapter(adapter_name)
#             return func(adapter, **func_kwargs)
#         except Exception as e:
#             errors.append((adapter_name, str(e)))
#             click.echo(f"{adapter_name} failed ({e})", err=True)

#             if not fallback_order:
#                 break
#             if auto_fallback:
#                 continue

#             click.echo("Remaining fallbacks:")
#             for i, name in enumerate(fallback_order, start=1):
#                 click.echo(f"  {i}. {name}")
#             choice = click.prompt("Pick fallback number (or 0 to abort)", type=int, default=1)
#             if choice == 0:
#                 break
#             if 1 <= choice <= len(fallback_order):
#                 # Move chosen adapter to the front
#                 chosen = fallback_order.pop(choice - 1)
#                 fallback_order.insert(0, chosen)
#             else:
#                 click.echo("Invalid choice, aborting.")
#                 break

#     raise click.ClickException(
#         "All adapters failed:\n" + "\n".join(f"{a}: {err}" for a, err in errors)
#     )





#######################################
#######################################

# FOR CDSE STAC

import click
from sat_ingest.core.support_matrix import SupportMatrix
from ...adapter_registry import build_adapter  # relative import to repo root

# Static hints as a backup when SupportMatrix doesn't have it
_COLLECTION_HINTS = {
    ("sentinel-2", "L2A"): ["sentinel-2-l2a"],
    ("landsat-8", "L2"): ["landsat-c2-l2"],
    ("landsat-9", "L2"): ["landsat-c2-l2"],
    ("noaa-goes", "ABI-L1b-Rad"): ["noaa-goes"],
}

def _get_default_collections(satellite, product):
    try:
        choice = SupportMatrix().resolve(satellite, product)
        if choice.collections:
            return list(choice.collections)
    except Exception:
        pass
    return _COLLECTION_HINTS.get((satellite.lower(), product), None)

def run_with_fallback(primary_adapter, func, func_kwargs,
                      satellite=None, product=None,
                      fallback_order=None, auto_fallback=False):

    # Auto-collections injection
    if satellite and "params" in func_kwargs:
        params = func_kwargs["params"]
        if not getattr(params, "collections", None):
            inferred = _get_default_collections(satellite, product)
            if inferred:
                params.collections = inferred

    tried = []
    errors = []

    if not fallback_order:
        if satellite:
            inferred = _get_default_collections(satellite, product)
            choice_adapter = None
            try:
                choice_adapter = SupportMatrix().resolve(satellite, product).adapter
            except Exception:
                pass
            fallback_order = [a for a in [choice_adapter, "stac_generic"] if a]
        else:
            fallback_order = ["stac_generic"]

    if primary_adapter not in fallback_order:
        fallback_order.insert(0, primary_adapter)

    while fallback_order:
        adapter_name = fallback_order.pop(0)
        tried.append(adapter_name)
        click.echo(f"[adapter] {adapter_name}")

        try:
            adapter = build_adapter(adapter_name)
            return func(adapter, **func_kwargs)
        except Exception as e:
            errors.append((adapter_name, str(e)))
            click.echo(f"{adapter_name} failed ({e})", err=True)

            if not fallback_order:
                break
            if auto_fallback:
                continue

            click.echo("Remaining fallbacks:")
            for i, name in enumerate(fallback_order, start=1):
                click.echo(f"  {i}. {name}")
            choice = click.prompt("Pick fallback number (or 0 to abort)", type=int, default=1)
            if choice == 0:
                break
            if 1 <= choice <= len(fallback_order):
                chosen = fallback_order.pop(choice - 1)
                fallback_order.insert(0, chosen)
            else:
                click.echo("Invalid choice, aborting.")
                break

    raise click.ClickException(
        "All adapters failed:\n" + "\n".join(f"{a}: {err}" for a, err in errors)
    )
