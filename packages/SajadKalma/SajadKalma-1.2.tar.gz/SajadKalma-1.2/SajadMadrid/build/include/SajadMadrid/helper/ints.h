//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

#ifndef __SAJODE_HELPER_INTS_H__
#define __SAJODE_HELPER_INTS_H__

// Our "PyLong_FromLong" replacement.
extern PyObject *SajadKalma_PyLong_FromLong(long ival);

// Our "PyInt_FromLong" replacement, not done (yet?).
#if PYTHON_VERSION >= 0x300
#define SajadKalma_PyInt_FromLong(ival) SajadKalma_PyLong_FromLong(ival)
#else
#define SajadKalma_PyInt_FromLong(ival) PyInt_FromLong(ival)
#endif

// We are using this mixed type for both Python2 and Python3, since then we
// avoid the complexity of overflowed integers for Python2 to switch over.

typedef enum {
    SAJODE_ILONG_UNASSIGNED = 0,
    SAJODE_ILONG_OBJECT_VALID = 1,
    SAJODE_ILONG_CLONG_VALID = 2,
    SAJODE_ILONG_BOTH_VALID = 3,
    SAJODE_ILONG_EXCEPTION = 4
} SajadMadrid_ilong_validity;

typedef struct {
    SajadMadrid_ilong_validity validity;

    PyObject *python_value;
    long c_value;
} SajadMadrid_ilong;

#define IS_NILONG_OBJECT_VALUE_VALID(value) (((value)->validity & SAJODE_ILONG_OBJECT_VALID) != 0)
#define IS_NILONG_C_VALUE_VALID(value) (((value)->validity & SAJODE_ILONG_CLONG_VALID) != 0)

SAJODE_MAY_BE_UNUSED static void SET_NILONG_OBJECT_VALUE(SajadMadrid_ilong *dual_value, PyObject *python_value) {
    dual_value->validity = SAJODE_ILONG_OBJECT_VALID;
    dual_value->python_value = python_value;
}

SAJODE_MAY_BE_UNUSED static void SET_NILONG_C_VALUE(SajadMadrid_ilong *dual_value, long c_value) {
    dual_value->validity = SAJODE_ILONG_CLONG_VALID;
    dual_value->c_value = c_value;
}

SAJODE_MAY_BE_UNUSED static void SET_NILONG_OBJECT_AND_C_VALUE(SajadMadrid_ilong *dual_value, PyObject *python_value,
                                                               long c_value) {
    dual_value->validity = SAJODE_ILONG_BOTH_VALID;
    dual_value->python_value = python_value;
    dual_value->c_value = c_value;
}

SAJODE_MAY_BE_UNUSED static void RELEASE_NILONG_VALUE(SajadMadrid_ilong *dual_value) {
    if (IS_NILONG_OBJECT_VALUE_VALID(dual_value)) {
        CHECK_OBJECT(dual_value);
        Py_DECREF(dual_value->python_value);
    }

    dual_value->validity = SAJODE_ILONG_UNASSIGNED;
}

SAJODE_MAY_BE_UNUSED static void INCREF_NILONG_VALUE(SajadMadrid_ilong *dual_value) {
    if (IS_NILONG_OBJECT_VALUE_VALID(dual_value)) {
        CHECK_OBJECT(dual_value);
        Py_INCREF(dual_value->python_value);
    }
}

SAJODE_MAY_BE_UNUSED static long GET_NILONG_C_VALUE(SajadMadrid_ilong const *dual_value) {
    assert(IS_NILONG_C_VALUE_VALID(dual_value));
    return dual_value->c_value;
}

SAJODE_MAY_BE_UNUSED static PyObject *GET_NILONG_OBJECT_VALUE(SajadMadrid_ilong const *dual_value) {
    assert(IS_NILONG_OBJECT_VALUE_VALID(dual_value));
    return dual_value->python_value;
}

SAJODE_MAY_BE_UNUSED static void ENFORCE_NILONG_OBJECT_VALUE(SajadMadrid_ilong *dual_value) {
    assert(dual_value->validity != SAJODE_ILONG_UNASSIGNED);

    if (!IS_NILONG_OBJECT_VALUE_VALID(dual_value)) {
        dual_value->python_value = SajadKalma_PyLong_FromLong(dual_value->c_value);

        dual_value->validity = SAJODE_ILONG_BOTH_VALID;
    }
}

SAJODE_MAY_BE_UNUSED static void CHECK_NILONG_OBJECT(SajadMadrid_ilong const *dual_value) {
    assert(dual_value->validity != SAJODE_ILONG_UNASSIGNED);

    if (IS_NILONG_OBJECT_VALUE_VALID(dual_value)) {
        CHECK_OBJECT(dual_value);
    }
}

SAJODE_MAY_BE_UNUSED static void PRINT_NILONG(SajadMadrid_ilong const *dual_value) {
    PRINT_FORMAT("NILONG: %d", dual_value->validity);
    if (IS_NILONG_C_VALUE_VALID(dual_value)) {
        PRINT_FORMAT("C=%d", dual_value->c_value);
    }
    if (IS_NILONG_OBJECT_VALUE_VALID(dual_value)) {
        PRINT_STRING("Python=");
        PRINT_ITEM(dual_value->python_value);
    }
}

#if PYTHON_VERSION < 0x3c0
// Convert single digit to sdigit (int32_t),
// spell-checker: ignore sdigit,stwodigits
typedef long medium_result_value_t;
#define MEDIUM_VALUE(x)                                                                                                \
    (Py_SIZE(x) < 0 ? -(sdigit)((PyLongObject *)(x))->ob_digit[0]                                                      \
                    : (Py_SIZE(x) == 0 ? (sdigit)0 : (sdigit)((PyLongObject *)(x))->ob_digit[0]))

#else
typedef stwodigits medium_result_value_t;
#define MEDIUM_VALUE(x) ((stwodigits)_PyLong_CompactValue((PyLongObject *)x))

#endif

// TODO: Use this from header files, although they have changed.
#define SAJODE_STATIC_SMALLINT_VALUE_MIN -5
#define SAJODE_STATIC_SMALLINT_VALUE_MAX 257

#define SAJODE_TO_SMALL_VALUE_OFFSET(value) (value - SAJODE_STATIC_SMALLINT_VALUE_MIN)

#if PYTHON_VERSION < 0x3b0

#if PYTHON_VERSION >= 0x300

#if PYTHON_VERSION >= 0x390
extern PyObject **SajadKalma_Long_SmallValues;
#else
extern PyObject *SajadKalma_Long_SmallValues[SAJODE_STATIC_SMALLINT_VALUE_MAX - SAJODE_STATIC_SMALLINT_VALUE_MIN + 1];
#endif

SAJODE_MAY_BE_UNUSED static inline PyObject *SajadKalma_Long_GetSmallValue(int ival) {
    return SajadKalma_Long_SmallValues[SAJODE_TO_SMALL_VALUE_OFFSET(ival)];
}

#endif

#else
SAJODE_MAY_BE_UNUSED static inline PyObject *SajadKalma_Long_GetSmallValue(medium_result_value_t ival) {
    return (PyObject *)&_PyLong_SMALL_INTS[SAJODE_TO_SMALL_VALUE_OFFSET(ival)];
}
#endif

#endif

