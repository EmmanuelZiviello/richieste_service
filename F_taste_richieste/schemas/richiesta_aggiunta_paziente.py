from F_taste_richieste.ma import ma
from F_taste_richieste.models.richiesta_aggiunta_paziente import RichiestaAggiuntaPazienteModel
from marshmallow import fields

class RichiestaAggiuntaPazienteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RichiestaAggiuntaPazienteModel
        load_instance = True
        include_relationships = False  # Disabilita automaticamente le relazioni

    id_nutrizionista = fields.Integer(dump_only=True)  # Ex nutrizionista Nested
    id_paziente = fields.String(dump_only=True)
    accettata = fields.Boolean()
    data_richiesta = fields.DateTime()
    data_accettazione = fields.DateTime(allow_none=True)
