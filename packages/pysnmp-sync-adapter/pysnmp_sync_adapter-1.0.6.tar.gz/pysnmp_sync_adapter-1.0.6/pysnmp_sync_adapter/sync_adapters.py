import os
import sys
import asyncio
import functools
import importlib
from typing import Sequence, List, Any, Union


# Determine desired architecture:
# - honor PYSNMP_ARCH if set to 'v1arch' or 'v3arch',
# - otherwise auto-detect v3arch if its module is already loaded,
# - fallback to v1arch.
_env_arch = os.getenv("PYSNMP_ARCH", "").lower()
if _env_arch in ("v1arch", "v3arch"):
    arch = _env_arch
elif "pysnmp.hlapi.v3arch.asyncio" in sys.modules:
    arch = "v3arch"
else:
    arch = "v1arch"

# Import the selected asyncio HLAPI submodule
_mod = importlib.import_module("pysnmp.hlapi." + arch + ".asyncio")

# Bind symbols
UdpTransportTarget = _mod.UdpTransportTarget
Udp6TransportTarget = _mod.Udp6TransportTarget
get_cmd = _mod.get_cmd
next_cmd = _mod.next_cmd
set_cmd = _mod.set_cmd
bulk_cmd = _mod.bulk_cmd
walk_cmd = _mod.walk_cmd
bulk_walk_cmd = _mod.bulk_walk_cmd


# Event loop & transport helpers
def ensure_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def create_transport(
    transport_cls, *addr, timeout=None, retries=None, **other_kwargs
):
    """
    Synchronously await the async factory on the given transport class.

    Example for IPv4:
    create_transport(UdpTransportTarget, ("demo.pysnmp.com", 161), timeout=2)

    Example for IPv6:
    create_transport(Udp6TransportTarget, ("2001:db8::1", 161), timeout=2)

    Only passes timeout and retries if they are not None.
    """
    loop = ensure_loop()

    # Build the factory kwargs
    factory_kwargs = {}
    if timeout is not None:
        factory_kwargs["timeout"] = timeout
    if retries is not None:
        factory_kwargs["retries"] = retries
    # Merge any extra kwargs
    factory_kwargs.update(other_kwargs)

    # Call the async factory
    coro = transport_cls.create(*addr, **factory_kwargs)
    return loop.run_until_complete(coro)


# Sync runners
def _sync_coro(coro, timeout=None):
    """
    Run the given coroutine to completion on the shared loop,
    scheduling if needed. Supports timeout in seconds.
    """
    loop = ensure_loop()
    wrapped = asyncio.wait_for(coro, timeout=timeout)
    if loop.is_running():
        task = asyncio.ensure_future(wrapped)
        return loop.run_until_complete(task)
    return loop.run_until_complete(wrapped)


def _sync_agen(agen, timeout=None):
    """ Consume an async-generator into a list synchronously. """
    async def _collect():
        out = []
        async for item in agen:
            out.append(item)
        return out
    return _sync_coro(_collect(), timeout=timeout)


def make_sync(fn):
    """ Turn any pysnmp async‐HLAPI fn into a sync wrapper. """
    @functools.wraps(fn)
    def wrapper(*args, timeout=None, **kwargs):
        return _sync_coro(fn(*args, **kwargs), timeout=timeout)
    return wrapper


# Exposed sync API
get_cmd_sync = make_sync(get_cmd)
next_cmd_sync = make_sync(next_cmd)
set_cmd_sync = make_sync(set_cmd)
bulk_cmd_sync = make_sync(bulk_cmd)


def walk_cmd_sync(*args, timeout=None, **kwargs):
    """ Sync wrapper for walk_cmd (async generator). """
    return _sync_agen(walk_cmd(*args, **kwargs), timeout=timeout)


def bulk_walk_cmd_sync(*args, timeout=None, **kwargs):
    """ Sync wrapper for bulk_walk_cmd (async generator). """
    return _sync_agen(bulk_walk_cmd(*args, **kwargs), timeout=timeout)


def parallel_get_sync(
    *args,
    queries: list,
    timeout: float = None,
    max_parallel: int = None,
    **kwargs
):
    """
    Execute multiple SNMP GET requests in parallel, with PDU packing.
    
    Signature:
        parallel_get_sync(
            SnmpDispatcher() or SnmpEngine(),
            authData,
            transportTarget,
            [contextData],         # v3arch [with SnmpEngine()];
                                   # omit for v1arch [with SnmpDispatcher()]
            queries=[...],         # required keyword-only
            timeout=5,             # optional function timeout
            max_parallel=10,       # optional throttle
            lookupMib=True,        # any extra get_cmd kwargs
        )
    
    - If an element of `queries` is a single ObjectType, it becomes its own PDU.  
    - If an element is a list/tuple of ObjectType, those are grouped into a single PDU.  
    - All PDUs fire concurrently via asyncio.gather().  
    - Returns a list of `(errInd, errStat, errIdx, varBinds)` in the same order as `queries`.
    """
    loop = ensure_loop()
    sem = asyncio.Semaphore(max_parallel) if max_parallel else None

    # wrap each query in a coroutine that acquires a semaphore before
    # calling get_cmd, then releases it
    async def _throttled_get(coro_fn):
        if sem:
            async with sem:
                return await coro_fn()
        else:
            return await coro_fn()

    # build throttled coroutines per query or per grouped sub-list
    coros = []
    for q in queries:
        if isinstance(q, (list, tuple)):
            fn = lambda q=q: get_cmd(*args, *q, **kwargs)
        else:
            fn = lambda q=q: get_cmd(*args, q, **kwargs)
        coros.append(_throttled_get(fn))

    # Gather all in parallel
    async def _gather_all():
        return await asyncio.gather(*coros)

    # Run synchronously with optional timeout and max_parallel
    return _sync_coro(_gather_all(), timeout=timeout)


def cluster_varbinds(queries, max_per_pdu):
    """
    Normalize-and-split queries into flat chunks of <= max_per_pdu var-binds.

    :param queries:     a sequence where each element is either
                         - an ObjectType, or
                         - a list/tuple of ObjectType
    :param max_per_pdu: max number of var-binds per PDU
    :return:            List of flat [ObjectType, ...] chunks
    """
    if max_per_pdu < 1:
        raise ValueError("max_per_pdu must be >= 1")

    # flatten any nested singleton lists/tuples
    flat = []
    for q in queries:
        if isinstance(q, (list, tuple)):
            flat.extend(q)
        else:
            flat.append(q)

    # chunk the flat list
    chunks = []
    for oid in flat:
        if not chunks or len(chunks[-1]) >= max_per_pdu:
            chunks.append([oid])
        else:
            chunks[-1].append(oid)

    return chunks
