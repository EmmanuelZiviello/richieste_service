from F_taste_richieste.repositories.richieste_repository import RichiestaAggiuntaPazienteRepository
from F_taste_richieste.db import get_session
from F_taste_richieste.kafka.kafka_producer import send_kafka_message
from F_taste_richieste.utils.kafka_helpers import wait_for_kafka_response
from F_taste_richieste.models.richiesta_aggiunta_paziente import RichiestaAggiuntaPazienteModel
from F_taste_richieste.schemas.richiesta_aggiunta_paziente import RichiestaAggiuntaPazienteSchema

richiesta_schema_for_dump = RichiestaAggiuntaPazienteSchema()


class RichiesteService:

    
    @staticmethod
    def add(s_richiesta):
        if "id_paziente" not in s_richiesta or "id_nutrizionista" not in s_richiesta:
            return {"status_code":"400"}, 400
            #return {"esito add_richiesta":"Dati mancanti"}, 400
        session=get_session('dietitian')
        id_paziente=s_richiesta["id_paziente"]
        id_nutrizionista=s_richiesta["id_nutrizionista"]
        richiesta=RichiestaAggiuntaPazienteRepository.find_by_id_paziente_and_id_nutrizionista(id_paziente,id_nutrizionista,session)
        if richiesta is not None:
            session.close()
            return {"status_code":"403"}, 403
            #return {"message": "richiesta già presente"}, 403
    
        richiesta=RichiestaAggiuntaPazienteModel(id_paziente,id_nutrizionista)
        RichiestaAggiuntaPazienteRepository.add(richiesta,session)
        session.close()
        return {"status_code":"200"}, 200
        #return {"message": "richiesta aggiunta a propria lista pazienti inviata con successo"}, 200

    @staticmethod
    def get_richieste_utente(id_paziente):
        session=get_session('patient')
        richieste=RichiestaAggiuntaPazienteRepository.find_new_requests(id_paziente)
        if richieste is None:
            session.close()
            return {"message":"Richieste non presenti nel database"},400
        output_richiesta=richiesta_schema_for_dump.dump(richieste,many=True), 200
        session.close()
        return output_richiesta