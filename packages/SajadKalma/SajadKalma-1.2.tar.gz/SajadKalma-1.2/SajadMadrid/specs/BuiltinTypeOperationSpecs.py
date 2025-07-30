# من تطوير Sajad @f_g_d_6


"""Type operation specs. """

from .BuiltinParameterSpecs import BuiltinMethodParameterSpecBase


class TypeMethodSpec(BuiltinMethodParameterSpecBase):
    """Method spec of exactly the `type` built-in value/type."""

    __slots__ = ()

    method_prefix = "type"


type___prepare___spec = TypeMethodSpec(
    name="__prepare__", list_star_arg="args", dict_star_arg="kwargs"
)


