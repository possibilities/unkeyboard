from points_to_lines import points_to_lines


def tracks_with_points_to_tracks_with_lines(tracks_with_points):
    tracks_with_lines = []
    for track_with_points in tracks_with_points:
        tracks_with_lines.append(
            {
                **track_with_points,
                "lines": points_to_lines(track_with_points["points"]),
            }
        )
    return tracks_with_lines
