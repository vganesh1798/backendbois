#!/usr/bin/env python3

from datetime import *

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Time, Table
from sqlalchemy.orm import backref, relationship

import klap4.db
from klap4.db_entities import SQLBase


class ProgramFormat(SQLBase):
    __tablename__ = "program_format"

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)

    programs = relationship("klap4.db_entities.program.Program", back_populates="program_format", cascade="all, delete-orphan")
    
    program_slots = relationship("klap4.db_entities.program.ProgramSlot", back_populates="program_format", uselist=True,
                                 cascade="all, delete-orphan")

    program_log_entries = relationship("ProgramLogEntry", back_populates="program_format")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def serialize(self):
        serialized_program = {
                              "type": self.type,
                              "description": self.description
                             }
        return serialized_program
    
    def __repr__(self):
        return f"<Program(type={self.type}, " \
                        f"description={self.description})>"
    
    def __str__(self):
        return str(self.type)


class Program(SQLBase):
    __tablename__ = "program"

    id = Column(Integer, primary_key=True)
    format_id = Column(Integer, ForeignKey("program_format.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    name = Column(String, nullable=False, unique=True)
    duration = Column(Time, nullable=True)
    months = Column(String, nullable=True)

    program_format = relationship("klap4.db_entities.program.ProgramFormat", back_populates="programs")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def ref(self):
        return str(self.program_format.type)+'-'+str(self.name)
    

    def serialize(self):
        serialized_program = {
                              "type": self.program_format.type,
                              "name": self.name,
                              "duration": str(self.duration),
                              "months": self.months
                             }
        return serialized_program
    
    def __repr__(self):
        return f"<Program(type={self.program_format.type}, " \
                        f"name={self.name}, " \
                        f"months={self.months})>"
    
    def __str__(self):
        return str(self.name)


class ProgramSlot(SQLBase):
    __tablename__ = "program_slot"

    id = Column(Integer, primary_key=True)
    program_type = Column(String, ForeignKey("program_format.type"), nullable=False)
    day = Column(Integer)
    time = Column(Time)

    program_format = relationship("klap4.db_entities.program.ProgramFormat", back_populates="program_slots")

    program_log_entries = relationship("ProgramLogEntry", back_populates="program_slot", uselist=False,
                                       cascade="all, delete-orphan",
                                       primaryjoin="and_(ProgramLogEntry.program_type == ProgramSlot.program_type,"
                                                    "ProgramLogEntry.slot_id == ProgramSlot.id"
                                                    ")")
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<ProgramSlot(program_type={self.program_type}, " \
                            f"day={self.day}, " \
                            f"time={self.time})>"
    
    def __str__(self):
        return str(self.program_type)+ '+' + str(self.day) + '+' + str(self.time)


class ProgramLogEntry(SQLBase):
    __tablename__ = "program_log_entry"

    program_type = Column(String, ForeignKey("program_format.type"), primary_key=True)
    program_name = Column(String, nullable=False)
    slot_id = Column(Integer, ForeignKey("program_slot.id"), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    dj_id = Column(String, ForeignKey("dj.id"), nullable=False)

    program_format = relationship("ProgramFormat", back_populates="program_log_entries")
    program_slot = relationship("ProgramSlot", back_populates="program_log_entries", uselist=True)

    dj = relationship("klap4.db_entities.dj.DJ", backref=backref("program_log_entries", uselist=True, cascade="all, delete-orphan"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    

    @property
    def id(self):
        return str(self.program_type) + str(self.slot_id) + str(self.timestamp)

    def serialize(self):
        serialized_program = {
            "program_type": self.program_type,
            "program_name": self.program_name,
            "slot_id": self.slot_id,
            "timestamp": self.timestamp,
            "dj_id": self.dj_id
        }        

        return serialized_program

    def __repr__(self):
        return f"<ProgramLogEntry(program_type={self.program_type}, " \
                                f"program_name={self.program_name}, " \
                                f"timestamp={self.timestamp}, " \
                                f"dj={self.dj_id})>"


class Quarter(SQLBase):
    __tablename__ = "quarter"

    id = Column(Integer, primary_key=True)
    begin = Column(DateTime, primary_key=True)
    end = Column(DateTime, primary_key=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<Quarter(id={self.id}, " \
                    f"begin={self.begin}, " \
                    f"end={self.end})>"
