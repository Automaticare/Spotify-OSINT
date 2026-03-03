CREATE TABLE playlists (
    id          VARCHAR     PRIMARY KEY,        -- Spotify playlist ID
    name        VARCHAR     NOT NULL,
    owner_id    VARCHAR     NOT NULL,
    is_active   BOOLEAN     DEFAULT TRUE,
    added_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tracked_tracks (
    track_id    VARCHAR     NOT NULL,
    playlist_id VARCHAR     NOT NULL REFERENCES playlists(id),
    track_name  VARCHAR     NOT NULL,
    artist_names TEXT[]     NOT NULL,
    album_name  VARCHAR,
    spotify_url VARCHAR,
    added_at    TIMESTAMPTZ,                    -- Playlist'e eklenme zamanı (Spotify verisi)
    detected_at TIMESTAMPTZ DEFAULT NOW(),      -- Bizim tespit ettiğimiz zaman
    PRIMARY KEY (track_id, playlist_id)
);
