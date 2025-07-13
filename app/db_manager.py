from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random

class DatabaseManager:
    def __init__(self, config):
        self.config = config
        if getattr(config, 'TESTING', False):
            # Use SQLite for testing
            self.write_engine = create_engine(f'sqlite:///{config.TEST_DB}', pool_pre_ping=True)
            self.WriteSession = sessionmaker(bind=self.write_engine)
            self.read_engines = [self.write_engine]
            self.ReadSessions = [self.WriteSession]
        else:
            # Create the write engine using primary host
            self.write_engine = self._create_engine(
                host=config.POSTGRES_PRIMARY_HOST,
                port=config.POSTGRES_PORT,
                user=config.POSTGRES_USER,
                password=config.POSTGRES_PASSWORD,
                dbname=config.POSTGRES_DB,
            )
            self.WriteSession = sessionmaker(bind=self.write_engine)

            self.read_engines = self._create_read_engines()
            self.ReadSessions = [sessionmaker(bind=engine) for engine in self.read_engines]

    def _create_engine(self, host, port, user, password, dbname):
        uri = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        return create_engine(uri, pool_pre_ping=True)

    def _create_read_engines(self):
        engines = []
        for rep_num in range(int(self.config.READ_REPLICAS)):
            engine = self._create_engine(
                host=f'{self.config.POSTGRES_REPLICA_HOST}-{rep_num}',
                port=self.config.POSTGRES_PORT,
                user=self.config.POSTGRES_USER,
                password=self.config.POSTGRES_PASSWORD,
                dbname=self.config.POSTGRES_DB,
            )
            engines.append(engine)
        return engines

    def get_write_session(self):
        return self.WriteSession()

    def get_read_session(self):
        if not self.ReadSessions:
            return self.get_write_session()  # fallback
        return random.choice(self.ReadSessions)()
