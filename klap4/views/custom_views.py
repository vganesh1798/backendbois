from flask_admin.contrib.sqla import ModelView

class GenreModelView(ModelView):
    column_list=['abbreviation', 'name', 'color']
    form_columns = ('abbreviation', 'name', 'color')


class ArtistModelView(ModelView):
    column_list=['name', 'genre', 'number']
    form_columns = ('genre', 'name', 'number')


class AlbumModelView(ModelView):
    column_list=['name', 'artist', 'date_added', 'missing', 'format_bitfield']
    form_columns = ('artist', 'letter', 'name', 'date_added', 'missing', 'format_bitfield', 'label_id', 'promoter_id')


class AlbumReviewModelView(ModelView):
    column_display_pk = True
    column_list = ['id', 'album', 'dj_id', 'date_entered', 'content']


class AlbumProblemModelView(ModelView):
    column_list = ['id', 'album', 'dj_id', 'content']


class SongModelView(ModelView):
    column_list = ['name', 'album']


class ProgramFormatModelView(ModelView):
    column_display_pk = True
    form_columns = ['type', 'description']


class ProgramModelView(ModelView):
    column_display_pk = True
    form_columns = ('id', 'program_format', 'name', 'duration', 'months')


class ProgramSlotModelView(ModelView):
    column_display_pk = True
    form_columns = ('program_format', 'day', 'time')


class ProgramLogEntryModelView(ModelView):
    column_display_pk = True
    form_columns = ('program_format', 'program_name', 'program_slot', 'timestamp', 'dj')


class PlaylistModelView(ModelView):
    column_display_pk = True
    form_columns = ('dj_id', 'name', 'show')


class PlaylistEntryModelView(ModelView):
    column_display_pk = True
    form_columns = ('playlist', 'index', 'reference_type', 'reference', 'entry')

class DJModelView(ModelView):
    column_display_pk = True
    form_columns = ('id', 'name', 'is_admin')