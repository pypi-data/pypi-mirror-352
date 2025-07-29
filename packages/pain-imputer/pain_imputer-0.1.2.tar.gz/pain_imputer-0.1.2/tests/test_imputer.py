from pain_imputer.imputer import PAINImputer

def test_imputer_initialization():
    imputer = PAINImputer()
    assert imputer is not None