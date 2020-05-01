#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import backref, relationship

import klap4.db
from klap4.db_entities.genre import Genre
from klap4.db_entities import decompose_tag, full_module_name, SQLBase
from klap4.utils.spotify_utils import getArtistImage, getRelatedArtists

def find_genre_id(genre_abbr: str):
    entity = None

    try:
        from klap4.db import Session
        session = Session()
        entity = session.query(Genre).filter(Genre.abbreviation == genre_abbr).one()

        return entity.id
    except:
        raise "error"


class Artist(SQLBase):
    __tablename__ = "artist"

    id = Column(Integer, primary_key=True)
    genre_id = Column(Integer, ForeignKey("genre.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    number = Column(Integer, nullable=False)
    name = Column(String, nullable=False)

    genre = relationship("klap4.db_entities.genre.Genre", back_populates="artists")
    albums = relationship("klap4.db_entities.album.Album", back_populates="artist", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"])
            kwargs["genre_id"] = find_genre_id(decomposed_tag.genre_abbr)

            if decomposed_tag.artist_num is not None:
                kwargs["number"] = decomposed_tag.artist_num

            kwargs.pop("id")

        if "number" not in kwargs:
            from klap4.db_entities import get_entity_from_tag
            genre = get_entity_from_tag(kwargs["genre_abbr"])
            kwargs["number"] = genre.next_artist_num

        super().__init__(**kwargs)

    @property
    def next_album_letter(self):
        return chr(ord('A') + len(self.albums))  # TODO: Handle letter wrap around ('Z' -> 'AA')
        # 'A' + 3 == 'D'

    @property
    def ref(self):
        return self.genre.ref + str(self.number)
    

    def serialize(self):
        album_list = []
        for album in self.albums:
            album_list.append({
                                "id": album.ref,
                                "album_name": album.name,
                                "album_format": album.format_bitfield,
                                "new_album": album.is_new,
                                "has_reviews": True if len(album.reviews) > 0 else False,
                                "has_problems": True if len(album.problems) > 0 else False,
                                "missing": album.missing
                            })

        serialized_artist = {
                                "id": self.ref,
                                "name": self.name,
                                "genre": self.genre.name,
                                "albums": album_list,
                                "image": getArtistImage(self.name),
                                "related_artists": getRelatedArtists(self.name)
                            }
        return serialized_artist

    def __repr__(self):
        return f"<Artist(ref={self.ref}, " \
                       f"name={self.name}, " \
                       f"next_album_letter={self.next_album_letter})>"

    def __str__(self):
        return self.name
