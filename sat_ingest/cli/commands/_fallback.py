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

# # FOR CDSE STAC

# import click
# from sat_ingest.core.support_matrix import SupportMatrix
# from ...adapter_registry import build_adapter  # relative import to repo root

# # Static hints as a backup when SupportMatrix doesn't have it
# _COLLECTION_HINTS = {
#     ("sentinel-2", "L2A"): ["sentinel-2-l2a"],
#     ("landsat-8", "L2"): ["landsat-c2-l2"],
#     ("landsat-9", "L2"): ["landsat-c2-l2"],
#     ("noaa-goes", "ABI-L1b-Rad"): ["noaa-goes"],
# }

# def _get_default_collections(satellite, product):
#     try:
#         choice = SupportMatrix().resolve(satellite, product)
#         if choice.collections:
#             return list(choice.collections)
#     except Exception:
#         pass
#     return _COLLECTION_HINTS.get((satellite.lower(), product), None)

# def run_with_fallback(primary_adapter, func, func_kwargs,
#                       satellite=None, product=None,
#                       fallback_order=None, auto_fallback=False):

#     # Auto-collections injection
#     if satellite and "params" in func_kwargs:
#         params = func_kwargs["params"]
#         if not getattr(params, "collections", None):
#             inferred = _get_default_collections(satellite, product)
#             if inferred:
#                 params.collections = inferred

#     tried = []
#     errors = []

#     if not fallback_order:
#         if satellite:
#             sm = SupportMatrix()
#             fallback_order = sm.get_all_adapters(satellite, product)
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
#                 chosen = fallback_order.pop(choice - 1)
#                 fallback_order.insert(0, chosen)
#             else:
#                 click.echo("Invalid choice, aborting.")
#                 break

#     raise click.ClickException(
#         "All adapters failed:\n" + "\n".join(f"{a}: {err}" for a, err in errors)
#     )


############################################################
############
# ONE FINAL TRY
# sat_ingest/_fallback.py
import click
from sat_ingest.core.support_matrix import get_all_adapters
from sat_ingest.adapter_registry import build_adapter

def run_with_fallback(primary_adapter, func, func_kwargs,
                      satellite=None, product=None,
                      fallback_order=None, auto_fallback=False):
    """
    Try running func with the primary adapter. If it fails, try other adapters that
    support the same satellite/product combination.
    """
    tried = []
    if fallback_order:
        adapters_to_try = [primary_adapter] + [a for a in fallback_order if a != primary_adapter]
    elif satellite and product:
        # dynamically suggest adapters based on support matrix
        adapters_to_try = get_all_adapters(satellite, product)
        if primary_adapter in adapters_to_try:
            adapters_to_try.remove(primary_adapter)
        adapters_to_try.insert(0, primary_adapter)
    else:
        adapters_to_try = [primary_adapter]

    for adapter_name in adapters_to_try:
        if adapter_name in tried:
            continue
        tried.append(adapter_name)

        click.echo(f"[adapter] {adapter_name}")
        try:
            adapter = build_adapter(adapter_name)
            func(adapter, **func_kwargs)
            return  # success, exit
        except Exception as e:
            click.echo(f"[error] Adapter '{adapter_name}' failed: {e}")
            if adapter_name == adapters_to_try[-1]:
                raise
            if not auto_fallback:
                cont = click.prompt(f"Try next adapter? (y/n)", type=str, default="y")
                if cont.lower() != "y":
                    raise
    raise RuntimeError("All fallback adapters failed.")




#####################################
# support S1, S2, S3, S5P, Landsat, and GOES in the same fallback system
#####################################

# from __future__ import annotations
# import click
# import inspect
# from typing import Any, Union
# from sat_ingest.adapter_registry import build_adapter
# from sat_ingest.support_matrix import SupportMatrix

# def run_with_fallback(
#     initial_source: str,
#     params: Union[Any, str],
#     fallback_order: str | None,
#     auto_fallback: bool,
#     op_name: str,
#     op_kwargs: dict | None = None
# ):
#     """
#     Runs an operation (search, download, quicklook) with fallback logic.
#     `params` may be a SearchParams or a path string (for quicklook).
#     """
#     op_kwargs = op_kwargs or {}

#     if fallback_order:
#         fallbacks = [s.strip() for s in fallback_order.split(",") if s.strip()]
#     else:
#         if hasattr(params, "collections"):  # SearchParams
#             sat = getattr(params, "satellite", None)
#             prod = getattr(params, "product", None)
#         else:
#             sat = None
#             prod = None
#         fallbacks = SupportMatrix().get_fallbacks(sat or "", prod)

#     tried = {}
#     current_source = initial_source
#     if not current_source:
#         current_source = fallbacks[0] if fallbacks else None

#     for adapter_name in [current_source] + [f for f in fallbacks if f != current_source]:
#         click.echo(f"[adapter] {adapter_name}")
#         try:
#             adapter = build_adapter(adapter_name)
#             if not hasattr(adapter, op_name):
#                 raise ValueError(f"Adapter '{adapter_name}' does not implement {op_name}()")

#             method = getattr(adapter, op_name)
#             sig = inspect.signature(method)
#             if "params" in sig.parameters:
#                 method(params, **op_kwargs)
#             else:
#                 method(**({"params": params} | op_kwargs))
#             return  # success → stop fallback chain
#         except Exception as e:
#             tried[adapter_name] = str(e)
#             if auto_fallback:
#                 continue
#             else:
#                 remaining = [f for f in fallbacks if f not in tried]
#                 if not remaining:
#                     break
#                 click.echo("Remaining fallbacks:")
#                 for idx, rem in enumerate(remaining, 1):
#                     click.echo(f"  {idx}. {rem}")
#                 choice = click.prompt(
#                     "Pick fallback number (or 0 to abort)", type=int, default=1
#                 )
#                 if choice == 0:
#                     break
#                 current_source = remaining[choice - 1]

#     click.echo("Error: All adapters failed:")
#     for name, err in tried.items():
#         click.echo(f"{name}: {err}")
