from gyver import database


def test_make_uri_should_return_expected_uri():
    expected = "mysql+aiomysql://user:Pas%24word@localhost:3306/database_name"
    config = database.DefaultDatabaseConfig(
        driver=database.types.Driver.MYSQL,
        host="localhost",
        user="user",
        password="Pas$word",
        name="database_name",
    )

    assert database.make_uri(config, False) == expected
