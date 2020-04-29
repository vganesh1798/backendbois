from flask import request, jsonify
from flask_restful import Resource

from klap4.services.song_services import change_single_fcc, change_album_fcc

class SongAPI(Resource):
    def put(self, ref, typ):
        json_data = request.get_json(force=True)
        try:
            fcc = json_data['fcc']
            if typ == 'single':
                song_number = json_data['song_number']
                change_single_fcc(ref, song_number, fcc)
            elif typ == 'all':
                update = change_album_fcc(ref, fcc)
            
            return "Updated"
        except:
            return jsonify({"error": "Bad request"}), 400