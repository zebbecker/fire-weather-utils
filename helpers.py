import math

def iter_features_offset(w, collection_id, params=None, page_size=100, max_pages=None, progress=True):
    """
    Paginate through OGC API Features using offset parameter.
    - Uses w.collection_items() with offset increments
    - Default page_size=100
    - Shows progress as pages are fetched
    """
    params = dict(params or {})
    
    # Get total count with minimal data
    meta_params = dict(params)
    meta_params["limit"] = 1
    meta = w.collection_items(collection_id, **meta_params)
    total = meta.get("numberMatched", 0)
    
    if total == 0:
        if progress:
            print("No matching features")
        return []
    # Round up the division here for total number of pages
    pages = math.ceil(total / page_size)

    # Support a user-defined page limit
    if max_pages and max_pages < pages:
        pages = max_pages

    all_features = []
    
    for i in range(pages):
        offset = i * page_size
        page_params = dict(params)
        page_params["limit"] = page_size
        page_params["offset"] = offset
        
        page = w.collection_items(collection_id, **page_params)
        features = page.get("features", [])
        all_features.extend(features)
        
        if progress:
            print(f"Page {i+1}/{pages}: {len(all_features)}/{total} features")
        
        if len(features) < page_size:
            break
    
    return all_features