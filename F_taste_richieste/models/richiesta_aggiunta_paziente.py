from datetime import datetime
from F_taste_richieste.db import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, UniqueConstraint

class RichiestaAggiuntaPazienteModel(Base):
    __tablename__ = "richiesta_aggiunta_paziente"

    id_richiesta = Column(Integer, primary_key=True)
    accettata = Column(Boolean, default=False)
    data_richiesta = Column(TIMESTAMP, nullable=False)
    data_accettazione = Column(TIMESTAMP, nullable=True)
    id_nutrizionista = Column(Integer, nullable=False)  # Ex fk_nutrizionista
    id_paziente = Column(String(10), nullable=False)  # Ex fk_paziente

    __table_args__ = (
        UniqueConstraint(id_paziente, id_nutrizionista, name="one_request_for_each_patient_by_a_nutritionist"),
    )

    def __repr__(self):
        return "RichiestaAggiuntaPazienteModel(id_paziente:%s, id_nutrizionista:%s, accettata:%s, data_richiesta:%s, data_accettazione:%s)" % (
            self.id_paziente, self.id_nutrizionista, self.accettata, self.data_richiesta, self.data_accettazione
        )

    def __json__(self):
        return {
            'id_paziente': self.id_paziente,
            'id_nutrizionista': self.id_nutrizionista,
            'accettata': self.accettata,
            'data_richiesta': self.data_richiesta,
            'data_accettazione': self.data_accettazione
        }

    def __init__(self, id_paziente, id_nutrizionista):
        self.id_paziente = id_paziente
        self.id_nutrizionista = id_nutrizionista
        self.accettata = False
        self.data_richiesta = datetime.now()
  
