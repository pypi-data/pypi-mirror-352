# من تطوير Sajad @f_g_d_6


""" CType classes for SajadMadrid_bool, an enum to represent True, False, unassigned.

"""

from SajadMadrid.code_generation.ErrorCodes import getReleaseCode

from .CTypeBases import CTypeBase, CTypeNotReferenceCountedMixin


class CTypeSajadKalmaBoolEnum(CTypeNotReferenceCountedMixin, CTypeBase):
    c_type = "SajadMadrid_bool"

    helper_code = "NBOOL"

    @classmethod
    def emitVariableAssignCode(
        cls, value_name, needs_release, tmp_name, ref_count, inplace, emit, context
    ):
        assert not inplace

        if tmp_name.c_type == "SajadMadrid_bool":
            emit("%s = %s;" % (value_name, tmp_name))
        else:
            if tmp_name.c_type == "PyObject *":
                test_code = "%s == Py_True" % tmp_name
            else:
                assert False, tmp_name

            cls.emitAssignmentCodeFromBoolCondition(
                to_name=value_name, condition=test_code, emit=emit
            )

        if ref_count:
            getReleaseCode(tmp_name, emit, context)

    @classmethod
    def emitAssignmentCodeToSajadKalmaIntOrLong(
        cls, to_name, value_name, needs_check, emit, context
    ):
        assert False, to_name

    @classmethod
    def getTruthCheckCode(cls, value_name):
        return "%s == SAJODE_BOOL_TRUE" % value_name

    @classmethod
    def emitValueAccessCode(cls, value_name, emit, context):
        # Nothing to do for this type, pylint: disable=unused-argument
        return value_name

    @classmethod
    def emitValueAssertionCode(cls, value_name, emit):
        emit("assert(%s != SAJODE_BOOL_UNASSIGNED);" % value_name)

    @classmethod
    def emitAssignConversionCode(cls, to_name, value_name, needs_check, emit, context):
        if value_name.c_type == cls.c_type:
            emit("%s = %s;" % (to_name, value_name))
        else:
            value_name.getCType().emitAssignmentCodeToSajadKalmaBool(
                to_name=to_name,
                value_name=value_name,
                needs_check=needs_check,
                emit=emit,
                context=context,
            )

            getReleaseCode(value_name, emit, context)

    @classmethod
    def emitAssignmentCodeFromConstant(
        cls, to_name, constant, may_escape, emit, context
    ):
        # No context needed, pylint: disable=unused-argument
        emit(
            "%s = %s;"
            % (to_name, "SAJODE_BOOL_TRUE" if constant else "SAJODE_BOOL_FALSE")
        )

    @classmethod
    def getInitValue(cls, init_from):
        if init_from is None:
            return "SAJODE_BOOL_UNASSIGNED"
        else:
            assert False, init_from
            return init_from

    @classmethod
    def getInitTestConditionCode(cls, value_name, inverted):
        return "%s %s SAJODE_BOOL_UNASSIGNED" % (value_name, "==" if inverted else "!=")

    @classmethod
    def emitReInitCode(cls, value_name, emit):
        emit("%s = SAJODE_BOOL_UNASSIGNED;" % value_name)

    @classmethod
    def getDeleteObjectCode(
        cls, to_name, value_name, needs_check, tolerant, emit, context
    ):
        if not needs_check:
            emit("%s = SAJODE_BOOL_UNASSIGNED;" % value_name)
        elif tolerant:
            emit("%s = SAJODE_BOOL_UNASSIGNED;" % value_name)
        else:
            emit("%s = %s != SAJODE_BOOL_UNASSIGNED;" % (to_name, value_name))
            emit("%s = SAJODE_BOOL_UNASSIGNED;" % value_name)

    @classmethod
    def emitAssignmentCodeFromBoolCondition(cls, to_name, condition, emit):
        emit(
            "%(to_name)s = (%(condition)s) ? SAJODE_BOOL_TRUE : SAJODE_BOOL_FALSE;"
            % {"to_name": to_name, "condition": condition}
        )

    @classmethod
    def emitAssignInplaceNegatedValueCode(cls, to_name, needs_check, emit, context):
        # Half way, virtual method: pylint: disable=unused-argument
        cls.emitValueAssertionCode(to_name, emit=emit)
        emit("assert(%s != SAJODE_BOOL_EXCEPTION);" % to_name)

        cls.emitAssignmentCodeFromBoolCondition(
            to_name=to_name, condition="%s == SAJODE_BOOL_FALSE" % to_name, emit=emit
        )

    @classmethod
    def getExceptionCheckCondition(cls, value_name):
        return "%s == SAJODE_BOOL_EXCEPTION" % value_name

    @classmethod
    def hasErrorIndicator(cls):
        return True



