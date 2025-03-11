from F_taste_richieste.models.richiesta_aggiunta_paziente import RichiestaAggiuntaPazienteModel
from F_taste_richieste.models.richiesta_revocata import RichiestaRevocataModel
from datetime import datetime
from F_taste_richieste.db import get_session

class RichiestaAggiuntaPazienteRepository:

    @staticmethod
    def add(richiesta, session=None):
        session = session or get_session('patient')
        session.add(richiesta)
        session.commit()

    @staticmethod
    def find_new_requests(id_paziente, session=None):
        session = session or get_session('patient')
        return session.query(RichiestaAggiuntaPazienteModel).filter_by(id_paziente=id_paziente, accettata=False).all()

    @staticmethod
    def find_by_id_paziente_and_id_nutrizionista(id_paziente, id_nutrizionista, session=None):
        session = session or get_session('patient')
        return session.query(RichiestaAggiuntaPazienteModel).filter_by(id_paziente=id_paziente, id_nutrizionista=id_nutrizionista).first()

    @staticmethod
    def find_active_request(id_paziente, session=None):
        session = session or get_session('patient')
        return session.query(RichiestaAggiuntaPazienteModel).filter_by(id_paziente=id_paziente, accettata=True).first()

    @staticmethod
    def delete_request(richiesta, session=None):
        session = session or get_session('patient')
        session.delete(richiesta)
        session.commit()

    #da rimuovere, è uguale a add
    @staticmethod
    def save_richiesta(richiesta, session=None):
        session = session or get_session('patient')
        session.add(richiesta)
        session.commit()

    @staticmethod
    def create_richiesta_revocata(paziente, richiesta, email_nutrizionista,session=None):
        session = session or get_session('patient')
        richiesta_revocata = RichiestaRevocataModel(paziente.id_paziente, email_nutrizionista, richiesta.data_richiesta, richiesta.data_accettazione)
        session.add(richiesta_revocata)
        session.commit()