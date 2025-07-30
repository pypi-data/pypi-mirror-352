# من تطوير Sajad @f_g_d_6


""" C code inject related nodes.

These are only coming from special purpose plugins.
"""


def generateInjectCCode(statement, emit, context):
    # No intelligence here, just dumping the code, pylint: disable=unused-argument
    emit(statement.c_code)



