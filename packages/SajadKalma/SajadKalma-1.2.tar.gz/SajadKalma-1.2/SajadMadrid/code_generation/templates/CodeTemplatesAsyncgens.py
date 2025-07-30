# من تطوير Sajad @f_g_d_6


""" Async generator (await/async + yield) related templates.

"""

template_asyncgen_object_maker_template = """\
static PyObject *%(asyncgen_maker_identifier)s(%(asyncgen_creation_args)s);
"""

template_asyncgen_object_body = """
#if %(has_heap_declaration)s
struct %(function_identifier)s_locals {
%(function_local_types)s
};
#endif

static PyObject *%(function_identifier)s_context(PyThreadState *tstate, struct SajadKalma_AsyncgenObject *asyncgen, PyObject *yield_return_value) {
    CHECK_OBJECT(asyncgen);
    assert(SajadKalma_Asyncgen_Check((PyObject *)asyncgen));
    CHECK_OBJECT_X(yield_return_value);

#if %(has_heap_declaration)s
    // Heap access.
%(heap_declaration)s
#endif

    // Dispatch to yield based on return label index:
%(function_dispatch)s

    // Local variable initialization
%(function_var_inits)s

    // Actual asyncgen body.
%(function_body)s

%(asyncgen_exit)s
}

static PyObject *%(asyncgen_maker_identifier)s(%(asyncgen_creation_args)s) {
    return SajadKalma_Asyncgen_New(
        %(function_identifier)s_context,
        %(asyncgen_module)s,
        %(asyncgen_name_obj)s,
        %(asyncgen_qualname_obj)s,
        %(code_identifier)s,
        %(closure_name)s,
        %(closure_count)d,
#if %(has_heap_declaration)s
        sizeof(struct %(function_identifier)s_locals)
#else
        0
#endif
    );
}
"""

template_make_asyncgen = """\
%(closure_copy)s
%(to_name)s = %(asyncgen_maker_identifier)s(%(args)s);
"""

# TODO: For functions SAJODE_CANNOT_GET_HERE is injected by composing code.
template_asyncgen_exception_exit = """\
    SAJODE_CANNOT_GET_HERE("return must be present");

    function_exception_exit:
%(function_cleanup)s
    CHECK_EXCEPTION_STATE(&%(exception_state_name)s);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &%(exception_state_name)s);
    return NULL;
"""

template_asyncgen_noexception_exit = """\
    SAJODE_CANNOT_GET_HERE("return must be present");

%(function_cleanup)s
    return NULL;
"""

template_asyncgen_return_exit = """\
    function_return_exit:;

    return NULL;
"""


from . import TemplateDebugWrapper  # isort:skip

TemplateDebugWrapper.checkDebug(globals())


