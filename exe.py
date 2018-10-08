import cx_Freeze

executables = [cx_Freeze.Executable("mainfile.py")]

cx_Freeze.setup(
    name="Jeffventures",
    options={"build_exe": {"packages":["pygame","sys","random","math","time","datetime"],}},
    executables = executables

    )
