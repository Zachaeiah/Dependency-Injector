from src.di_container import Container, Inject

# -------------------------
# Interfaces / Base types
# -------------------------
class ILogger:
    def log(self, msg: str):
        raise NotImplementedError()


class IDatabase:
    def query(self, sql: str):
        raise NotImplementedError()


# -------------------------
# Implementations
# -------------------------
class ConsoleLogger(ILogger):
    def log(self, msg: str):
        print(f"[LOG]: {msg}")


class FileLogger(ILogger):
    def __init__(self):
        self.file = "log.txt"

    def log(self, msg: str):
        print(f"[FILE:{self.file}] {msg}")


class MySQLDatabase(IDatabase):
    def __init__(self, logger: ILogger):
        self.logger = logger

    def query(self, sql: str):
        self.logger.log(f"MySQL executing: {sql}")


class PostgresDatabase(IDatabase):
    def __init__(self, logger: ILogger = Inject(ILogger, "file")):
        self.logger = logger

    def query(self, sql: str):
        self.logger.log(f"Postgres executing: {sql}")


# -------------------------
# Business Layer
# -------------------------
class UserRepository:
    def __init__(self, db: IDatabase):
        self.db = db

    def get_user(self, user_id: int):
        self.db.query(f"SELECT * FROM users WHERE id={user_id}")


class UserService:
    def __init__(self, repo: UserRepository, logger: ILogger):
        self.repo = repo
        self.logger = logger

    def process(self):
        self.logger.log("Processing user request...")
        self.repo.get_user(42)


# -------------------------
# Factory Example
# -------------------------
def special_logger_factory():
    logger = ConsoleLogger()
    logger.log("Factory created logger")
    return logger


# -------------------------
# Demo
# -------------------------
def main():
    c = Container()

    # -------------------------
    # Register multiple providers
    # -------------------------
    c.register(ILogger, ConsoleLogger, singleton=True)              # default logger
    c.register(ILogger, FileLogger, singleton=True, name="file")    # named logger

    # -------------------------
    # Register DB implementations
    # -------------------------
    c.register(IDatabase, MySQLDatabase)        # default DB
    c.register(IDatabase, PostgresDatabase, name="pg")

    # -------------------------
    # Register factory
    # -------------------------
    c.register(ILogger, special_logger_factory, name="factory")

    # -------------------------
    # Resolve full dependency graph
    # -------------------------
    service = c.resolve(UserService)
    service.process()

    print("\n--- Named resolution ---")
    pg_db = c.resolve(IDatabase, name="pg")
    pg_db.query("SELECT NOW()")

    print("\n--- Factory resolution ---")
    factory_logger = c.resolve(ILogger, name="factory")
    factory_logger.log("Hello from factory")

    # -------------------------
    # Scoped container example
    # -------------------------
    print("\n--- Scoped container ---")
    scoped = c.create_scope()

    # override logger in scope only
    scoped.register(ILogger, FileLogger, singleton=True)

    scoped_service = scoped.resolve(UserService)
    scoped_service.process()

    # -------------------------
    # Validation
    # -------------------------
    print("\n--- Validation ---")
    errors = c.validate(fail_fast=False)
    if not errors:
        print("Container is valid")
    else:
        for e in errors:
            print(e)


if __name__ == "__main__":
    main()