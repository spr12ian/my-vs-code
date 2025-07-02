def deep_sort(obj):
    if isinstance(obj, dict):
        return {k: deep_sort(obj[k]) for k in sorted(obj)}
    elif isinstance(obj, list):
        # Optionally sort lists of dicts
        if all(isinstance(x, dict) for x in obj):
            # Convert dicts to tuples of sorted items for comparison, then sort
            return [deep_sort(x) for x in sorted(obj, key=lambda d: sorted(d.items()))]
        else:
            return [deep_sort(x) for x in obj]
    else:
        return obj
