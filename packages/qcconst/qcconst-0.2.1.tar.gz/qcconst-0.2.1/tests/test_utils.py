from qcconst.utils import to_table


def test_no_data():
    to_table([]) == "No data to display."
