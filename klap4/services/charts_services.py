from sqlalchemy import func, desc
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

from klap4.db_entities import SQLBase, decompose_tag, get_entity_from_tag
from klap4.db_entities.genre import Genre
from klap4.db_entities.artist import Artist
from klap4.db_entities.album import find_album, Album, AlbumReview, AlbumProblem
from klap4.db_entities.song import Song
from klap4.utils import get_json, format_object_list



def generate_chart(format: str, weeks: int) -> list:
    from datetime import datetime, timedelta

    from klap4.db import Session
    session = Session()

    chart_list = None

    weeks_ago = datetime.now() - timedelta(weeks=int(weeks))
    new_album_limit = datetime.now() - timedelta(days=30*6)

    if format == "all":
        chart_list = session.query(Song, func.sum(Song.times_played)) \
            .filter(Song.last_played > weeks_ago
            ) \
            .group_by(Song.id
            ) \
            .all()
        
    elif format == "new":
        chart_list = session.query(Song, func.sum(Song.times_played)) \
            .join(Album, and_(Album.date_added > new_album_limit, Song.album_id == Album.id)) \
            .filter(Song.last_played > weeks_ago) \
            .group_by(Song.id) \
            .all()
    
    better_charts = []
    ref_list = []

    for item in chart_list:
        genre_abbr = decompose_tag(item[0].ref).genre_abbr
        artist_num = decompose_tag(item[0].ref).artist_num
        album_letter = decompose_tag(item[0].ref).album_letter
        ref = genre_abbr + str(artist_num) + album_letter
        album = get_entity_from_tag(ref)
        if ref in ref_list:
            continue
        else:
            total_plays = album.total_plays
            better_charts.append((genre_abbr, artist_num, album_letter, total_plays))
            ref_list.append(ref)
    
    sorted_charts = sorted(better_charts, key=lambda x:(-x[3], x[0], x[1], x[2]))
    return sorted_charts


def charts_format(chart_list):
    formatted_list = []
    for entry in chart_list:
        genre_tag = entry[0]
        artist_tag = genre_tag + str(entry[1])
        album_tag = artist_tag + entry[2]

        genre = get_entity_from_tag(genre_tag)
        artist = get_entity_from_tag(artist_tag)
        album = get_entity_from_tag(album_tag)

        formatted_album = {
                    "album_id": album_tag,
                    "rank": chart_list.index(entry)+1,
                    "genre": genre.name,
                    "artist_name": artist.name,
                    "album_name": album.name,
                    "label_name": None if album.label_id is None else album.label.name,
                    "promoter_name": None if album.promoter_id is None else album.promoter.name,
                    "times_played": entry[3]
        }
        formatted_list.append(formatted_album)
    
    return formatted_list