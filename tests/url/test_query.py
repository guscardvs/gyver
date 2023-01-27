from gyver.url.query import Query


def test_query():  # sourcery skip: extract-duplicate-method

    # Test query load
    query = Query("param1=value1&param2=value2")
    assert query.params == {"param1": ["value1"], "param2": ["value2"]}

    # Test query encode
    query = Query("param1=value1&param2=value2")
    assert query.encode() == "param1=value1&param2=value2"

    # Test query no null equal returns empty param
    query = Query("param1=&param2=value2")
    assert query.omit_empty_equal() == "param1&param2=value2"

    # Test query adds correctly
    query = Query("param1=value1&param2=value2")
    query.add(param3="value3")
    assert query.params == {
        "param1": ["value1"],
        "param2": ["value2"],
        "param3": ["value3"],
    }

    # Test query set adds correctly
    query = Query("param1=value1&param2=value2")
    query.set(param3="value3")
    assert query.params == {"param3": ["value3"]}

    # Test setitem works correctly
    query = Query("param1=value1&param2=value2")
    query["param3"] = "value3"
    assert query.params == {
        "param1": ["value1"],
        "param2": ["value2"],
        "param3": ["value3"],
    }

    # Test getitem works correctly
    query = Query("param1=value1&param2=value2")
    assert query["param1"] == ["value1"]

    # Test removing a single parameter
    q = Query("param1=value1&param2=value2")
    q.remove("param1")
    assert q.encode() == "param2=value2"

    # Test removing multiple parameters at once
    q = Query("param1=value1&param2=value2&param3=value3")
    q.remove("param1", "param3")
    assert q.encode() == "param2=value2"

    # Test removing a non-existent parameter
    q = Query("param1=value1")
    q.remove("param2")
    assert q.encode() == "param1=value1"

    # Test sorting multiple parameters
    q = Query("param2=value2&param1=value1&param3=value3")
    q.sort()
    assert q.encode() == "param1=value1&param2=value2&param3=value3"

    # Test sorting a single parameter
    q = Query("param1=value1")
    q.sort()
    assert q.encode() == "param1=value1"

    # Test sorting with multiple values
    q = Query("param1=value1&param1=value2&param2=value3")
    q.sort()
    assert q.encode() == "param1=value1&param1=value2&param2=value3"
