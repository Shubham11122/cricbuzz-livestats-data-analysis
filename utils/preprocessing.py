def extract_matches_list(recent_matches_json, limit=20):
    """
    Walks the nested typeMatches -> seriesMatches -> seriesAdWrapper -> matches
    structure and returns a flat list of matchInfo dicts.
    Skips 'ad' placeholder entries that have no seriesAdWrapper key.
    Stops once `limit` matches are collected (keeps API usage manageable).
    """
    flat_matches = []

    for type_block in recent_matches_json.get("typeMatches", []):
        for series_block in type_block.get("seriesMatches", []):
            wrapper = series_block.get("seriesAdWrapper")
            if wrapper is None:
                continue  # this is an ad placeholder, skip it

            for match in wrapper.get("matches", []):
                match_info = match.get("matchInfo")
                if match_info:
                    flat_matches.append(match_info)

                if len(flat_matches) >= limit:
                    return flat_matches

    return flat_matches