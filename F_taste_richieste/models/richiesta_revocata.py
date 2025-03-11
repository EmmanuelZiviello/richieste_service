from datetime import datetime
from F_taste_richieste.db import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP

class RichiestaRevocataModel(Base):
    __tablename__ = "richiesta_revocata"

    id_richiesta = Column(Integer, primary_key=True)
    data_richiesta = Column(TIMESTAMP, nullable=False)
    data_accettazione = Column(TIMESTAMP, nullable=True)
    data_revoca = Column(TIMESTAMP, nullable=True)
    
    email_nutrizionista = Column(String(45), nullable=False)  
    id_paziente = Column(String(7), nullable=False)  # Ex ForeignKey

    def __init__(self, id_paziente, email_nutrizionista, data_richiesta, data_accettazione):
        self.id_paziente = id_paziente
        self.email_nutrizionista = email_nutrizionista
        self.data_richiesta = data_richiesta
        self.data_accettazione = data_accettazione
        self.data_revoca = datetime.now()

    def __repr__(self):
        return "RichiestaRevocataModel(id_paziente=%r, email_nutrizionista=%r, data_richiesta=%r, data_accettazione=%r, data_revoca=%r)" % (
            self.id_paziente, self.email_nutrizionista, self.data_richiesta, self.data_accettazione, self.data_revoca
        )

    def __json__(self):
        return {
            "id_paziente": self.id_paziente,
            "email_nutrizionista": self.email_nutrizionista,
            "data_richiesta": self.data_richiesta,
            "data_accettazione": self.data_accettazione,
            "data_revoca": self.data_revoca,
        }

    @classmethod
    def find_by_id_paziente_and_email_nutrizionista(cls, id_paziente, email_nutrizionista, session) -> "RichiestaRevocataModel":
        return session.query(cls).filter_by(id_paziente=id_paziente, email_nutrizionista=email_nutrizionista).first()

    @classmethod
    def find_by_id_paziente(cls, id_paziente, session) -> list["RichiestaRevocataModel"]:
        return session.query(cls).filter_by(id_paziente=id_paziente).all()
