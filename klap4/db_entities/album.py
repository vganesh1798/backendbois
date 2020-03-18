#!/usr/bin/env python3

from datetime import datetime

from sqlalchemy import Column, ForeignKey, Boolean, DateTime, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class Album(SQLBase):
    __tablename__ = "album"

    class FORMAT:
        VINYL = 1 * 2 ** 0
        CD = 1 * 2 ** 1
        DIGITAL = 1 * 2 ** 2

    genre_abbr = Column(String(2), ForeignKey("genre.abbreviation"), primary_key=True)
    artist_num = Column(Integer, ForeignKey("artist.number"), primary_key=True)
    letter = Column(String(1), primary_key=True)
    name = Column(String, nullable=False)
    date_added = Column(DateTime, nullable=False)
    missing = Column(Boolean, nullable=False)
    format_bitfield = Column(Integer, nullable=False)
    label_id = Column(Integer, ForeignKey("label.id"), nullable=True)
    promoter_id = Column(Integer, ForeignKey("promoter.id"), nullable=True)

    genre = relationship("klap4.db_entities.genre.Genre", back_populates="albums")
    artist = relationship("klap4.db_entities.artist.Artist", back_populates="albums")
    label = relationship("klap4.db_entities.label_and_promoter.Label", back_populates="artists")
    promoter = relationship("klap4.db_entities.label_and_promoter.Promoter", back_populates="artists")
    album_reviews = relationship("klap4.db_entities.album.AlbumReview", back_populates="album")

    is_new = False
    id = None

    def __init__(self, **kwargs):
        if "id" in kwargs:
            kwargs["genre_abbr"] = kwargs["id"][:2]
            kwargs["artist_num"] = int(kwargs["id"][2:-1])

            if kwargs["id"][-1].isdigit():
                try:
                    kwargs.pop("letter")
                except KeyError:
                    pass
            else:
                kwargs["letter"] = kwargs["id"][-1]

        if "letter" not in kwargs:
            kwargs["letter"] = self.artist.next_album_letter

        defaults = {
            "date_added": datetime.now(),
            "missing": False,
        }
        kwargs = {**defaults, **kwargs}

        super().__init__(**kwargs)

    @property
    def is_new(self):
        # TODO: Determine thresh hold to determine if an album is new.
        return False

    @property
    def id(self):
        return self.artist.id + self.letter

    def __repr__(self):
        return f"<Album(id={self.id}, " \
                      f"{self.name=}, " \
                      f"{self.date_added=}, " \
                      f"{self.missing=}, " \
                      f"{self.is_new=}, " \
                      f"format={self.format_bitfield}, " \
                      f"{self.label_id=}, " \
                      f"{self.promoter_id=})>"


class AlbumReview(SQLBase):
    __tablename__ = "album_review"

    genre_abbr = Column(String(2), ForeignKey("genre.abbreviation"), primary_key=True)
    artist_num = Column(Integer, ForeignKey("artist.number"), primary_key=True)
    album_letter = Column(String(1), ForeignKey("album.letter"), primary_key=True)
    dj_id = Column(Integer, primary_key=True)
    date_entered = Column(DateTime, nullable=False)
    content = Column(String, nullable=False)

    genre = relationship("klap4.db_entities.genre.Genre", back_populates="album_reviews")
    artist = relationship("klap4.db_entities.artist.Artist", back_populates="album_reviews")
    album = relationship("klap4.db_entities.album.Album", back_populates="album_reviews")

    is_recent = False
    id = False

    def __init__(self, **kwargs):
        if "date_entered" in kwargs:
            kwargs["date_entered"] = datetime.now()
        super().__init__(**kwargs)

    @property
    def is_recent(self):
        # TODO: Determine thresh hold to determine if a review is recent.
        return False

    @property
    def id(self):
        return self.album.id + str(self.dj_id)

    def __repr__(self):
        return f"<AlbumReview(id={self.id}, " \
                            f"{self.date_entered=}, " \
                            f"{self.is_recent=}, " \
                            f"content={self.content[:20] + '...' if len(self.content) > 20 else self.message})>"