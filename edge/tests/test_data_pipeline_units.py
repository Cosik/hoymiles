import pytest
from hoymiles.data_pipeline import (
    CalculatedFieldTransformer,
    DataPipeline,
    FilterKeysTransformer,
    FilterNullTransformer,
    RenameKeysTransformer,
    RoundTransformer,
    ScaleTransformer,
    TypeCastTransformer,
)


def test_filter_keys_transformer():
    data = {"a": 1, "b": 2, "c": 3}
    tf = FilterKeysTransformer(["a", "c"])
    assert tf.transform(data) == {"a": 1, "c": 3}


def test_rename_keys_transformer():
    data = {"old": 1, "stay": 2}
    tf = RenameKeysTransformer({"old": "new"})
    assert tf.transform(data) == {"new": 1, "stay": 2}


def test_type_cast_transformer():
    data = {"i": "1", "f": "1.5", "n": None}
    tf = TypeCastTransformer({"i": int, "f": float, "n": int})
    res = tf.transform(data)
    assert res["i"] == 1
    assert res["f"] == 1.5
    assert res["n"] is None

    with pytest.raises(ValueError, match="Cannot cast"):
        tf.transform({"i": "not_int"})


def test_scale_transformer():
    data = {"val": 10, "str": "no"}
    tf = ScaleTransformer({"val": 0.5, "str": 2})
    assert tf.transform(data) == {"val": 5.0, "str": "no"}


def test_round_transformer():
    data = {"val": 1.23456}
    tf = RoundTransformer({"val": 2})
    assert tf.transform(data) == {"val": 1.23}


def test_calculated_field_transformer():
    data = {"a": 10, "b": 2}
    tf = CalculatedFieldTransformer({"sum": lambda d: d["a"] + d["b"]})
    assert tf.transform(data)["sum"] == 12

    tf_err = CalculatedFieldTransformer({"err": lambda d: d["non_existent"]})
    with pytest.raises(ValueError, match="Error calculating err"):
        tf_err.transform(data)


def test_filter_null_transformer():
    data = {"a": 1, "b": None, "c": "", "d": 0}
    tf = FilterNullTransformer(keep_zero=True)
    assert tf.transform(data) == {"a": 1, "d": 0}

    tf2 = FilterNullTransformer(keep_zero=False)
    assert tf2.transform(data) == {"a": 1}


def test_data_pipeline_execution():
    pipeline = DataPipeline()
    pipeline.add_transformer(TypeCastTransformer({"a": int}))
    pipeline.add_transformer(ScaleTransformer({"a": 2}))
    assert pipeline.execute({"a": "5"}) == {"a": 10}


def test_data_pipeline_validation_fail():
    pipeline = DataPipeline()
    pipeline.add_transformer(CalculatedFieldTransformer({"x": lambda d: d["y"]}))
    with pytest.raises(ValueError, match="Error calculating x"):
        pipeline.execute({"z": 1})
