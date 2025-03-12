from datetime import datetime
from F_taste_richieste.repositories.richieste_repository import RichiestaAggiuntaPazienteRepository
from F_taste_richieste.db import get_session
from F_taste_richieste.kafka.kafka_producer import send_kafka_message
from F_taste_richieste.utils.kafka_helpers import wait_for_kafka_response
from F_taste_richieste.models.richiesta_aggiunta_paziente import RichiestaAggiuntaPazienteModel
from F_taste_richieste.models.richiesta_revocata import RichiestaRevocataModel
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
    
    @staticmethod
    def gestisci_richiesta(id_paziente,id_nutrizionista,conferma):
            session=get_session('patient')
            richiesta=RichiestaAggiuntaPazienteRepository.find_by_id_paziente_and_id_nutrizionista(id_paziente,id_nutrizionista,session)
            if richiesta is None:
                    session.close()
                    return {'message' : 'richiesta non trovata'}, 400
            
            if conferma == True:
                if not richiesta.accettata:
                    if RichiestaAggiuntaPazienteRepository.find_active_request(id_paziente,session) is not None:
                            session.close()
                            return {'message' : 'Non puoi accettare una richiesta senza revocare la precedente'}, 403
                    richiesta.accettata=True
                    richiesta.data_accettazione = datetime.now()
                    richiesta.id_paziente=id_paziente
                    #viene mandato via kafka una notifica al servizio paziente che deve aggiornare id_nutrizionista
                    #e in base al valore del messaggio status_code:codice capisce se può continuare o meno con l'aggiungere nel db la richiesta
                    message={"id_paziente":id_paziente,"id_nutrizionista":id_nutrizionista}
                    send_kafka_message("patient.updateFk.request",message)
                    response = wait_for_kafka_response(["patient.updateFk.success", "patient.updateFk.failed"])
                    #controllo sul valore in response per capire se si può aggiornare il db
                    if response is None:
                        session.close()
                        return {"message": "Errore nella comunicazione con Kafka"}, 500
                    
                    if response.get("status_code") == "200":
                        RichiestaAggiuntaPazienteRepository.add(richiesta,session)
                        session.close()
                        return {"message": "richiesta accettata con successo"}, 200
                    elif response.get("status_code") == "500":
                         session.close()
                         return {"message": "Errore nella comunicazione con Kafka"}, 500
                    elif response.get("status_code") == "400":
                         session.close()
                         return {"message": "Dati mancanti per aggiornare il paziente ed il suo nutrizionista"}, 400
                    elif response.get("status_code") == "404":
                         session.close()
                         return {"message": "Paziente o nutrizionista non presenti nel database"}, 404
                    
                    
                    
                    
                session.close()
                return {'message' : 'richiesta gia accettata'}, 403
            elif conferma == False:
                if not richiesta.accettata:
                    RichiestaAggiuntaPazienteRepository.delete_request(richiesta,session)
                    session.close()
                    return {"message": "richiesta rifiutata con successo"}, 200
                session.close()
                return {'message' : 'non puoi rifiutare una richiesta gia accettata'}, 403
    
                  
    @staticmethod
    def revoca_condivisione(id_paziente):
         session=get_session('patient')
         richiesta=RichiestaAggiuntaPazienteRepository.find_active_request(id_paziente,session)
         if richiesta is None:
            session.close()
            return {'message' : 'richiesta non trovata'}, 404
         else:
              message={"id_paziente":id_paziente}
              send_kafka_message("patient.removeFk.request",message)
              response = wait_for_kafka_response(["patient.removeFk.success", "patient.removeFk.failed"])
              #controllo sul valore in response per capire se si può aggiornare il db
              if response is None:
                    session.close()
                    return {"message": "Errore nella comunicazione con Kafka"}, 500
              
              if response.get("status_code") == "200":
                   email_nutrizionista = response.get("email_nutrizionista")
                   if email_nutrizionista:
                         richiesta_revocata = RichiestaRevocataModel(id_paziente, email_nutrizionista, richiesta.data_richiesta, richiesta.data_accettazione)
                         RichiestaAggiuntaPazienteRepository.add(richiesta_revocata,session)
                         RichiestaAggiuntaPazienteRepository.delete_request(richiesta,session)
                         session.close()
                         return {"message": "richiesta revocata con successo"}, 204
                   session.close()
                   return {"message":"email nutrizionista non ottenuta in modo corretto"}, 400 
              elif response.get("status_code") == "500":
                         session.close()
                         return {"message": "Errore nella comunicazione con Kafka"}, 500
              elif response.get("status_code") == "400":
                         session.close()
                         return {"message": "Dati mancanti per aggiornare il paziente ed il suo nutrizionista"}, 400
              elif response.get("status_code") == "404":
                         session.close()
                         return {"message": "Paziente o nutrizionista non presenti nel database"}, 404
              
              