#!/usr/bin/env python3

from datetime import datetime, timedelta

from sqlalchemy import Column, ForeignKey, UniqueConstraint, Boolean, DateTime, String, Integer
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import and_

import klap4.db
from klap4.db_entities.genre import Genre
from klap4.db_entities.artist import Artist
from klap4.db_entities import decompose_tag, full_module_name, SQLBase
from klap4.utils.spotify_utils import getAlbumCover


def find_artist_id(genre_abbr: str, artist_num: int):
    entity = None
    try:
        from klap4.db import Session
        session = Session()

        entity = session.query(Artist) \
            .join(Genre, and_(Genre.id == Artist.genre_id, Genre.abbreviation == genre_abbr)) \
            .filter(Artist.number == artist_num).one()
        
        return entity.id
    except:
        raise "error"


def find_album(genre_abbr: str, artist_num: int, album_letter: str):
    entity = None
    try:
        from klap4.db import Session
        session = Session()

        entity = session.query(Album) \
            .join(Artist, and_(Artist.id == Album.artist_id, Artist.number == artist_num)) \
            .join(Genre, and_(Genre.id == Artist.genre_id, Genre.abbreviation == genre_abbr)) \
            .filter(Album.letter == album_letter).one()
        
        return entity
    except:
        raise "error"

class Album(SQLBase):
    __tablename__ = "album"

    class FORMAT:
        VINYL = 0b00001
        CD = 0b00010
        DIGITAL =0b00100
        SINGLE = 0b01000
        SEVENINCH = 0b10000

    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artist.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    letter = Column(String(1), nullable=False)
    name = Column(String, nullable=False)
    date_added = Column(DateTime, nullable=False)
    missing = Column(Boolean, nullable=False)
    format_bitfield = Column(Integer, nullable=False)
    label_id = Column(Integer, ForeignKey('label.id'), nullable=True)
    promoter_id = Column(Integer, ForeignKey('promoter.id'), nullable=True)

    artist = relationship("klap4.db_entities.artist.Artist", back_populates="albums")
    label = relationship("klap4.db_entities.label_and_promoter.Label", back_populates="albums")
    promoter = relationship("klap4.db_entities.label_and_promoter.Promoter", back_populates="albums")
    
    reviews = relationship("klap4.db_entities.album.AlbumReview", back_populates="album", cascade="all, delete-orphan")
    problems = relationship("klap4.db_entities.album.AlbumProblem", back_populates="album", cascade="all, delete-orphan")
    songs = relationship("klap4.db_entities.song.Song", back_populates="album", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"])
            kwargs["artist_id"] = find_artist_id(decomposed_tag.genre_abbr, decomposed_tag.artist_num)

            if decomposed_tag.album_letter is not None:
                kwargs["letter"] = decomposed_tag.album_letter

            kwargs.pop("id")

        if "letter" not in kwargs:
            from klap4.db_entities import get_entity_from_tag
            artist = get_entity_from_tag(f"{kwargs['genre_abbr']}{kwargs['artist_num']}")
            kwargs["letter"] = artist.next_album_letter

        defaults = {
            "date_added": datetime.now(),
            "missing": False,
        }
        kwargs = {**defaults, **kwargs}

        super().__init__(**kwargs)

    @property
    def is_new(self):
        return datetime.now() - self.date_added < timedelta(days=30 * 6)
    
    @property
    def next_review_id(self):
        return len(self.reviews) + 1
    
    @property
    def next_problem_id(self):
        return len(self.problems) + 1

    @property
    def total_plays(self):
        sum = 0
        for song in self.songs:
            sum = sum + song.times_played
        
        return sum

    @property
    def ref(self):
        return self.artist.ref + self.letter
    

    def serialize(self):
        review_list = []
        problem_list = []
        song_list = []
        for review in self.reviews:
            review_list.append({
                                 "date_entered": str(review.date_entered),
                                 "reviewer": review.dj_id,
                                 "review": review.content
                                })
        for problem in self.problems:
            problem_list.append({
                                 "reporter": problem.dj_id,
                                 "problem": problem.content
                                })
        for song in self.songs:
            song_list.append({
                              "ref": song.ref,
                              "number": song.number,
                              "song_name": song.name,
                              "fcc_status": song.fcc_status,
                              "times_played": song.times_played,
                              "last_played": str(song.last_played),
                              "recommended": song.recommended
                            })

        serialized_album = {
                            "id": self.ref,
                            "name": self.name,
                            "artist_id": self.artist.ref,
                            "artist": self.artist.name,
                            "genre": self.artist.genre.name,
                            "label": None if self.label_id is None else self.label.name,
                            "promoter": None if self.promoter_id is None else self.promoter.name,  
                            "date_added": str(self.date_added),
                            "format": self.format_bitfield,
                            "missing": self.missing,
                            "new_album": self.is_new,
                            "reviews": review_list,
                            "problems": problem_list,
                            "songs": song_list,
                            "image": getAlbumCover(self.name, self.artist.name)
                            }
        return serialized_album


    def __repr__(self):
        return f"<Album(ref={self.ref}, " \
                      f"name={self.name}, " \
                      f"date_added={self.date_added}, " \
                      f"missing={self.missing}, " \
                      f"is_new={self.is_new}, " \
                      f"format={self.format_bitfield}, " \
                      f"label_id={self.label_id}, " \
                      f"promoter_id={self.promoter_id})>"
    
    def __str__(self):
        return str(self.name)


class AlbumReview(SQLBase):
    __tablename__ = "album_review"

    id = Column(Integer, primary_key=True)
    album_id = Column(Integer, ForeignKey("album.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    dj_id = Column(String, ForeignKey("dj.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    date_entered = Column(DateTime, nullable=False)
    content = Column(String, nullable=False)
    
    album = relationship("klap4.db_entities.album.Album", back_populates="reviews")
    dj = relationship("klap4.db_entities.dj.DJ", back_populates="reviews")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"])
            ref_album = find_album(decomposed_tag.genre_abbr, decomposed_tag.artist_num, decomposed_tag.album_letter)
            kwargs["album_id"] = ref_album.id

            kwargs["id"] = ref_album.next_review_id

        if "date_entered" not in kwargs:
            kwargs["date_entered"] = datetime.now()
        super().__init__(**kwargs)

    @property
    def is_recent(self):
        return datetime.now() - self.date_entered < timedelta(weeks=4)

    @property
    def ref(self):
        return self.album.ref + '-R' + str(self.id)
    

    @property
    def serialize(self):
        serialized_review = {
                              "ref": self.ref,
                              "album": self.album.name,
                              "date_entered": str(self.date_entered),
                              "reviewer": self.dj_id,
                              "content": self.content
                            }
        return serialized_review

    def __repr__(self):
        return f"<AlbumReview(ref={self.ref}, " \
                            f"date_entered={self.date_entered}, " \
                            f"is_recent={self.is_recent}, " \
                            f"content={self.content[:20] + '...' if len(self.content) > 20 else self.content})>"


class AlbumProblem(SQLBase):
    __tablename__ = "album_problem"

    id = Column(Integer, primary_key=True)
    album_id = Column(Integer, ForeignKey("album.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    dj_id = Column(String, ForeignKey("dj.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    
    album = relationship("klap4.db_entities.album.Album", back_populates="problems")
    dj = relationship("klap4.db_entities.dj.DJ", back_populates="problems")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"])
            ref_album = find_album(decomposed_tag.genre_abbr, decomposed_tag.artist_num, decomposed_tag.album_letter)
            kwargs["album_id"] = ref_album.id

            kwargs["id"] = ref_album.next_problem_id
        super().__init__(**kwargs)


    @property
    def ref(self):
        return f"{self.album.ref}-P{self.id}"

    
    def __repr__(self):
        return f"<AlbumProblem(ref={self.ref}, " \
                             f"content={self.content[:20] + '...' if len(self.content) > 20 else self.content})>"
