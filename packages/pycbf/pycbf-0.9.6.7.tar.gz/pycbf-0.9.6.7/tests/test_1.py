from pathlib import Path

import pycbf

DATA_DIR = Path(__file__).parent.parent / "data"


def test_1(dials_data):
    data_dir = dials_data("pycbf", pathlib=True)
    object = pycbf.cbf_handle_struct()  # FIXME
    # Expect this in the root pycbf folder
    object.read_file(str(data_dir / "img2cif_packed.cif"), pycbf.MSG_DIGEST)
    object.rewind_datablock()
    print("Found", object.count_datablocks(), "blocks")
    object.select_datablock(0)
    print("Zeroth is named", object.datablock_name())
    object.rewind_category()
    categories = object.count_categories()
    for i in range(categories):
        print("Category:", i, end=" ")
        object.select_category(i)
        category_name = object.category_name()
        print("Name:", category_name, end=" ")
        rows = object.count_rows()
        print("Rows:", rows, end=" ")
        cols = object.count_columns()
        print("Cols:", cols)
        loop = 1
        object.rewind_column()
        while loop != 0:
            column_name = object.column_name()
            print('column name "', column_name, '"', end=" ")
            try:
                object.next_column()
            except Exception:
                break
        print()
        for j in range(rows):
            object.select_row(j)
            object.rewind_column()
            print("row:", j)
            for k in range(cols):
                name = object.column_name()
                print("col:", name, end=" ")
                object.select_column(k)
                typeofvalue = pycbf.cbf2str(object.get_typeofvalue())
                print("type:", typeofvalue)
                if typeofvalue.find("bnry") > -1:
                    print("Found the binary!!", end=" ")
                    s = object.get_integerarray_as_string()
                    print(type(s))
                    print(dir(s))
                    print(len(s))
                else:
                    value = object.get_value()
                    print("Val:", value, i)
        print()
    del object
    #
    print(dir())
    # object.free_handle(handle)
