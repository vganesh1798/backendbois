from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

from klap4.db_entities import SQLBase, decompose_tag, get_entity_from_tag
from klap4.db_entities.genre import Genre
from klap4.db_entities.artist import Artist
from klap4.db_entities.album import Album
from klap4.db_entities.song import Song
from klap4.utils import get_json, format_object_list


def change_single_fcc(ref, song_number, fcc):
    from klap4.db import Session
    session = Session()

    album = get_entity_from_tag(ref)
    album_id = album.id

    update_song = session.query(Song) \
        .join(Album, and_(Album.id == Song.album_id, Album.id == album_id)) \
        .filter(Song.number == song_number) \
        .one()

    update_song.fcc_status = fcc
    session.commit()
    return


def change_album_fcc(ref, fcc):
    from klap4.db import Session
    session = Session()

    album = get_entity_from_tag(ref)
    for song in album.songs:
        song.fcc_status = fcc
        session.commit()
    
    return get_json(album)