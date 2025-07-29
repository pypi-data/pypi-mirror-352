# version of pycbf_test1 with write logic added
import os
from pathlib import Path

import pycbf

DATA_DIR = Path(__file__).parent.parent / "data"


def test_4(dials_data, tmp_path):
    data_dir = dials_data("pycbf", pathlib=True)
    object = pycbf.cbf_handle_struct()
    newobject = pycbf.cbf_handle_struct()
    object.read_file(str(data_dir / "img2cif_packed.cif"), pycbf.MSG_DIGEST)
    object.rewind_datablock()
    print("Found", object.count_datablocks(), "blocks")
    object.select_datablock(0)
    print("Zeroth is named", object.datablock_name())
    newobject.force_new_datablock(object.datablock_name())
    object.rewind_category()
    categories = object.count_categories()
    for i in range(categories):
        print("Category:", i, end=" ")
        object.select_category(i)
        category_name = object.category_name()
        print("Name:", category_name, end=" ")
        newobject.new_category(category_name)
        rows = object.count_rows()
        print("Rows:", rows, end=" ")
        cols = object.count_columns()
        print("Cols:", cols)
        loop = 1
        object.rewind_column()
        while loop != 0:
            column_name = object.column_name()
            print('column name "', column_name, '"', end=" ")
            newobject.new_column(column_name)
            try:
                object.next_column()
            except Exception:
                break
        print()
        for j in range(rows):
            object.select_row(j)
            newobject.new_row()
            object.rewind_column()
            print("row:", j)
            for k in range(cols):
                name = object.column_name()
                print("col:", name, end=" ")
                object.select_column(k)
                newobject.select_column(k)
                typeofvalue = pycbf.cbf2str(object.get_typeofvalue())
                print("type:", typeofvalue)
                if typeofvalue.find("bnry") > -1:
                    print("Found the binary!!", end=" ")
                    s = object.get_integerarray_as_string()
                    print(type(s))
                    print(dir(s))
                    print(len(s))
                    (
                        compression,
                        binaryid,
                        elsize,
                        elsigned,
                        elunsigned,
                        elements,
                        minelement,
                        maxelement,
                        byteorder,
                        dimfast,
                        dimmid,
                        dimslow,
                        padding,
                    ) = object.get_integerarrayparameters_wdims_fs()
                    if dimfast == 0:
                        dimfast = 1
                    if dimmid == 0:
                        dimmid = 1
                    if dimslow == 0:
                        dimslow = 1
                    print("compression: ", compression)
                    print("binaryid", binaryid)
                    print("elsize", elsize)
                    print("elsigned", elsigned)
                    print("elunsigned", elunsigned)
                    print("elements", elements)
                    print("minelement", minelement)
                    print("maxelement", maxelement)
                    print("byteorder", byteorder)
                    print("dimfast", dimfast)
                    print("dimmid", dimmid)
                    print("dimslow", dimslow)
                    print("padding", padding)
                    newobject.set_integerarray_wdims_fs(
                        pycbf.CBF_BYTE_OFFSET,
                        binaryid,
                        s,
                        elsize,
                        elsigned,
                        elements,
                        byteorder,
                        dimfast,
                        dimmid,
                        dimslow,
                        padding,
                    )
                else:
                    value = object.get_value()
                    newobject.set_value(value)
                    print("Val:", value, i)
        print()
    del object
    os.chdir(tmp_path)
    newobject.write_widefile(
        "newtest1.cbf",
        pycbf.CBF,
        pycbf.MIME_HEADERS | pycbf.MSG_DIGEST | pycbf.PAD_4K,
        0,
    )
    #
    print(dir())
    # object.free_handle(handle)
