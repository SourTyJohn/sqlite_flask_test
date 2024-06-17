from os.path import abspath, dirname, join


ROOT = dirname( abspath(__name__) )
DB_PATH = join(
    join(ROOT, "data"), "global.db"
)
