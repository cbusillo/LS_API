from sqlmodel import SQLModel, create_engine


sqlite_file_name = 'shiny.sqlite3'
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# "**/site-packages/**/*.py",
# ".vscode/*.py",
# "/**/*.pyi",
# "/opt/**/**",
# "shiny_api_old/**"